import sys, pickle, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
M=pickle.load(open("mondes.pkl","rb"))
n=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(",")]; out=sys.argv[3]
cams=[(0,10),(90,10),(45,30)] if len(sys.argv)<5 else [tuple(map(float,c.split(":"))) for c in sys.argv[4].split(",")]
ws=[w for t,w in M[n]]
T=(200,220)
sheet=Image.new("RGB",(T[0]*len(frames),T[1]*len(cams)),(0,0,0))
for j,(az,el) in enumerate(cams):
    for i,f in enumerate(frames):
        cam=G.camera_orbite((0,2.6,0),az,el,11,50)
        im=G.rendre([ws[f]],cam,T,f"{n} f{f} az{az:.0f}")
        sheet.paste(im,(i*T[0],j*T[1]))
sheet.save(out)
