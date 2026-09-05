"""
Combo de 3 coups (jab gauche -> cross droit -> hook gauche) sur un
mannequin, deux rigs R6 independants (meme principe que
r6_directional_punch : un attaquant + un mannequin, chronologie commune).

Demande utilisateur explicite : "Fais une nvl animation de combo de hit
avec VFX texturing inspire toi des refs que je t'ai envoye sois encore
plus fluide je veux pas du saccade du chelou et enfin fais Camera de
loin qui montre la scene en entierete."

Consequence directe sur la chronologie : contrairement a
r6_directional_punch (une longue charge de ~1,25s avant UN coup), un
combo n'a PAS de temps mort entre les coups -- chaque retour de bras
DEVIENT l'amorce du coup suivant (le buste qui se re-tord dans l'autre
sens pendant que la main revient sert de windup au coup suivant), pour
eviter tout arret qui lirait comme "saccade". Chaque coup individuel
reutilise la lecon apprise sur r6_directional_punch (retour utilisateur
+ recherche) : la fenetre HIP_DRIVE_T -> IMPACT_T (chaine cinetique ->
lacher) est un vrai SNAP D'UNE SEULE FRAME (1/30s, le OUT_HZ de
dump_scene_data.py) -- jamais 3-5 frames intermediaires (= effet "pale
de moulin" sur un bras rigide sans coude, cause identifiee la derniere
fois).

Meme convention d'axes que r6_directional_punch (verifiee, pas
resupposee) :
  - Torso/Head/jambes : X positif = penche/tourne vers l'AVANT.
  - Right/Left Arm : X positif = part vers l'avant (-Z) puis monte
    par-dessus jusqu'a X=180 (au-dessus de la tete). X=90 = horizontale,
    droit devant. X negatif = derriere le corps.
  - Torso Y (torsion) : Y POSITIF fait pivoter l'EPAULE DROITE VERS
    L'AVANT (donc l'epaule GAUCHE vers l'arriere) -- Y negatif fait
    l'inverse (epaule gauche en avant). Un jab gauche "lache" donc sur Y
    NEGATIF (epaule gauche projetee en avant), un cross droit sur Y
    POSITIF -- exactement l'inverse l'un de l'autre, ce qui fait que le
    buste OSCILLE d'un cote a l'autre a chaque coup, jamais un aller
    simple : c'est cette oscillation, pas des pauses, qui enchaine les
    coups sans a-coup.
  - Left Arm : X va dans le MEME sens que Right Arm (avant = -Z pour les
    deux bras, symetrie du rig) ; Z va dans le sens OPPOSE (deja etabli
    sur r6_throne_crown/r6_directional_punch -- "vers l'exterieur" du
    corps a un signe different pour chaque bras).
  - HumanoidRootPart Y=180 : personnage retourne, "devant" devient +Z --
    utilise pour le mannequin (place plus loin en -Z, doit faire face a
    l'attaquant).
  - Aucun coude/genou (contrainte du rig, voir r6_rig.py).
"""
import math

import numpy as np

from r6_rig import JOINTS, PART_SIZES, joint_for_part

REST = (0.0, 0.0, 0.0)


def _euler_xyz_matrix(rx_deg, ry_deg, rz_deg):
    """Meme maths que anim_engine.euler_xyz_matrix (CFrame.Angles de
    Roblox), reimplementee ici pour garder ce module sans dependance a
    bpy -- dump_scene_data.py l'importe directement, sans passer par
    anim_engine/bpy."""
    rx, ry, rz = math.radians(rx_deg), math.radians(ry_deg), math.radians(rz_deg)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rx @ Ry @ Rz


def grounded_root_y(torso_rot, leg_rot, leg_part, target_y=0.0):
    """Hauteur de racine EXACTE qui pose le pied de `leg_part` a
    `target_y` (le sol), etant donnes les rotations prevues du buste et
    de cette jambe -- cinematique directe (memes C0/C1 que anim_engine/
    calibrate.py). Resolu analytiquement, pas par recherche numerique :
    translater la racine en Y deplace le pied de EXACTEMENT la meme
    quantite (la rotation ne depend pas de Y), donc une seule evaluation
    suffit. Necessaire car mesure (voir README, passe "placement") : le
    buste (Torso) qui pivote fort au coil souleve ou enfonce le pied
    BIEN PLUS que la rotation propre de la jambe elle-meme (jusqu'a 0,24
    stud sur le hook rien qu'avec la rotation du buste, jambe locale a
    zero) -- un simple offset constant sur root_pos.Y ne peut pas suivre
    ca, il faut la vraie cinematique."""
    joint = joint_for_part(leg_part)
    c0 = np.array(JOINTS[joint]["C0"]["pos"])
    c1 = np.array(JOINTS[joint]["C1"]["pos"])
    r_torso = _euler_xyz_matrix(*torso_rot)
    r_leg_local = _euler_xyz_matrix(*leg_rot)
    leg_local_pos = c0 - r_leg_local @ c1
    r_leg_world = r_torso @ r_leg_local
    half = PART_SIZES[leg_part][1] / 2.0
    tip_offset_y = (r_torso @ leg_local_pos + r_leg_world @ np.array([0.0, -half, 0.0]))[1]
    return target_y - tip_offset_y


def grounded_root_y_balanced(torso_rot, left_rot, right_rot, target_y=0.0):
    """Quand les DEUX jambes portent du poids (charge, avant tout
    transfert marque vers l'avant ou l'arriere), caler sur une seule
    jambe laisse forcement l'autre flotter ou s'enfoncer d'autant (les
    deux solutions individuelles sont symetriques par rapport a la
    moyenne, le systeme etant lineaire en root_pos.Y) -- mesure sur le
    hook : 0,236 stud de chaque cote au lieu de 0 d'un cote et 0,47 de
    l'autre si on force une seule jambe. La moyenne partage l'erreur
    entre les deux pieds plutot que de la concentrer sur un seul."""
    y_left = grounded_root_y(torso_rot, left_rot, "Left Leg", target_y)
    y_right = grounded_root_y(torso_rot, right_rot, "Right Leg", target_y)
    return (y_left + y_right) / 2.0


def _kf(time, root_pos=(0.0, 3.0, 0.0), HumanoidRootPart=REST, Torso=REST,
        Head=REST, **legs_arms):
    d = {
        "time": time,
        "root_pos": root_pos,
        "HumanoidRootPart": HumanoidRootPart,
        "Torso": Torso,
        "Head": Head,
    }
    d.update(legs_arms)
    return d


