"""Géométrie exacte des frappes TSB (M1-M4, WallComboPlayer).
Chargeur local (charge.py) : ignore les Poses de poids 0 (conteneurs) que
geo_pose.mondes_rbxm prend pour des clés (bug : torse ramené à l'identité
sur M4 f18/20/24/28 et WallComboPlayer)."""
import json, sys
import numpy as np
import charge as K, geo_pose as G

ARM = {'RA': 'Right Arm', 'LA': 'Left Arm', 'RL': 'Right Leg', 'LL': 'Left Leg'}
SH = {'RA': np.array([1.0, 0.5, 0]), 'LA': np.array([-1.0, 0.5, 0]),
      'RL': np.array([0.5, -1.0, 0]), 'LL': np.array([-0.5, -1.0, 0])}

# (id, anim, membre, fenêtre de recherche du coup [a,b], début de la fenêtre d'armé, type)
FRAPPES = [
    ('M1', 'M1', 'LA', (6, 12), 0, 'poing', 9),
    ('M2', 'M2', 'RA', (7, 13), 0, 'poing'),
    ('M3', 'M3', 'LA', (6, 11), 0, 'poing'),
    ('M4', 'M4', 'RL', (10, 16), 0, 'pied'),
    ('WC1', 'WallComboPlayer', 'LA', (238, 246), 214, 'marteau'),
    ('WC2', 'WallComboPlayer', 'LA', (270, 280), 246, 'revers'),
    ('WC3', 'WallComboPlayer', 'RA', (350, 358), 300, 'balayage'),
]

cache = {}
def mondes(nom):
    if nom not in cache:
        cache[nom] = K.mondes(nom)
    return cache[nom]

def tip(w, k):
    return G.bout(w, ARM[k])

def pivot(w, k):
    R, p = w['Torso']
    return p + R @ SH[k]

def vitesse(mw, k):
    B = np.array([tip(w, k) for _, w in mw])
    return np.r_[0.0, np.linalg.norm(np.diff(B, axis=0), axis=1) * 60]

def repere(avant):
    return G.repere(avant)

def loc(v, avant):
    f, r = repere(avant)
    return np.array([v @ f, v @ r, v[1]])

C0 = {'RA': np.array([1., 0.5, 0]), 'LA': np.array([-1., 0.5, 0]), 'RL': np.array([0.5, -1., 0]), 'LL': np.array([-0.5, -1., 0])}
C1 = {'RA': np.array([-0.5, 0.5, 0]), 'LA': np.array([0.5, 0.5, 0]), 'RL': np.array([0., 1., 0]), 'LL': np.array([0., 1., 0])}

def transl(w, k):
    """Translation du membre hors de son emboîtement, axes du torse (droite, haut, avant)."""
    Rt, pt = w['Torso']; Ra, pa = w[ARM[k]]
    t = Rt.T @ ((pa + Ra @ C1[k]) - (pt + Rt @ C0[k]))
    return np.array([t[0], t[1], -t[2]])

def decompose(wa, wc, k, avant):
    """Déplacement du bout de a à c = torse (translation + rotation, membre figé dans ses axes) + rotation du membre + translation du membre."""
    Rta, pta = wa['Torso']; Rtc, ptc = wc['Torso']
    def parts(w):
        Rt, pt = w['Torso']; Ra, pa = w[ARM[k]]
        piv = pa + Ra @ C1[k]
        tr = Rt.T @ (piv - (pt + Rt @ C0[k]))
        rot = Rt.T @ (G.bout(w, ARM[k]) - piv)
        return tr, rot
    tra, rota = parts(wa); trc, rotc = parts(wc)
    tipLa = C0[k] + tra + rota
    d = {'torse_translation': ptc - pta,
         'torse_rotation': (Rtc - Rta) @ tipLa,
         'membre_rotation': Rtc @ (rotc - rota),
         'membre_translation': Rtc @ (trc - tra)}
    tot = G.bout(wc, ARM[k]) - G.bout(wa, ARM[k])
    assert np.allclose(sum(d.values()), tot, atol=1e-6)
    return {n: [round(float(x), 2) for x in loc(v, avant)] for n, v in d.items()} | {'total': [round(float(x), 2) for x in loc(tot, avant)]}

