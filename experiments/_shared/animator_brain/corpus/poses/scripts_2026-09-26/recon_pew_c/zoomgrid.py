import sys
from PIL import Image, ImageDraw
t, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6])
s = float(sys.argv[6]) if len(sys.argv) > 6 else 2
src = sys.argv[7] if len(sys.argv) > 7 else f'../../refs/pew/t_{t}.png'
im = Image.open(src).convert('RGB').resize((960, 540)).crop((x0, y0, x1, y1))
im = im.resize((int((x1-x0)*s), int((y1-y0)*s)))
d = ImageDraw.Draw(im)
for x in range((x0//20+1)*20, x1, 20):
    X = (x-x0)*s; d.line([(X,0),(X,im.height)], fill=(255,0,0) if x%100==0 else (110,0,0))
    if x % 100 == 0 or x % 50 == 0: d.text((X+2,2), str(x), fill='yellow')
for y in range((y0//20+1)*20, y1, 20):
    Y = (y-y0)*s; d.line([(0,Y),(im.width,Y)], fill=(255,0,0) if y%100==0 else (110,0,0))
    if y % 50 == 0: d.text((2,Y+2), str(y), fill='yellow')
im.save(f'zg_{t}.png')