GROUND_Y = 3.0
ATTACKER_Z0 = -1.2
DUMMY_Z = -6.6
SNAP = 1 / 30  # une frame de sortie a 30 fps -- voir docstring de module

# -- Jeu de jambes : root_pos.Y a d'abord ete varie via un simple OFFSET
# CONSTANT (creuse pendant la charge, remonte au lacher) pour vendre
# l'idee que le coup part des jambes. Mesure (foot_check.py) apres coup :
# le rig n'a pas de genou -- baisser la racine d'un montant fixe, sans
# tenir compte de la rotation reelle du buste et de la jambe a cet
# instant precis, fait SOMBRER un pied sous le sol (jusqu'a -0,10 stud
# mesure) pendant qu'une autre pose, elle, fait flotter l'autre pied
# encore plus haut -- le buste seul (Torso qui pivote fort au coil) peut
# soulever un pied de 0,24 stud, BIEN PLUS que la rotation propre de la
# jambe. Retour utilisateur ("le placement... n'est pas bon") confirme.
# Remplace par `grounded_root_y()` (plus haut) : la racine est calee par
# la VRAIE cinematique directe (meme C0/C1 que anim_engine/calibrate.py)
# pour que la jambe AVANT (celle qui plante) ait son pied exactement au
# sol a chaque pose, quelle que soit la rotation du buste ce jour-la --
# jamais un offset devine.

# -- Chronologie -- retour utilisateur (analyse frame par frame des 3
# videos de reference, deuxieme passe, ciblee sur la FLUIDITE et non plus
# l'impact) : ce qui lit comme "smooth"/professionnel n'est PAS une
# interpolation continue de bout en bout -- c'est l'inverse. Sur les 3
# refs, ~5-8% des frames seulement montrent une VRAIE pose intermediaire
# en train de bouger ; le reste alterne des HOLDS reellement statiques
# (4 a 17x plus longs que le coup lui-meme) et un SNAP quasi instantane
# (1-3 frames) pour le lacher -- jamais une pose qui "coule" en continu
# de la charge au contact. Notre version precedente interpolait tout en
# continu (AUTO_CLAMPED de bout en bout) : ca lit comme une animation
# "tweenee" (mou, jamais vraiment charge ni vraiment relache), pas comme
# un vrai coup. Corrige : un vrai HOLD statique (keyframe dupliquee, meme
# pose) au COIL de chaque coup -- durree croissante jab<cross<hook,
# meme logique d'escalade que le reste du projet -- puis un lacher tout
# aussi bref qu'avant (SNAP=1/30, inchange). Pendant le hold, la scene
# n'est PAS morte : le halo de charge du poing (drawFistCharge, deja
# pulse en continu sur toute la fenetre windup->impact) continue de
# vivre a l'ecran independamment de la pose du rig -- exactement le
# "quelque chose bouge toujours meme pendant un hold" releve sur les
# refs (VFX/camera, jamais le rig lui-meme, qui lui reste sciemment figE).
# Toutes les constantes de chronologie ci-dessous sont construites en
# NOMBRE DE FRAMES entieres (a 30 fps) plutot qu'en secondes decimales --
# piege trouve en implementant ce hold : `calibrate.py` mesure via
# `idx_at(t) = round(t*60)` sur un echantillonnage a 60 Hz ; si `t` (donc
# JAB_T/CROSS_T/HOOK_T) ne tombe pas exactement sur ce quadrillage, la
# mesure attrape un instant legerement DECALE de l'impact reel -- negligeable
# d'habitude (~3 ms), mais suffisant pour fausser sensiblement l'ecart de
# contact du cross une fois la chronologie retimee (ecart mesure tombe a
# 0.339 stud avec une Y fausse de 0.32 stud, alors que rien dans la pose
# elle-meme n'avait change). Corrige a la racine : chaque instant est un
# nombre entier de frames /30, donc systematiquement un multiple exact de
# 1/60 egalement -- aucune ambiguite d'arrondi possible.
def _fr(n):
    return n / 30.0


JAB_HOLD = _fr(3)     # jab : hold court (coup rapide, leger)
CROSS_HOLD = _fr(5)
HOOK_HOLD = _fr(7)    # hook (finisher) : hold le plus long

GARDE_T = _fr(5)
JAB_WINDUP_T = _fr(10)                        # arrivee a la pose de charge
JAB_WINDUP_HOLD_T = JAB_WINDUP_T + JAB_HOLD   # meme pose, tenue -- vrai hold (frame 13)
JAB_HIPDRIVE_T = JAB_WINDUP_HOLD_T + _fr(2) - SNAP  # lacher bref (frame 14)
JAB_T = JAB_WINDUP_HOLD_T + _fr(2)                  # frame 15

CROSS_WINDUP_T = JAB_T + _fr(5)                # = retour du jab qui devient l'armement du cross (frame 20)
CROSS_COIL_T = CROSS_WINDUP_T + _fr(5)         # arrivee au coil (frame 25)
CROSS_COIL_HOLD_T = CROSS_COIL_T + CROSS_HOLD  # meme pose, tenue -- vrai hold (frame 30)
CROSS_HIPDRIVE_T = CROSS_COIL_HOLD_T + _fr(3) - SNAP  # frame 32
CROSS_T = CROSS_COIL_HOLD_T + _fr(3)                  # frame 33

HOOK_WINDUP_T = CROSS_T + _fr(5)               # = retour du cross qui devient l'armement du hook (frame 38)
HOOK_COIL_T = HOOK_WINDUP_T + _fr(6)           # arrivee au coil (le plus charge du combo, frame 44)
HOOK_COIL_HOLD_T = HOOK_COIL_T + HOOK_HOLD     # meme pose, tenue -- le hold le plus long (frame 51)
HOOK_HIPDRIVE_T = HOOK_COIL_HOLD_T + _fr(3) - SNAP    # frame 53
HOOK_T = HOOK_COIL_HOLD_T + _fr(3)                    # frame 54

DURATION = HOOK_T + 1.05


def lerp3(a, b, f):
    return tuple(a[i] + f * (b[i] - a[i]) for i in range(3))


def lerp_legs(a, b, f):
    return {k: lerp3(a[k], b[k], f) for k in a}


