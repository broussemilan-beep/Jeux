from PIL import Image, ImageDraw
import sys
def grid(src, box, out, step=50, lab=100, scale=1.0):
    im = Image.open(src).convert("RGB")
    x0,y0,x1,y1 = box
    c = im.crop(box)
    if scale != 1.0:
        c = c.resize((int(c.width*scale), int(c.height*scale)))
    d = ImageDraw.Draw(c)
    s = scale
    for x in range(x0 - x0%step + step, x1, step):
        X = (x-x0)*s
        d.line([(X,0),(X,c.height)], fill=(255,0,0) if x%lab==0 else (120,0,0), width=1)
        if x % lab == 0: d.text((X+2,2), str(x), fill=(255,255,0))
    for y in range(y0 - y0%step + step, y1, step):
        Y = (y-y0)*s
        d.line([(0,Y),(c.width,Y)], fill=(255,0,0) if y%lab==0 else (120,0,0), width=1)
        if y % lab == 0: d.text((2,Y+2), str(y), fill=(255,255,0))
    c.save(out)
if __name__ == "__main__":
    grid(sys.argv[1], tuple(map(int, sys.argv[2].split(','))), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), float(sys.argv[6]))
