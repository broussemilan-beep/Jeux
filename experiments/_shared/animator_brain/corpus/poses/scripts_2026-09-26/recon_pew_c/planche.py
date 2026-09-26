from PIL import Image, ImageDraw
import sys, glob
fs = sorted(glob.glob('f30/f_*.png'))
a, b = int(sys.argv[1]), int(sys.argv[2])
sel = fs[a-1:b]
W,H = 640,360; cols=3
rows=(len(sel)+cols-1)//cols
out = Image.new('RGB',(W*cols,H*rows),'black')
for i,f in enumerate(sel):
    im=Image.open(f).convert('RGB')
    k=a+i
    d=ImageDraw.Draw(im); d.rectangle([0,0,110,22],fill='black'); d.text((4,4),f"f{k:03d} t={4.3+(k-1)/30:.3f}",fill='yellow')
    out.paste(im,((i%cols)*W,(i//cols)*H))
out.save(sys.argv[3])