# ---------------------------------------------------------------------
# Garde -- stance de combat alerte (pas la charge lente du direct du
# droit) : buste legerement penche en avant, poings deja hauts pres du
# visage, jambes deja flechies -- un combo part d'une garde prete, pas
# d'une pose neutre relachee.
_READY_TORSO = (5, 0, 0)
_READY_HEAD = (3, 0, 0)
_READY_LEGS = {"Right Leg": (5, 0, 7), "Left Leg": (7, 0, -6)}
_READY_ARMS = {"Right Arm": (62, 0, -10), "Left Arm": (66, 0, 12)}
_READY_ROOT_Y = grounded_root_y(_READY_TORSO, _READY_LEGS["Left Leg"], "Left Leg")

# -- JAB (gauche) -- rapide, amplitude modeste (un jab ne charge pas
# loin), sert surtout a amorcer l'oscillation du buste pour le cross qui
# suit.
JAB_WINDUP_TORSO = (4, 9, 0)
JAB_WINDUP_HEAD = (3, 5, 0)
JAB_WINDUP_LEGS = {"Right Leg": (7, 0, 8), "Left Leg": (9, 0, -7)}
JAB_WINDUP_LEFT_ARM = (52, 0, 16)
JAB_WINDUP_RIGHT_ARM = (64, 0, -11)
JAB_WINDUP_ROOT_Y = grounded_root_y(JAB_WINDUP_TORSO, JAB_WINDUP_LEGS["Left Leg"], "Left Leg")

JAB_STRIKE_TORSO = (-3, -15, 0)
JAB_STRIKE_HEAD = (5, -7, 0)
JAB_STRIKE_LEGS = {"Right Leg": (2, 0, 6), "Left Leg": (10, 0, -8)}
JAB_STRIKE_LEFT_ARM = (90, 0, 34)     # Z calibre par balayage numerique (0,493 stud, voir calibrate.py)
JAB_STRIKE_RIGHT_ARM = (58, 0, -12)
# Avancee calibree par mesure directe (calibrate.py), pas devinee : la
# premiere passe laissait 3,1 studs d'ecart (le mannequin est loin,
# Z=-6.6, contre une avancee de -0.55 seulement) -- corrige pour amener
# le poing pres du torse au moment de l'impact.
JAB_LUNGE_Z = -4.743

# Chaine cinetique du jab -- fraction reduite par rapport au cross/hook
# (un jab n'a pas besoin d'un runway de chaine cinetique aussi marque,
# c'est un coup rapide du bras plus que des hanches) : buste/jambes/
# racine a 85%, bras gauche (le jab) a seulement 25% -- le payload du
# snap final.
_JF_BODY, _JF_ARM = 0.85, 0.25
JAB_HIPDRIVE_TORSO = lerp3(JAB_WINDUP_TORSO, JAB_STRIKE_TORSO, _JF_BODY)
JAB_HIPDRIVE_HEAD = lerp3(JAB_WINDUP_HEAD, JAB_STRIKE_HEAD, _JF_BODY)
JAB_HIPDRIVE_LEGS = lerp_legs(JAB_WINDUP_LEGS, JAB_STRIKE_LEGS, _JF_BODY)
JAB_HIPDRIVE_LEFT_ARM = lerp3(JAB_WINDUP_LEFT_ARM, JAB_STRIKE_LEFT_ARM, _JF_ARM)
JAB_HIPDRIVE_RIGHT_ARM = lerp3(JAB_WINDUP_RIGHT_ARM, JAB_STRIKE_RIGHT_ARM, _JF_BODY)
JAB_HIPDRIVE_ROOT_Z = ATTACKER_Z0 + _JF_BODY * (JAB_LUNGE_Z - ATTACKER_Z0)
JAB_HIPDRIVE_ROOT_Y = grounded_root_y(JAB_HIPDRIVE_TORSO, JAB_HIPDRIVE_LEGS["Left Leg"], "Left Leg")

# -- CROSS (droit) -- meme mecanique de puissance que r6_directional_punch
# (chaine cinetique complete, buste dominant), retimee ici pour s'enchainer
# directement depuis le retour du jab. Les valeurs STRIKE_* sont les
# memes que celles calibrees dans r6_directional_punch (ecart de contact
# 0,366 stud verifie la-bas) -- reutilisees telles quelles, pas redevinees.
CROSS_WINDUP_TORSO = (6, 6, 1)      # le buste repart de la torsion du jab (Y negatif) vers l'autre sens
CROSS_WINDUP_HEAD = (5, 4, 0)
CROSS_WINDUP_LEGS = {"Right Leg": (9, 0, 9), "Left Leg": (10, 0, -7)}
CROSS_WINDUP_RIGHT_ARM = (-25, 0, -9)
CROSS_WINDUP_LEFT_ARM = (58, 0, 20)
# Racine calee sur la jambe AVANT (Left, plantee) pour ce buste-la --
# voir grounded_root_y(), passe "placement".
# Cale sur LA MOYENNE des deux jambes pendant la charge -- le poids
# n'est pas encore transfere d'un cote, une seule jambe de reference
# laisse l'autre flotter/s'enfoncer de deux fois plus (mesure, voir
# grounded_root_y_balanced()). Le transfert franc vers l'avant (Left)
# n'arrive qu'au hip-drive/strike.
CROSS_WINDUP_ROOT_Y = grounded_root_y_balanced(CROSS_WINDUP_TORSO, CROSS_WINDUP_LEGS["Left Leg"], CROSS_WINDUP_LEGS["Right Leg"])

