import sys
from PIL import Image, ImageDraw
import os
R=os.environ.get('REFPAT','/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/refs/sp2/t_%s.png')
def grille(t, out, k=2, box=None):
    im=Image.open(R%t).convert('RGB')
    if box: im=im.crop(box)
    ox,oy=(box[0],box[1]) if box else (0,0)
    im=im.resize((im.width*k,im.height*k))
    d=ImageDraw.Draw(im)
    for x in range(0,640,20):
        if x<ox or x>ox+im.width//k: continue
        X=(x-ox)*k
        d.line([(X,0),(X,im.height)],fill=(0,255,255) if x%100==0 else (0,120,160),width=1)
        if x%40==0: d.text((X+2,2),str(x),fill=(255,255,0))
    for y in range(0,360,20):
        if y<oy or y>oy+im.height//k: continue
        Y=(y-oy)*k
        d.line([(0,Y),(im.width,Y)],fill=(0,255,255) if y%100==0 else (0,120,160),width=1)
        if y%40==0: d.text((2,Y+2),str(y),fill=(255,255,0))
    im.save(out)
if __name__=='__main__':
    t=sys.argv[1]; box=tuple(map(int,sys.argv[2].split(','))) if len(sys.argv)>2 else None
    k=int(sys.argv[3]) if len(sys.argv)>3 else 2
    grille(t,'g_%s.png'%t.replace('.',''),k,box)