def analyse(fid, nom, k, win, w0, typ, contact_force=None):
    mw = mondes(nom)
    v = vitesse(mw, k)
    a, b = win
    pic = a + int(np.argmax(v[a:b + 1]))
    vmax = v[pic]
    # fin de la phase rapide : dernière image >= 50 % du pic, sans trou
    c = pic
    while c + 1 <= b and v[c + 1] >= 0.5 * vmax:
        c += 1
    # début de la phase rapide
    s = pic
    while s - 1 >= w0 and v[s - 1] >= 0.5 * vmax:
        s -= 1
    depart = s - 1          # dernière image AVANT le saut de vitesse = pose armée juste avant la détente
    contact = contact_force if contact_force is not None else c
    wc = mondes(nom)[contact][1]
    tc = wc['Torso'][1]
    d = tip(wc, k) - tc; d[1] = 0
    avant = tuple(d / np.linalg.norm(d))
    f, r = repere(avant)
    # armé max : poing le plus en arrière le long du coup, dans [w0, depart]
    proj = [ (tip(w, k) - mondes(nom)[contact][1]['Torso'][1]) @ f for _, w in mw[w0:depart + 1]]
    armé = w0 + int(np.argmin(proj))
    D = {i: G.descripteurs(mw[i][1], avant) for i in range(len(mw))}
    lac = np.array([D[i]['buste']['lacet'] for i in range(len(mw))])
    # contre-rotation max : bras droit -> lacet le plus négatif ; bras gauche -> le plus positif
    seg = lac[w0:depart + 1]
    if k in ('RA', 'RL'):
        tordu = w0 + int(np.argmin(seg))
    else:
        tordu = w0 + int(np.argmax(seg))
    # tenue : images de [armé, depart] où le poing va à < 4 studs/s
    tenue = [i for i in range(armé + 1, depart + 1) if v[i] < 4.0]
    # trajet du poing de l'armé au contact (monde, repère du coup, origine = torse à l'armé)
    o = mw[armé][1]['Torso'][1]
    P = np.array([loc(tip(mw[i][1], k) - o, avant) for i in range(armé, contact + 1)])
    corde = np.linalg.norm(P[-1] - P[0]); long_ = np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1))
    u = (P[-1] - P[0]) / max(corde, 1e-9)
    dev = [np.linalg.norm((p - P[0]) - ((p - P[0]) @ u) * u) for p in P]
    # angle balayé autour du centre du torse (horizontal)
    azs = []
    for i in range(armé, contact + 1):
        w = mw[i][1]; q = loc(tip(w, k) - w['Torso'][1], avant)
        azs.append(np.degrees(np.arctan2(q[1], q[0])))
    # décomposition : torse (bras figé dans les axes du torse) vs bras
    ww = mw[armé][1]; Rw = ww['Torso'][0]
    vloc = Rw.T @ (tip(ww, k) - pivot(ww, k))
    Rc = wc['Torso'][0]
    fA = pivot(wc, k) + Rc @ vloc
    dep_tot = loc(tip(wc, k) - tip(ww, k), avant)
    dep_torse = loc(fA - tip(ww, k), avant)
    dep_bras = loc(tip(wc, k) - fA, avant)
    # longueur pivot->bout constante ? (contrôle)
    lp = [np.linalg.norm(tip(mw[i][1], k) - pivot(mw[i][1], k)) for i in (armé, contact)]
    def membre(dd):
        if k in ('RA', 'LA'):
            return dd['bras'][k]
        return None
    res = {
        'id': fid, 'anim': nom, 'membre': k, 'type': typ,
        'avant_vecteur': [round(x, 3) for x in avant],
        'avant_az_deg_depuis_-Z_vers_+X': round(float(np.degrees(np.arctan2(avant[0], -avant[2]))), 1),
        'images': {'arme_max_poing_le_plus_recule': armé, 'contre_rotation_max_buste': tordu,
                   'depart_detente': depart, 'pic_vitesse': pic, 'contact': contact},
        'vitesse_pic_studs_s': round(float(vmax), 1),
        'vitesses_depart_a_contact': [round(float(x), 1) for x in v[depart:contact + 2]],
        'derive_moyenne_arme_a_depart_studs_s': round(float(np.mean(v[armé + 1:depart + 1])) if depart > armé else 0.0, 1),
        'tenue_images_<4studs/s': tenue,
        'durees_images_60': {'arme_a_depart (derive lente)': depart - armé, 'tenue': len(tenue),
                             'depart_a_contact': contact - depart, 'arme_a_contact': contact - armé},
        'trajet': {'corde': round(float(corde), 2), 'longueur': round(float(long_), 2),
                   'rectitude_corde_sur_longueur': round(float(corde / max(long_, 1e-9)), 2),
                   'ecart_max_a_la_corde': round(float(max(dev)), 2),
                   'deplacement_poing_(avant,droite,haut)': [round(float(x), 2) for x in dep_tot],
                   'az_poing_autour_du_torse_deg': [round(float(x), 0) for x in azs],
                   'delta_lacet_buste': round(float(D[contact]['buste']['lacet'] - D[armé]['buste']['lacet']), 1)},
        'desc_arme': D[armé], 'desc_contre_rotation_max': D[tordu], 'desc_depart': D[depart], 'desc_contact': D[contact],
    }
    if k in ('RA', 'LA'):
        res['trajet']['delta_az_bras_torse'] = round(float(D[contact]['bras'][k]['torse'][0] - D[armé]['bras'][k]['torse'][0]), 1)
        res['trajet']['delta_el_bras_torse'] = round(float(D[contact]['bras'][k]['torse'][1] - D[armé]['bras'][k]['torse'][1]), 1)
        res['trajet']['delta_az_bras_coup'] = round(float(D[contact]['bras'][k]['coup'][0] - D[armé]['bras'][k]['coup'][0]), 1)
        res['trajet']['delta_az_depart_contact_torse'] = round(float(D[contact]['bras'][k]['torse'][0] - D[depart]['bras'][k]['torse'][0]), 1)
        res['trajet']['delta_lacet_depart_contact'] = round(float(D[contact]['buste']['lacet'] - D[depart]['buste']['lacet']), 1)
    res['translation_membre_(droite,haut,avant)_axes_torse'] = {n: [round(float(x), 2) for x in transl(mw[i][1], k)] for n, i in (('arme', armé), ('depart', depart), ('contact', contact))}
    autre = {'RA': 'LA', 'LA': 'RA', 'RL': 'LL', 'LL': 'RL'}[k]
    res['translation_autre_bras'] = None
    if k in ('RA', 'LA'):
        res['translation_autre_bras'] = {n: [round(float(x), 2) for x in transl(mw[i][1], autre)] for n, i in (('arme', armé), ('depart', depart), ('contact', contact))}
    res['decomposition_arme_a_contact_(avant,droite,haut)'] = decompose(mw[armé][1], wc, k, avant)
    res['decomposition_depart_a_contact_(avant,droite,haut)'] = decompose(mw[depart][1], wc, k, avant)
    res['decomposition_arme_a_depart_(avant,droite,haut)'] = decompose(mw[armé][1], mw[depart][1], k, avant)
    res['resume'] = {n: G.resume(D[i]) for n, i in (('arme', armé), ('depart', depart), ('contact', contact))}
    return res