CROSS_COIL_TORSO = (11, -28, 3)
CROSS_COIL_HEAD = (9, -18, 0)
# Jeu de jambes -- retour utilisateur ("les jambes c'est trop statique",
# PUIS "le placement et le jeu de jambes n'est pas bon" une fois le
# premier essai mesure). Diagnostic mesure (voir foot_check dans le
# README) : le rig n'a pas de genou -- CHAQUE degre de rotation de
# hanche (X ou Z, les deux comptent, angle combine) souleve le PIED du
# sol proportionnellement a 1-cos(angle), puisque la jambe est un
# segment rigide qui pivote day autour de la hanche. Le premier essai
# (Left Leg jusqu'a 34 degres) soulevait le pied de 0,29 a 0,57 stud au-
# dessus du sol au moment meme du coup -- visible, pas juste "pas assez
# de jeu de jambes" comme avant, mais un vrai defaut de placement.
# Correction "placement" : la jambe AVANT (Left, qui plante/encaisse le
# transfert de poids pour un cross) reste PRES DE LA VERTICALE au moment
# du coup (angle modeste, pied mesure a moins de 0,05 stud du sol) ; la
# jambe ARRIERE (Right, qui pousse/pivote sur l'avant du pied) porte le
# vrai swing visible -- un talon qui se souleve en poussant est
# anatomiquement correct, un pied avant qui flotte a 0,3 stud ne l'est
# pas.
# Correction "axes des jambes" (retour utilisateur suivant : "les appuis
# sont toujours pareils, vers l'avant, le jeu de jambes doit changer
# selon l'envoi de la charge") : Right Leg.Z restait TOUJOURS POSITIF et
# grandissait juste en magnitude d'un coup a l'autre (7 -> 9 -> 16...),
# jamais un vrai changement d'axe -- ca lit comme "toujours la meme
# jambe qui pousse pareil", pas un pivot qui repond a la direction du
# coup. Corrige : Z se charge tres large vers l'exterieur au coil (comme
# le bras, meme principe de chambrage) puis BASCULE de signe au strike
# (pivot du talon qui se termine, le pied a fini de tourner) -- le meme
# renversement deja utilise sur le bras du hook (Z: -78 -> 91), applique
# ici a la jambe qui pivote.
CROSS_COIL_LEGS = {"Right Leg": (16, 0, 26), "Left Leg": (11, 0, -8)}
CROSS_COIL_RIGHT_ARM = (-85, 0, -17)
CROSS_COIL_LEFT_ARM = (46, 0, 40)
CROSS_COIL_ROOT_Y = grounded_root_y_balanced(CROSS_COIL_TORSO, CROSS_COIL_LEGS["Left Leg"], CROSS_COIL_LEGS["Right Leg"])

CROSS_STRIKE_TORSO = (-8, 34, 0)
CROSS_STRIKE_HEAD = (10, 12, 0)
# Jambe arriere (Right) qui pousse/pivote : le pied a fini de pivoter,
# Z bascule de +26 (charge, tourne vers l'exterieur) a -22 (pivot
# termine, tourne vers l'interieur) -- un vrai renversement d'axe, pas
# juste "plus grand", X reste modeste (pas de bascule vers l'arriere,
# le talon se souleve mais la jambe ne penche pas en arriere). Jambe
# avant (Left) qui plante : angle modeste, pied mesure a moins de 0,05
# stud du sol (voir foot_check.py) au lieu des 0,29 stud du tout premier
# essai.
CROSS_STRIKE_LEGS = {"Right Leg": (6, 0, -8), "Left Leg": (5, 0, 2)}
CROSS_STRIKE_RIGHT_ARM = (90, 0, -4)
CROSS_STRIKE_LEFT_ARM = (10, 0, -18)
# Idem jab : calibre par mesure. Premiere valeur (-7.109) etait FAUSSE --
# calculee a partir d'une mesure contaminee par le secondary motion actif
# depuis JAB_T (voir plus bas), qui perturbait deja legerement la pose du
# cross a son propre instant d'impact. Recalcule PROPREMENT
# (secondary_motion=None pendant la mesure) une fois le t_min corrige.
CROSS_LUNGE_Z = -4.6513

_CF_BODY, _CF_ARM = 0.92, 0.20
CROSS_HIPDRIVE_TORSO = lerp3(CROSS_COIL_TORSO, CROSS_STRIKE_TORSO, _CF_BODY)
CROSS_HIPDRIVE_HEAD = lerp3(CROSS_COIL_HEAD, CROSS_STRIKE_HEAD, _CF_BODY)
CROSS_HIPDRIVE_LEGS = lerp_legs(CROSS_COIL_LEGS, CROSS_STRIKE_LEGS, _CF_BODY)
CROSS_HIPDRIVE_RIGHT_ARM = lerp3(CROSS_COIL_RIGHT_ARM, CROSS_STRIKE_RIGHT_ARM, _CF_ARM)
CROSS_HIPDRIVE_LEFT_ARM = lerp3(CROSS_COIL_LEFT_ARM, CROSS_STRIKE_LEFT_ARM, 0.85)
CROSS_HIPDRIVE_ROOT_Z = ATTACKER_Z0 + _CF_BODY * (CROSS_LUNGE_Z - ATTACKER_Z0)
CROSS_HIPDRIVE_ROOT_Y = grounded_root_y(CROSS_HIPDRIVE_TORSO, CROSS_HIPDRIVE_LEGS["Left Leg"], "Left Leg")

# -- HOOK (gauche) -- le finisher : pas un coup droit mais un balayage
# lateral (Z, pas seulement X) porte par une GRANDE rotation du buste --
# lecture visuelle differente du cross (qui "pousse" tout droit, le hook
# "balaie" autour). Amplitude la plus grande du combo, VFX les plus
# lourds (voir le lecteur).
HOOK_WINDUP_TORSO = (8, -22, -2)     # repart de la torsion du cross (Y positif) vers l'autre sens
HOOK_WINDUP_HEAD = (6, -12, 0)
# Chambrage large des le windup (Left.Z deja tres negatif, pas juste au
# coil) -- le hook a le chambrage le plus large du combo, ca doit se
# lire des le debut de l'amorce, pas seulement au pic du coil.
HOOK_WINDUP_LEGS = {"Right Leg": (12, 0, 10), "Left Leg": (14, 0, -22)}
# Convention (docstring de module) : Z bras GAUCHE negatif = vers
# l'EXTERIEUR du corps, positif = vers l'INTERIEUR (croise). Un hook se
# charge large vers l'exterieur (Z tres negatif) puis BALAYE vers
# l'interieur en frappant (Z devient positif a l'impact) -- c'est cet
# arc lateral, pas une simple extension en X, qui distingue le hook du
# jab/cross (tous deux des coups droits).
HOOK_WINDUP_LEFT_ARM = (70, 0, -50)
HOOK_WINDUP_RIGHT_ARM = (30, 0, -14)
HOOK_WINDUP_ROOT_Y = grounded_root_y_balanced(HOOK_WINDUP_TORSO, HOOK_WINDUP_LEGS["Left Leg"], HOOK_WINDUP_LEGS["Right Leg"])

