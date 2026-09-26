exec(open('run_frame.py').read())
import sys, json
LAB["Cap"]=3
def planche_x(T, cands, nom):
    tiles=[]
    ref=Image.open(REFD+f'sp2/t_{T}.png').convert('RGB').resize((640,360))
    for lab,x in cands:
        w=monde_complet(vers_q(x)); im=rendu(w,vers_cam3(x),(0,x['hanche'],0),(640,360),mode='rgb')
        t=Image.blend(ref,im,0.5).resize((427,240)); ImageDraw.Draw(t).text((4,4),lab,fill=(255,255,0)); tiles.append(t)
    W=Image.new('RGB',(427*3,240*((len(tiles)+2)//3)))
    for i,t in enumerate(tiles): W.paste(t,((i%3)*427,(i//3)*240))
    W.save(OUT+f'{T}_{nom}.png'); print(OUT+f'{T}_{nom}.png')
B=dict(az=0,el=40,dist=3.2,dx=0,dy=0,hanche=2.2,pen=55,cote=0,RAaz=-165,RAel=5,LAaz=-60,LAel=0,RLaz=20,RLel=-40,LLaz=-20,LLel=-30,tl=0,tt=0,cape=5,fov=70)
