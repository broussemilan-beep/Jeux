import sys; sys.path.insert(0, '.')
from joint import *
from PIL import Image, ImageDraw
def zoom_compare(p, camargs, ref, box, out, pitch, W, H, extra_lines=True):
    w = G.pose(p)
    cam = cam3(w, *camargs[:3], pitch, camargs[3])
    im = G.rendre([w], cam, (W, H), '')
    r = Image.open(REFS[ref]).convert('RGB').resize((W, H))
    # outline render parts onto ref
    P = projector(cam, W, H)
    ov = r.copy(); d = ImageDraw.Draw(ov)
    cols = {'Torso': (255, 60, 60), 'Right Arm': (60, 255, 60), 'Left Arm': (60, 140, 255), 'Head': (255, 255, 255),
            'Right Leg': (255, 220, 0), 'Left Leg': (255, 220, 0)}
    for part, col in cols.items():
        R, c = w[part]; h = np.array(M.SIZES[part]) / 2
        cs = {(a, b, cc): P(c + R @ (np.array([a, b, cc]) * h)) for a in (-1, 1) for b in (-1, 1) for cc in (-1, 1)}
        for (a, b, cc), q in cs.items():
            for k in range(3):
                n = [a, b, cc]; n[k] = -n[k]; n = tuple(n)
                if n > (a, b, cc):
                    d.line([tuple(q), tuple(cs[n])], fill=col, width=3)
        if part in ('Right Arm', 'Left Arm'):   # hand-end face in thick
            fc = [cs[(a, -1, cc)] for a, cc in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            d.polygon([tuple(x) for x in fc], outline=(255, 0, 255))
    x0, y0, x1, y1 = box
    A = im.crop(box); B = ov.crop(box)
    S = Image.new('RGB', (A.width * 2 + 6, A.height)); S.paste(A, (0, 0)); S.paste(B, (A.width + 6, 0))
    S.save(out)
    return w, cam