HOOK_COIL_TORSO = (14, -40, -4)
HOOK_COIL_HEAD = (9, -24, 0)
# Retour utilisateur ("les axes des jambes doivent changer selon l'envoi
# de la charge") : Left.Z va chercher le chambrage le plus large du
# combo (-34, plus loin que le windup, echo direct au bras gauche qui va
# a -78) ; Right.Z se charge aussi (24, plus que la windup) -- LES DEUX
# jambes participent au chargement du hook (contrairement au cross ou
# seule la jambe arriere bouge vraiment), coherent avec un coup qui
# tourne toute la hanche plutot que de pousser tout droit.
HOOK_COIL_LEGS = {"Right Leg": (14, 0, 13), "Left Leg": (9, 0, -14)}
HOOK_COIL_LEFT_ARM = (78, 0, -78)
HOOK_COIL_RIGHT_ARM = (26, 0, -16)
# Mesure sans compensation : le buste seul (X=14, Y=-40) souleve deja le
# pied avant de 0,24 stud, bien avant meme de compter la rotation propre
# de la jambe -- voir grounded_root_y(), passe "placement".
HOOK_COIL_ROOT_Y = grounded_root_y_balanced(HOOK_COIL_TORSO, HOOK_COIL_LEGS["Left Leg"], HOOK_COIL_LEGS["Right Leg"])

HOOK_STRIKE_TORSO = (-10, 46, 2)
HOOK_STRIKE_HEAD = (12, 22, 0)
# Le hook pivote sur la jambe AVANT (Left, meme cote que le bras qui
# frappe) : un vrai lead hook pivote sur la BOULE du pied avant, talon
# legerement souleve -- mesure (foot_check.py), un X trop grand (34)
# soulevait le pied ENTIER de 0,40 stud, bien au-dela d'un talon qui se
# souleve, donc X reste modeste ici. Le vrai pivot se lit sur Z, qui
# BASCULE de signe (-34 au coil -> +30 au strike, le plus grand
# renversement du combo, coherent avec le hook = finisher) -- Right Leg
# suit aussi le mouvement (24 -> -18, renversement plus modeste, la
# jambe arriere accompagne la rotation de hanche sans la dominer).
HOOK_STRIKE_LEGS = {"Right Leg": (10, 0, -10), "Left Leg": (14, 0, 12)}
HOOK_STRIKE_LEFT_ARM = (88, 0, 91)     # balaye de l'exterieur (Z negatif, charge) vers l'interieur (Z positif, croise sur la cible) -- Z calibre par balayage numerique (0,380 stud, voir calibrate.py), pas devine
HOOK_STRIKE_RIGHT_ARM = (18, 0, -20)
# Idem jab/cross : calibre par mesure PROPRE (secondary_motion=None).
HOOK_LUNGE_Z = CROSS_LUNGE_Z - 2.102

_HF_BODY, _HF_ARM = 0.90, 0.18
HOOK_HIPDRIVE_TORSO = lerp3(HOOK_COIL_TORSO, HOOK_STRIKE_TORSO, _HF_BODY)
HOOK_HIPDRIVE_HEAD = lerp3(HOOK_COIL_HEAD, HOOK_STRIKE_HEAD, _HF_BODY)
HOOK_HIPDRIVE_LEGS = lerp_legs(HOOK_COIL_LEGS, HOOK_STRIKE_LEGS, _HF_BODY)
HOOK_HIPDRIVE_LEFT_ARM = lerp3(HOOK_COIL_LEFT_ARM, HOOK_STRIKE_LEFT_ARM, _HF_ARM)
HOOK_HIPDRIVE_RIGHT_ARM = lerp3(HOOK_COIL_RIGHT_ARM, HOOK_STRIKE_RIGHT_ARM, _HF_BODY)
HOOK_HIPDRIVE_ROOT_Z = CROSS_LUNGE_Z + _HF_BODY * (HOOK_LUNGE_Z - CROSS_LUNGE_Z)
HOOK_HIPDRIVE_ROOT_Y = grounded_root_y(HOOK_HIPDRIVE_TORSO, HOOK_HIPDRIVE_LEGS["Left Leg"], "Left Leg")

# -- Follow-through + pose finale (fiere, le combo est termine) --
OVERSHOOT_TORSO = (2, 58, 4)
OVERSHOOT_HEAD = (16, 26, 0)
OVERSHOOT_LEFT_ARM = (96, 0, -44)

RECOVER_TORSO = (-10, 10, 0)
RECOVER_HEAD = (-6, 4, 0)
RECOVER_LEFT_ARM = (30, 0, 12)
RECOVER_RIGHT_ARM = (34, 0, -14)

# OVERSHOOT/RECOVER reutilisent HOOK_STRIKE_LEGS (le corps continue sur
# sa lancee, les jambes n'ont pas de nouvelle pose propre) -- mais le
# buste, lui, continue de tourner (OVERSHOOT_TORSO.Y=58 contre 46 au
# strike), ce qui a lui seul soulevait les deux pieds de plus de 0,2
# stud (mesure) avant cette correction. Cale sur la jambe avant, comme
# le reste du combo.
OVERSHOOT_ROOT_Y = grounded_root_y_balanced(OVERSHOOT_TORSO, HOOK_STRIKE_LEGS["Left Leg"], HOOK_STRIKE_LEGS["Right Leg"])
RECOVER_ROOT_Y = grounded_root_y_balanced(RECOVER_TORSO, HOOK_STRIKE_LEGS["Left Leg"], HOOK_STRIKE_LEGS["Right Leg"])

FINAL_TORSO = (-8, 0, 0)
FINAL_HEAD = (-6, 0, 0)
FINAL_ROOT_Y = grounded_root_y(FINAL_TORSO, _READY_LEGS["Left Leg"], "Left Leg")