if __name__ == '__main__':
    out = []
    for fr in FRAPPES:
        r = analyse(*fr)
        out.append(r)
        print('=====', r['id'], r['anim'], r['membre'], r['type'], 'avant az', r['avant_az_deg_depuis_-Z_vers_+X'])
        print('  images', r['images'], 'pic', r['vitesse_pic_studs_s'], 'vit', r['vitesses_depart_a_contact'])
        print('  durees', r['durees_images_60'], 'derive', r['derive_moyenne_arme_a_depart_studs_s'], 'tenue', r['tenue_images_<4studs/s'])
        t = r['trajet']
        print('  trajet', {x: t[x] for x in t if x != 'az_poing_autour_du_torse_deg'})
        print('  az poing autour torse', t['az_poing_autour_du_torse_deg'])
        for n, s in r['resume'].items():
            print('  ', n, s)
        print('   translation membre', r['translation_membre_(droite,haut,avant)_axes_torse'], 'autre bras', r['translation_autre_bras'])
        for x in ('arme_a_contact', 'arme_a_depart', 'depart_a_contact'):
            print('   decomp', x, r['decomposition_%s_(avant,droite,haut)' % x])
        print('   pieds contact', r['desc_contact']['pieds'], 'tete', r['desc_contact'].get('tete'))
    json.dump(out, open('frappes_tsb.json', 'w'), ensure_ascii=False, indent=1)
