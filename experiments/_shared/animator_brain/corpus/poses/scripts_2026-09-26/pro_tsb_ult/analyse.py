import sys, json, pickle, numpy as np
sys.path.insert(0,'.'); sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
from epaule import decalage, local_torse
D=pickle.load(open('mondes_corriges.pkl','rb'))
PART={'RA':'Right Arm','LA':'Left Arm'}
COUPS=[
 dict(id='U1_direct_droit_lent', anim='Ultimate1', bras='RA', armé=432, tenue=(290,432), départ=434, contact=496, apres=(498,556), extra={'geste_prealable':(190,290)}),
 dict(id='U2_revers_gauche', anim='Ultimate2', bras='LA', armé=93, tenue=(91,94), départ=95, contact=109, apres=(119,171), extra={'passage_devant':101,'arret':119}),
 dict(id='CR_vrille_deux_mains', anim='Collateral Ruin', bras='RA', armé=48, tenue=(48,61), départ=61, contact=77, apres=(97,128), extra={'poing_le_plus_en_arriere':67,'claquage':(73,77),'fin_vrille':96}),
 dict(id='SB_bombe_bras_en_X', anim='Stoic Bomb', bras='RA', armé=150, tenue=(57,250), départ=207, contact=216, apres=(225,250), extra={'ouverture_bras':(252,283)}),
 dict(id='SS_balayage_vrille', anim='Swift Sweep', bras='RA', armé=6, tenue=None, départ=7, contact=30, apres=None, extra={'coup_de_pied_2':52}),
]
def avant_de(w, part):
    v=G.bout(w,part)-w['Torso'][1]; v[1]=0; n=np.linalg.norm(v); return tuple(np.round(v/n,4))
def vit_rel(fr,i,part):
    a=G.bout(fr[i][1],part)-fr[i][1]['Torso'][1]; b=G.bout(fr[i-1][1],part)-fr[i-1][1]['Torso'][1]
    return float(np.linalg.norm(a-b)*60)
def enrichir(d, w, bras):
    d=json.loads(json.dumps(d))
    d['pivot_epaule_decale_torse(dr,ht,av)']={k:list(map(float,decalage(w,PART[k]))) for k in PART}
    d['poing_axes_torse(dr,ht,av)']={k:list(map(float,local_torse(w,G.bout(w,PART[k])))) for k in PART}
    d['haut_du_bras_axes_torse(dr,ht,av)']={k:list(map(float,local_torse(w,G.haut(w,PART[k])))) for k in PART}
    return d
res={}
for c in COUPS:
    fr=D[c['anim']]; part=PART[c['bras']]
    wc=fr[c['contact']][1]
    av=(0.0,0.0,-1.0) if c['id'] in ('SB_bombe_bras_en_X','SS_balayage_vrille','U2_revers_gauche') else avant_de(wc,part)
    f_,r_=G.repere(av)
    da=G.descripteurs(fr[c['armé']][1],av); dc=G.descripteurs(wc,av)
    # trajet du poing armé -> contact dans le repère du coup (relatif au centre du torse)
    P=[]
    for i in range(c['armé'],c['contact']+1):
        w=fr[i][1]; v=G.bout(w,part)-w['Torso'][1]; P.append([v@f_, v@r_, v[1]])
    P=np.array(P); corde=P[-1]-P[0]; L=np.sum(np.linalg.norm(np.diff(P,axis=0),axis=1)); Lc=np.linalg.norm(corde)
    u=corde/max(Lc,1e-9); dev=np.max(np.linalg.norm((P-P[0])-np.outer((P-P[0])@u,u),axis=1))
    azs=np.degrees(np.unwrap(np.arctan2(P[:,1],P[:,0])))
    lac=np.degrees(np.unwrap(np.radians([G.descripteurs(fr[i][1],av)['buste']['lacet'] for i in range(c['armé'],c['contact']+1)])))
    arm_az=np.degrees(np.unwrap(np.radians([G.descripteurs(fr[i][1],av)['bras'][c['bras']]['torse'][0] for i in range(c['armé'],c['contact']+1)])))
    arm_el=[G.descripteurs(fr[i][1],av)['bras'][c['bras']]['torse'][1] for i in range(c['armé'],c['contact']+1)]
    vs=[vit_rel(fr,i,part) for i in range(c['armé']+1,c['contact']+1)]
    k=int(np.argmax(vs))+c['armé']+1
    t={'fps':60,'arme':c['armé'],'tenue':c['tenue'],'duree_tenue_f':(c['tenue'][1]-c['tenue'][0]) if c['tenue'] else 0,
       'depart':c['départ'],'contact':c['contact'],'depart_a_contact_f':c['contact']-c['départ'],
       'vitesse_max_rel_studs_s':round(max(vs),1),'image_vitesse_max':k,'apres':c['apres'],**c['extra']}
    traj={'corde':[round(float(x),2) for x in corde],'longueur_corde':round(float(Lc),2),'longueur_trajet':round(float(L),2),
          'rectitude(corde/trajet)':round(float(Lc/L),2),'ecart_max_a_la_corde':round(float(dev),2),
          'balayage_horizontal_du_poing_deg':round(float(azs[-1]-azs[0]),1),'delta_lacet_buste_deg':round(float(lac[-1]-lac[0]),1),
          'delta_az_bras_torse_deg':round(float(arm_az[-1]-arm_az[0]),1),'delta_el_bras_torse_deg':round(float(arm_el[-1]-arm_el[0]),1),
          'delta_hauteur_poing':round(float(P[-1,2]-P[0,2]),2),
          'az_bras_torse_min_max':[round(float(arm_az.min()),1),round(float(arm_az.max()),1)],
          'lacet_min_max':[round(float(lac.min()),1),round(float(lac.max()),1)],
          'poing_echantillons(av,dr,ht)':[[round(float(x),2) for x in P[j]] for j in np.linspace(0,len(P)-1,min(9,len(P))).astype(int)]}
    res[c['id']]={'anim':c['anim'],'bras':c['bras'],'avant':av,'temps':t,'trajet':traj,
                 'descripteurs_arme':enrichir(da,fr[c['armé']][1],c['bras']),'descripteurs_contact':enrichir(dc,wc,c['bras'])}
    print('=====',c['id'],'avant',av); print(' ARME   ',G.resume(da)); print(' CONTACT',G.resume(dc)); print(' temps',t); print(' trajet',{k:v for k,v in traj.items() if k!='poing_echantillons(av,dr,ht)'})
    print(' poing', traj['poing_echantillons(av,dr,ht)'])
    print(' pivots arme', res[c['id']]['descripteurs_arme']['pivot_epaule_decale_torse(dr,ht,av)'], 'contact', res[c['id']]['descripteurs_contact']['pivot_epaule_decale_torse(dr,ht,av)'])
    print(' pieds arme', da['pieds'], 'contact', dc['pieds'])
json.dump(res,open('coups.json','w'),ensure_ascii=False,indent=1)