def attacker_combo():
    keyframes = [
        _kf(0.00, root_pos=(0, _READY_ROOT_Y, ATTACKER_Z0), Torso=_READY_TORSO, Head=_READY_HEAD,
            **_READY_LEGS, **_READY_ARMS),
        _kf(GARDE_T, root_pos=(0, _READY_ROOT_Y, ATTACKER_Z0), Torso=_READY_TORSO, Head=_READY_HEAD,
            **_READY_LEGS, **_READY_ARMS),

        # -- JAB -- charge, HOLD reel (meme pose tenue -- pas juste un
        # point de passage), puis lacher bref. Le halo de charge du poing
        # (lecteur, drawFistCharge) continue de pulser pendant tout le
        # hold : le rig est statique, l'ecran ne l'est jamais.
        _kf(JAB_WINDUP_T, root_pos=(0, JAB_WINDUP_ROOT_Y, ATTACKER_Z0), Torso=JAB_WINDUP_TORSO, Head=JAB_WINDUP_HEAD,
            **JAB_WINDUP_LEGS, **{"Left Arm": JAB_WINDUP_LEFT_ARM, "Right Arm": JAB_WINDUP_RIGHT_ARM}),
        _kf(JAB_WINDUP_HOLD_T, root_pos=(0, JAB_WINDUP_ROOT_Y, ATTACKER_Z0), Torso=JAB_WINDUP_TORSO, Head=JAB_WINDUP_HEAD,
            **JAB_WINDUP_LEGS, **{"Left Arm": JAB_WINDUP_LEFT_ARM, "Right Arm": JAB_WINDUP_RIGHT_ARM}),
        _kf(JAB_HIPDRIVE_T, root_pos=(0, JAB_HIPDRIVE_ROOT_Y, JAB_HIPDRIVE_ROOT_Z), Torso=JAB_HIPDRIVE_TORSO, Head=JAB_HIPDRIVE_HEAD,
            **JAB_HIPDRIVE_LEGS, **{"Left Arm": JAB_HIPDRIVE_LEFT_ARM, "Right Arm": JAB_HIPDRIVE_RIGHT_ARM}),
        _kf(JAB_T, root_pos=(0, GROUND_Y, JAB_LUNGE_Z), Torso=JAB_STRIKE_TORSO, Head=JAB_STRIKE_HEAD,
            **JAB_STRIKE_LEGS, **{"Left Arm": JAB_STRIKE_LEFT_ARM, "Right Arm": JAB_STRIKE_RIGHT_ARM}),

        # -- CROSS (le retour du jab EST l'armement du cross -- pas de
        # pause NEUTRE, mais un vrai HOLD au coil, meme principe que le
        # jab) -- root_pos.Y calee par grounded_root_y() sur la jambe
        # avant (Left) a chaque pose intermediaire, PAS un offset
        # constant (voir la note "placement" plus haut) --
        _kf(CROSS_WINDUP_T, root_pos=(0, CROSS_WINDUP_ROOT_Y, JAB_LUNGE_Z), Torso=CROSS_WINDUP_TORSO, Head=CROSS_WINDUP_HEAD,
            **CROSS_WINDUP_LEGS, **{"Right Arm": CROSS_WINDUP_RIGHT_ARM, "Left Arm": CROSS_WINDUP_LEFT_ARM}),
        _kf(CROSS_COIL_T, root_pos=(0, CROSS_COIL_ROOT_Y, JAB_LUNGE_Z), Torso=CROSS_COIL_TORSO, Head=CROSS_COIL_HEAD,
            **CROSS_COIL_LEGS, **{"Right Arm": CROSS_COIL_RIGHT_ARM, "Left Arm": CROSS_COIL_LEFT_ARM}),
        _kf(CROSS_COIL_HOLD_T, root_pos=(0, CROSS_COIL_ROOT_Y, JAB_LUNGE_Z), Torso=CROSS_COIL_TORSO, Head=CROSS_COIL_HEAD,
            **CROSS_COIL_LEGS, **{"Right Arm": CROSS_COIL_RIGHT_ARM, "Left Arm": CROSS_COIL_LEFT_ARM}),
        _kf(CROSS_HIPDRIVE_T, root_pos=(0, CROSS_HIPDRIVE_ROOT_Y, CROSS_HIPDRIVE_ROOT_Z), Torso=CROSS_HIPDRIVE_TORSO, Head=CROSS_HIPDRIVE_HEAD,
            **CROSS_HIPDRIVE_LEGS, **{"Right Arm": CROSS_HIPDRIVE_RIGHT_ARM, "Left Arm": CROSS_HIPDRIVE_LEFT_ARM}),
        _kf(CROSS_T, root_pos=(0, GROUND_Y, CROSS_LUNGE_Z), Torso=CROSS_STRIKE_TORSO, Head=CROSS_STRIKE_HEAD,
            **CROSS_STRIKE_LEGS, **{"Right Arm": CROSS_STRIKE_RIGHT_ARM, "Left Arm": CROSS_STRIKE_LEFT_ARM}),

        # -- HOOK (finisher -- le retour du cross EST l'armement du hook)
        # -- meme principe, root_pos.Y calee par cinematique directe --
        _kf(HOOK_WINDUP_T, root_pos=(0, HOOK_WINDUP_ROOT_Y, CROSS_LUNGE_Z), Torso=HOOK_WINDUP_TORSO, Head=HOOK_WINDUP_HEAD,
            **HOOK_WINDUP_LEGS, **{"Left Arm": HOOK_WINDUP_LEFT_ARM, "Right Arm": HOOK_WINDUP_RIGHT_ARM}),
        _kf(HOOK_COIL_T, root_pos=(0, HOOK_COIL_ROOT_Y, CROSS_LUNGE_Z), Torso=HOOK_COIL_TORSO, Head=HOOK_COIL_HEAD,
            **HOOK_COIL_LEGS, **{"Left Arm": HOOK_COIL_LEFT_ARM, "Right Arm": HOOK_COIL_RIGHT_ARM}),
        _kf(HOOK_COIL_HOLD_T, root_pos=(0, HOOK_COIL_ROOT_Y, CROSS_LUNGE_Z), Torso=HOOK_COIL_TORSO, Head=HOOK_COIL_HEAD,
            **HOOK_COIL_LEGS, **{"Left Arm": HOOK_COIL_LEFT_ARM, "Right Arm": HOOK_COIL_RIGHT_ARM}),
        _kf(HOOK_HIPDRIVE_T, root_pos=(0, HOOK_HIPDRIVE_ROOT_Y, HOOK_HIPDRIVE_ROOT_Z), Torso=HOOK_HIPDRIVE_TORSO, Head=HOOK_HIPDRIVE_HEAD,
            **HOOK_HIPDRIVE_LEGS, **{"Left Arm": HOOK_HIPDRIVE_LEFT_ARM, "Right Arm": HOOK_HIPDRIVE_RIGHT_ARM}),
        _kf(HOOK_T, root_pos=(0, GROUND_Y, HOOK_LUNGE_Z), Torso=HOOK_STRIKE_TORSO, Head=HOOK_STRIKE_HEAD,
            **HOOK_STRIKE_LEGS, **{"Left Arm": HOOK_STRIKE_LEFT_ARM, "Right Arm": HOOK_STRIKE_RIGHT_ARM}),

        # -- follow-through + pose finale -- root_pos.Y a nouveau calee
        # par cinematique directe (le buste continue de tourner apres
        # l'impact, ce qui a lui seul souleve les pieds -- voir plus haut) --
        _kf(HOOK_T + 0.08, root_pos=(0, OVERSHOOT_ROOT_Y, HOOK_LUNGE_Z - 0.2), Torso=OVERSHOOT_TORSO, Head=OVERSHOOT_HEAD,
            **HOOK_STRIKE_LEGS, **{"Left Arm": OVERSHOOT_LEFT_ARM, "Right Arm": HOOK_STRIKE_RIGHT_ARM}),
        _kf(HOOK_T + 0.45, root_pos=(0, RECOVER_ROOT_Y, HOOK_LUNGE_Z), Torso=RECOVER_TORSO, Head=RECOVER_HEAD,
            **HOOK_STRIKE_LEGS, **{"Left Arm": RECOVER_LEFT_ARM, "Right Arm": RECOVER_RIGHT_ARM}),
        _kf(DURATION, root_pos=(0, FINAL_ROOT_Y, HOOK_LUNGE_Z + 0.35), Torso=FINAL_TORSO, Head=FINAL_HEAD,
            **_READY_LEGS, **{"Left Arm": (10, 0, 12), "Right Arm": (10, 0, -12)}),
    ]
    phases = [
        {"name": "garde", "t0": 0.00, "t1": JAB_WINDUP_T, "expected_reversals": {}},
        {"name": "jab", "t0": JAB_WINDUP_T, "t1": JAB_T, "expected_reversals": {}},
        {"name": "cross", "t0": JAB_T, "t1": CROSS_T, "expected_reversals": {}},
        {"name": "hook", "t0": CROSS_T, "t1": HOOK_T, "expected_reversals": {}},
        {"name": "suite", "t0": HOOK_T, "t1": HOOK_T + 0.45, "expected_reversals": {}},
        {"name": "posture_finale", "t0": HOOK_T + 0.45, "t1": DURATION, "expected_reversals": {}},
    ]
    preview_times = [0.0, GARDE_T, JAB_WINDUP_T, JAB_T, CROSS_WINDUP_T, CROSS_COIL_T, CROSS_T,
                      HOOK_WINDUP_T, HOOK_COIL_T, HOOK_T, HOOK_T + 0.45, DURATION]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


