import cv2, numpy as np, sys
def masque_blanc(t, excl=(), seuil=165):
    im = cv2.imread(t if t.startswith('/') else f'../../refs/pew/t_{t}.png'); im = cv2.resize(im, (960, 540))
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    m = ((g > seuil) & (hsv[:, :, 1] < 60)).astype(np.uint8)
    for poly in excl:
        cv2.fillPoly(m, [np.array(poly, np.int32)], 0)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return m
if __name__ == "__main__":
    t = sys.argv[1]; excl = eval(sys.argv[2]) if len(sys.argv) > 2 else ()
    m = masque_blanc(t, excl)
    cv2.imwrite(f'masque_{t}.png', m * 255)