# -----------------------------------------------------------------------
# Mannequin : encaisse les 3 coups avec une intensite croissante (leger
# flinch au jab, vacillement au cross, projection au hook -- le combo
# doit se lire comme une escalade, pas 3 fois le meme recul). Racine
# Y=180 (face a l'attaquant, "devant" = +Z pour lui), meme convention que
# r6_directional_punch.
DUMMY_IDLE_TORSO = (0, 0, 0)
DUMMY_IDLE_HEAD = (0, 0, 0)
DUMMY_IDLE_ARMS = {"Right Arm": (4, 0, 10), "Left Arm": (4, 0, -10)}
DUMMY_IDLE_LEGS = {"Right Leg": (0, 0, 3), "Left Leg": (0, 0, -3)}

JAB_HIT_TORSO = (-10, 0, 3)
JAB_HIT_HEAD = (-16, -4, 0)
JAB_HIT_ARMS = {"Right Arm": (40, 0, 20), "Left Arm": (40, 0, -25)}
JAB_HIT_LEGS = {"Right Leg": (-4, 0, 4), "Left Leg": (2, 0, -4)}
# -- whiplash : la rotation continue un instant au-dela de la pose de
# contact (l'inertie du coup n'est pas absorbee instantanement), avant un
# rebond elastique partiel qui NE revient PAS a l'idle (le prochain coup
# arrive avant toute recuperation complete -- combo sans temps mort).
JAB_OVERSHOOT_TORSO = (-15, 0, 4)
JAB_OVERSHOOT_HEAD = (-23, -6, 0)
JAB_SETTLE_TORSO = (-6, 0, 2)
JAB_SETTLE_HEAD = (-9, -2, 0)

CROSS_HIT_TORSO = (-30, 0, 7)
CROSS_HIT_HEAD = (-36, -9, 0)
CROSS_HIT_ARMS = {"Right Arm": (130, 0, 50), "Left Arm": (130, 0, -62)}
CROSS_HIT_LEGS = {"Right Leg": (-16, 0, 9), "Left Leg": (9, 0, -12)}
CROSS_OVERSHOOT_TORSO = (-38, 0, 9)
CROSS_OVERSHOOT_HEAD = (-44, -12, 0)
CROSS_SETTLE_TORSO = (-19, 0, 4)
CROSS_SETTLE_HEAD = (-23, -5, 0)

HOOK_HIT_TORSO = (-18, 40, -10)
HOOK_HIT_HEAD = (-24, 46, -6)
HOOK_HIT_ARMS = {"Right Arm": (150, 0, 70), "Left Arm": (150, 0, -85)}
HOOK_HIT_LEGS = {"Right Leg": (-20, 0, 20), "Left Leg": (-8, 0, -22)}
# -- le finisher : whiplash + court hop (racine Y) pendant la projection,
# le corps continue de tourner sous l'impact avant de retomber au sol.
HOOK_OVERSHOOT_TORSO = (-22, 48, -12)
HOOK_OVERSHOOT_HEAD = (-30, 55, -8)
HOOK_HOP_Y = GROUND_Y + 0.42

DAZED_TORSO = (26, 0, -6)
DAZED_HEAD = (14, 8, 0)
DAZED_ARMS = {"Right Arm": (24, 0, 14), "Left Arm": (24, 0, -18)}
DAZED_LEGS = {"Right Leg": (4, 0, 6), "Left Leg": (0, 0, -8)}


def dummy_combo_reaction():
    keyframes = [
        _kf(0.00, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=DUMMY_IDLE_TORSO, Head=DUMMY_IDLE_HEAD, **DUMMY_IDLE_LEGS, **DUMMY_IDLE_ARMS),
        _kf(JAB_T - 0.03, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=DUMMY_IDLE_TORSO, Head=DUMMY_IDLE_HEAD, **DUMMY_IDLE_LEGS, **DUMMY_IDLE_ARMS),
        # -- flinch au jab : snap sur le contact, puis whiplash + rebond
        # partiel (jamais un retour a l'idle -- le cross arrive avant) --
        _kf(JAB_T, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=JAB_HIT_TORSO, Head=JAB_HIT_HEAD, **JAB_HIT_LEGS, **JAB_HIT_ARMS),
        _kf(JAB_T + 0.05, root_pos=(0, GROUND_Y, DUMMY_Z), HumanoidRootPart=(0, 180, 0),
            Torso=JAB_OVERSHOOT_TORSO, Head=JAB_OVERSHOOT_HEAD, **JAB_HIT_LEGS, **JAB_HIT_ARMS),
        _kf(JAB_T + 0.16, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 180, 0),
            Torso=JAB_SETTLE_TORSO, Head=JAB_SETTLE_HEAD, **JAB_HIT_LEGS, **JAB_HIT_ARMS),
        _kf(CROSS_T - 0.03, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 180, 0),
            Torso=JAB_SETTLE_TORSO, Head=JAB_SETTLE_HEAD, **JAB_HIT_LEGS, **JAB_HIT_ARMS),
        # -- vacille fort au cross : meme principe (snap -> whiplash ->
        # rebond partiel), amplitude plus grande --
        _kf(CROSS_T, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 180, 0),
            Torso=CROSS_HIT_TORSO, Head=CROSS_HIT_HEAD, **CROSS_HIT_LEGS, **CROSS_HIT_ARMS),
        _kf(CROSS_T + 0.06, root_pos=(0, GROUND_Y, DUMMY_Z - 0.15), HumanoidRootPart=(0, 180, 0),
            Torso=CROSS_OVERSHOOT_TORSO, Head=CROSS_OVERSHOOT_HEAD, **CROSS_HIT_LEGS, **CROSS_HIT_ARMS),
        _kf(CROSS_T + 0.20, root_pos=(0, GROUND_Y, DUMMY_Z - 0.85), HumanoidRootPart=(0, 180, 0),
            Torso=CROSS_SETTLE_TORSO, Head=CROSS_SETTLE_HEAD, **CROSS_HIT_LEGS, **CROSS_HIT_ARMS),
        _kf(HOOK_T - 0.03, root_pos=(0, GROUND_Y, DUMMY_Z - 0.85), HumanoidRootPart=(0, 165, 0),
            Torso=CROSS_SETTLE_TORSO, Head=CROSS_SETTLE_HEAD, **CROSS_HIT_LEGS, **CROSS_HIT_ARMS),
        # -- projete par le hook : le plus grand deplacement, tete/torse
        # tournent fort (coup lateral), whiplash + court hop pendant la
        # projection avant l'atterrissage --
        _kf(HOOK_T, root_pos=(0, GROUND_Y, DUMMY_Z - 0.85), HumanoidRootPart=(0, 150, 0),
            Torso=HOOK_HIT_TORSO, Head=HOOK_HIT_HEAD, **HOOK_HIT_LEGS, **HOOK_HIT_ARMS),
        _kf(HOOK_T + 0.08, root_pos=(0, HOOK_HOP_Y, DUMMY_Z - 1.35), HumanoidRootPart=(0, 145, 0),
            Torso=HOOK_OVERSHOOT_TORSO, Head=HOOK_OVERSHOOT_HEAD, **HOOK_HIT_LEGS, **HOOK_HIT_ARMS),
        _kf(HOOK_T + 0.35, root_pos=(0, GROUND_Y, DUMMY_Z - 2.6), HumanoidRootPart=(0, 130, 0),
            Torso=HOOK_HIT_TORSO, Head=HOOK_HIT_HEAD, **HOOK_HIT_LEGS, **HOOK_HIT_ARMS),
        _kf(HOOK_T + 0.75, root_pos=(0, GROUND_Y, DUMMY_Z - 3.0), HumanoidRootPart=(0, 140, 0),
            Torso=DAZED_TORSO, Head=DAZED_HEAD, **DAZED_LEGS, **DAZED_ARMS),
        _kf(DURATION, root_pos=(0, GROUND_Y, DUMMY_Z - 3.0), HumanoidRootPart=(0, 140, 0),
            Torso=DAZED_TORSO, Head=DAZED_HEAD, **DAZED_LEGS, **DAZED_ARMS),
    ]
    phases = [
        {"name": "attente", "t0": 0.00, "t1": JAB_T, "expected_reversals": {}},
        {"name": "jab_encaisse", "t0": JAB_T, "t1": CROSS_T, "expected_reversals": {}},
        {"name": "cross_encaisse", "t0": CROSS_T, "t1": HOOK_T, "expected_reversals": {}},
        {"name": "projete", "t0": HOOK_T, "t1": DURATION, "expected_reversals": {}},
    ]
    preview_times = [0.0, JAB_T, JAB_T + 0.05, CROSS_T, CROSS_T + 0.06, HOOK_T, HOOK_T + 0.08,
                      HOOK_T + 0.35, HOOK_T + 0.75, DURATION]
    engine_opts = {"handle_type": "AUTO_CLAMPED"}
    return keyframes, phases, preview_times, engine_opts


# -- Secondary motion -- UN SEUL t_min par part supporte par
# anim_engine._spring_chase (pas un par coup) : le mettre a JAB_T (le
# 1er coup) perturberait alors la pose CALIBREE du cross et du hook a
# leurs propres instants d'impact (trouve par calibrate.py -- l'ecart de
# contact du cross/hook explosait a 1,6/2,5 studs avec t_min=JAB_T,
# contre le residu attendu de ~0,5-1 stud une fois retombe a t_min=HOOK_T
# seul). Donc, comme r6_directional_punch, la vibration ne s'applique
# qu'APRES le DERNIER coup du combo (le hook, le seul qui a un vrai
# follow-through tenu) -- les coups intermediaires (jab, cross) restent
# des poses CFrame propres a leur instant d'impact, sans interference.
ATTACKER_SECONDARY_MOTION = {
    "Torso": {"channels": (0, 1, 2), "stiffness": 300.0,
              "damping_ratio": 0.42, "t_min": HOOK_T},
    "Left Arm": {"channels": (0, 2), "stiffness": 340.0,
                 "damping_ratio": 0.45, "t_min": HOOK_T},
}
DUMMY_SECONDARY_MOTION = {
    "Torso": {"channels": (0, 1, 2), "stiffness": 100.0,
              "damping_ratio": 0.45, "t_min": JAB_T},
    "Head": {"channels": (0, 1, 2), "stiffness": 150.0,
             "damping_ratio": 0.5, "t_min": JAB_T},
}
