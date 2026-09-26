# A1 : TSB, coups courts (M1-M4, Swift Sweep, Fail, Victim)

Chantier 4, agent A1. Source unique : `b64ecce0-tsb_anim.rbxm`, les 7
KeyframeSequences M1, M2, M3, M4, Swift Sweep, Swift Sweep (Fail) et Swift
Sweep (Victim). Rien n'a été modifié dans `/home/user/Jeux`.

Ce sont des **apprentissages**, pas des règles : « ici, l'animateur fait X
parce que Y (ou je le suppose) ».

Statuts utilisés :
- **vu** : je l'ai regardé moi-même sur les planches ;
- **mesuré** : sorti d'un outil ;
- **lu** : texte ;
- **déduit** : mon interprétation.

Repère : « avant » = -Z = la cible, qui est devant le perso. Le **lacet** du
torse est compté + quand le torse tourne vers sa gauche. La **hauteur** est
celle du centre du torse (3,0 debout).

## 0. Ce que j'ai regardé, et comment

**Planches de l'outil du dépôt** (`planche_cles.py`) : chaque clé, en 3/4 et
de profil, plus le rythme et les arcs.
- Fichiers : `frames/A1_tsb_coups_courts/{M1,M2,M3,M4,Swift_Sweep,Swift_Sweep__Fail_,Swift_Sweep__Victim_}.png`
  (et un `.json` par anim).
- Tout est sous `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/c4/`.
- Les rendus font 200 px : trop petits pour juger une pose. Je les ai
  complétés par mon propre outil.

**Mon outil `c4/a1/voir.py`** montre **toutes les images à 60 i/s**, sous 4
caméras (de haut en bas) :
- **face** : devant le perso, côté cible ;
- **profil** : à sa droite ;
- **dos** : derrière, légèrement au-dessus. C'est proche de la caméra de jeu ;
- **dessus**.

Un cadre jaune marque une image où une clé est posée, avec les parts posées
sous l'image.

Planches regardées, toutes images incluses :
- `v_M1.png` (27 img), `v_M2.png` (29), `v_M3.png` (28), `v_M4.png` (42) ;
- `v_SS_a.png` et `v_SS_b.png` (Swift Sweep, 97 img en deux moitiés) ;
- `v_SSF.png` (Fail, 43) et `v_SSV.png` (Victim, 36 ; caméras face, profil,
  dos et 3/4) ;
- pour la comparaison : `v_nous_frappe.png` (notre attaquant f262-295,
  caméra qui suit le torse).

**Mes outils de mesure** (`c4/a1/mesure.py`, `c4/a1/pieds.py`) : par image, on
obtient :
- le torse : lacet, penché, hauteur ;
- le lacet MONDE de la tête et son écart au torse ;
- la vitesse des poings ;
- la rotation par image de chaque part, relative à son parent ;
- la position des pieds et des poings dans le repère du coup.

Sorties brutes : `c4/a1/m_*.txt` et `p_*.txt`.

**Aussi extraits** :
- les temps exacts des clés ;
- les **KeyframeMarkers** du fichier : jamais lus avant, voir §3 ;
- la continuité exacte entre anims.

**Chargement.** `corpus.load_rbxm_sequences` ignore bien les Poses de poids 0.
C'était le bug relevé dans `pro_tsb_m1_m4.json`, corrigé depuis ; je l'ai
vérifié dans le code, lignes 60-66. Le torse de M4 n'a donc pas de fausses
pointes.

**Limite générale.** Je vois des blocs R6 en fil de fer, sans le jeu :
- ni l'anim de marche ou d'idle du dessous, qui porte les jambes de M1-M3 ;
- ni la caméra de jeu réelle ;
- ni les VFX, ni le son.

Tout ce qui touche à l'effet en jeu est donc « déduit ».

---

## 1. PAR SOURCE

### 1.1 M1 : crochet du GAUCHE (0,43 s, 27 images, 7 clés)

**Ce qui est fait** (vu sur `v_M1.png`, mesuré dans `m_M1.txt`) :

**f0, pose de départ** (clé : torse, tête, 2 bras).
- Torse tourné vers sa gauche (lacet +48), bras DROIT tendu devant et bas,
  bras gauche derrière.
- C'est la fin d'un direct du droit, pas une garde.
- Le torse est déjà bas : hauteur 2,82.

**f0→f6, anticipation**, 6 images, clé à f6 (torse + 2 bras, sans la tête).
- Le torse se dévisse de +48 à +6 (7°/img), penche en avant jusqu'à +16° et
  descend à 2,62.
- Le bras gauche part en arrière.
- Les deux poings dérivent à ~15 studs/s.

**f6→f10, frappe.**
- Le torse claque de +6 à -44 : 18°/img sur f6-8, puis 8°/img sur f8-10.
- Le poing gauche file à **67-73 studs/s pendant 4 images** : c'est un
  palier. Il balaie à hauteur d'épaule, de la gauche vers la droite.
- Il est au plus loin devant (2,57 studs) à f8, croise l'axe de la cible
  vers f9 et finit sur la droite du corps (vu en vue de dessus).
- Le bras droit est ARRACHÉ en arrière à 38°/img sur f6-8 : c'est le bras
  qui recule, le « contre-mouvement ».

**f10→f26, suite** (16 images, 60 % de l'anim).
- Le poing ralentit par paliers : 37 studs/s pendant 4 images, puis 6-7.
- Le torse finit sa rotation à -70 (f20), puis revient un peu, à -65 (f26).
- Pendant la frappe, le torse se redresse de +16 à -2, puis -6.

**Comment c'est fabriqué** (mesuré, temps des clés) :

| clé | f0 | f6 | f8 | f10 | f14 | f20 | f26 |
|---|---|---|---|---|---|---|---|
| parts posées | T H BD BG | T BD BG | T H BD BG | T BG | T H BD BG | T | T H BD BG |

- **L'amorti est fait par l'espacement des clés, pas par une courbe.** Toutes
  les clés sont en Linear (lu : `ETUDE_TSB.md` §1). Entre deux clés, la
  vitesse est donc constante.
- L'animateur espace ses clés de 2, 2, 4, 6, 6 images après l'anticipation,
  et chaque intervalle couvre un angle de torse plus petit : 34°, 16°, 19°,
  7°. On obtient un « ease-out » en escalier : rapide, puis moins, puis
  presque rien. (mesuré)
- **Les parts sont posées sélectivement** (mesuré sur le tableau ; lecture
  déduite) :
  - à f10, seuls le torse et le bras gauche, qui frappe, reçoivent une clé ;
  - le bras droit n'a plus de clé entre f8 et f14 : il fait un seul trajet
    lent, et c'est lui qui s'arrête le premier ;
  - à f20, seul le torse est posé : il continue seul sa rotation ;
  - la tête n'est posée qu'à f0, f8, f14 et f26 : c'est la part la plus
    « molle », elle dérive jusqu'à la fin.
  - Effet : les parts **partent ensemble** (toutes posées à f0 et f6) mais
    **s'arrêtent en décalé**. Le bras arrière s'arrête vers f8, le bras qui
    frappe à f10-14, le torse à f20, la tête glisse jusqu'à f26.
  - Le décalage est dans les **fins**, pas dans les départs.
- **La tête garde la cible.** (mesuré)
  - Le torse balaie 118° (+48 → -70). La tête, en lacet monde, ne balaie que
    37° (+8 → -29).
  - Par rapport au torse, elle contre-tourne de -40 à +45.
  - Déduit : c'est un réflexe de combattant (on ne quitte pas l'adversaire
    des yeux), et ça garde le visage lisible à la caméra.

**Pourquoi ça marche** (déduit).
- Le spectateur voit un départ presque immobile (15 studs/s), puis un
  poing qui passe d'un coup à pleine vitesse.
- Il n'y a pas de rampe d'accélération. Le contraste lent → rapide fait le
  « claquement », et la suite longue (60 % de l'anim) laisse lire la pose
  d'arrivée.

**Surprise.** M1 ne part PAS d'une garde. Sa pose f0 est la fin d'un direct
du droit.
- L'anticipation de M1 dure exactement **6 images = 0,1 s**. C'est la durée
  par défaut du fondu d'`AnimationTrack:Play()` (0,1 s ; lu ailleurs, pas
  vérifié ici).
- Déduit, hypothèse : la pose f0 n'est presque jamais vue à plein poids,
  puisque le fondu depuis l'idle couvre justement ces 6 images. Ce qui
  compte, c'est la pose f6 (armé).
- Je ne peux pas le vérifier sans le jeu.

### 1.2 M2 : direct du DROIT, plongeant (0,47 s, 29 images, 6 clés)

**Départ.** M2 commence **exactement** sur la dernière clé de M1 : écart 0,000
sur les 4 parts (mesuré).

**f0→f7, anticipation** (7 images).
- Le torse revient de -65 à -30 (5°/img) et **plonge** vers l'avant : +20°.
- Le bras droit monte à hauteur de tête : vu en vue de face, bras vert levé
  près de la tête à f7.

**f7→f10, frappe** (3 images).
- Torse : -30 → +9 (13°/img). Il continue de plonger, jusqu'à +32°.
- Poing droit : **78-80 studs/s, constant, 3 images**.
- À f10, le bras droit est à l'horizontale, droit devant (bras « coup az +6
  el +4 »). Vu de profil : bras horizontal, torse en diagonale à ~32°.

**f10→f28, suite** (18 images).
- Le torse NE S'ARRÊTE PAS : il tourne encore de +9 à +51 et penche jusqu'à
  +37 (f18).
- Le bras droit continue vers le bas et vers la gauche (« coup az -34 el
  -26 » à f18).
- Le poing dérive à 15 studs/s pendant 8 images, puis à 10.
- Il n'y a aucune image immobile.

**Clés.**
- f0, f7 et f10 : tout est posé.
- f18 : torse et bras droit seulement. f22 : torse, tête et bras droit.
- Le bras gauche, libre, n'a plus de clé entre f10 et f28 : il se pose le
  premier.
- Même schéma que M1 : départ groupé, fins étagées. (mesuré ; lecture
  déduite)

**Tête.** Le torse balaie 116° (-65 → +51). La tête reste entre -20 et +10
en monde (mesuré).

**Hauteur du torse.** Constante à 2,70 pendant tout le coup. Le poids passe
par le **penché** (0 → +37°), pas par une descente verticale. (mesuré)

### 1.3 M3 : direct du GAUCHE, qui se redresse (0,44 s, 28 images, 8 clés)

**Départ.** Commence exactement sur la fin de M2 (écart 0,000).

**f0→f6, armé très rapide.** Le torse passe de +51 à -40 : **91° en 6 images,
15°/img**.
- C'est l'intervalle le plus rapide du torse sur tout M3.
- Surprise : l'anticipation n'est pas lente ici.
- Déduit : M2 a fini loin sur sa gauche (+51), et la frappe de M3 part vers
  la droite. Le « retour » EST déjà le mouvement du coup.

**f6→f8, frappe.**
- Le poing gauche passe à 70 puis 65 studs/s.
- Le torse finit à -59.
- Le torse se **redresse et passe en arrière** : +17 → -12 à f10, et monte de
  2,77 à 2,88.
- Le bras droit remonte devant le visage, en garde (vu, vue de face f8-f27).

**f10→f27, tenue presque immobile** (17 images).
- Poings à 1-3 studs/s, mais jamais 0.
- Clés « de vie » : f12 (torse et bras gauche), f17 (torse, tête, bras
  gauche), f23 (torse et bras gauche).
- Le bras droit, en garde, n'est plus posé de f10 à f27.

**Clés.** f0, 6, 8, 10, 12, 17, 23, 27 : les intervalles s'allongent (6, 2,
2, 2, 5, 6, 4).

**Pourquoi** (déduit). Après deux coups où le corps se jette (M1 en rotation,
M2 en plongée), M3 est un coup **droit et net** : torse qui se redresse, garde
haute.
- La tenue de 0,25 s sert de respiration avant le coup de pied final.
- La variété du combo passe par l'axe vertical du corps : M1 penche en avant
  pendant l'armé, M2 plonge, M3 se redresse, M4 part en arrière.

### 1.4 M4 : coup de pied DROIT sauté, ferme le combo (0,69 s, 42 images, 22 clés)

**Départ.** Commence exactement sur la fin de M3. C'est le seul des quatre qui
pose les jambes.

**f0→f12, montée** (vu de profil sur `v_M4.png`, mesuré dans `pieds.py M4`).
- La jambe droite monte en diagonale devant : le pied passe de 0 à 2,8 studs
  de haut et à 2,2 devant. R6 n'a pas de genou : c'est une jambe tendue qui
  se lève.
- Le pied va à **18-28 studs/s, régulier** : c'est une dérive, pas un coup.
- Le **torse monte** de 2,86 à 3,42 et le pied d'appui quitte le sol
  (+0,48 à f12) : **petit saut** dans le coup.
- Le torse part en arrière : 0 → -32°.
- Le bras gauche monte au-dessus de la tête (poing à 4,6 de haut), le bras
  droit part derrière : les bras s'ouvrent pour l'équilibre.

**f12→f13, claquement : 1 image.**
- Le pied saute de 1,25 stud (**88 studs/s**) jusqu'à l'extension :
  3,44 devant, 3,30 de haut, à l'horizontale.
- Torse : +23° en une image, penché à -41°.
- La clé f13 pose torse, tête et jambes, **pas les bras** : ils traînent
  derrière le claquement, en interpolant de f12 à f15. (mesuré ; effet
  déduit)

**f13-f14.** L'extension est tenue 2 images.

**f15-f20.** La jambe redescend (64, 41, 30 studs/s) et le torse retombe à
2,82.

**f20-f41, récupération** (21 images). Le pied droit revient sous le corps en
glissant (de 2,0 à 0,5 devant), le torse revient de +60 à +23 et les bras se
replient en garde.
- On voit des clés d'UN seul bras, alternées : f18 BG, f20 BD, f21 BG,
  f24 BD, f25 BD, f28 BG, f29 BD.
- Déduit : c'est une passe de polissage pour que les deux bras ne se posent
  pas en même temps (« casser les jumeaux »).

**Tête.** Le torse balaie 118° (-58 → +60). La tête reste entre -9 et +13 en
monde (mesuré).

**Correction de `ETUDE_TSB.md` §4 bis.**
- L'étude disait « jambe à l'horizontale, f9-f15 ». Mesuré : la jambe MONTE
  en diagonale de f0 à f12, n'est à l'horizontale qu'à **f13-f14**, après un
  claquement d'une image, et redescend dès f15.
- Le petit saut (pied d'appui à +0,48) n'était pas noté.

### 1.5 Swift Sweep : balayage en vrille puis coup de pied haut tenu (1,60 s, 97 images, 24 clés)

Vu sur `v_SS_a.png` et `v_SS_b.png` ; mesuré dans `m_SS.txt` et `p_SS.txt`.

**Départ.** L'anim part du **neutre** (hauteur 2,96, lacet ≈ 0) : c'est une
compétence qui se lance depuis n'importe où.

**f0→f7, amorce lente.** Le torse tourne de +19 (3°/img) et descend à 2,80.

**f7→f19, la vrille démarre.**
- Le torse tourne de plus en plus vite : 9°/img, puis **17°/img**.
- Il descend (2,53 → 2,21) et penche en avant de +35°.
- Le pied gauche part en arrière.

**f19→f30, balayage bas.** La jambe gauche, tendue, fait le tour du corps à
**66-77 studs/s**, à 0,5-1,1 stud du sol (vu : jambe jaune à plat, vues
profil et dos).
- Le torse est **accroupi à 1,80** : 1,2 stud sous la hauteur debout.
- Il penche sur le côté (+40 à +60° de côté, lu dans la sortie de planche).
- Il a fait un tour complet à f30.

**f30→f50, la spirale monte.** La jambe continue de tourner, mais **ralentit
en montant** : 40-47 studs/s à 1-2 studs de haut, puis 20 studs/s à 2,4-3,4.
- Le torse remonte à 3,20. Le corps a fait ~1,7 tour au total (603°,
  mesuré en dépliant l'angle).
- Déduit : le balayage bas se transforme sans arrêt en coup de pied haut.
  L'élan de la vrille est « rangé » dans la montée.

**f50→f52, claquement.**
- Le pied gauche saute à l'extension : **165 studs/s sur 1 image**,
  4,1 studs de haut, 3,5 devant.
- Le torse se couche sur le côté : ~95° de côté. Vu de profil : jambe jaune
  horizontale à hauteur d'épaule, torse couché.

**f51→f54, tremblement d'impact.** 4 clés à 1 image d'écart.
- La hauteur du torse alterne : 3,03 / 3,16 / 3,03 / 3,15.
- Le pied **dépasse** d'environ 0,3 stud à f52 (4,13 de haut), puis revient
  à 3,90 à f53. C'est un dépassement d'une image, puis le recul.
- Déduit : c'est une vibration de choc cuite dans l'anim, pas un tremblement
  de caméra.

**f52→f75, tenue du coup de pied** : **23 images, 0,38 s**. Elle n'est pas
figée.
- Le pied ne dérive que de 1 à 6 studs/s.
- Le **bassin s'enfonce** doucement : torse de 3,16 à 2,48.
- La tête dérive aussi.

**f75→f96, retour.** La jambe redescend lentement (pied gauche à 6-10
studs/s) et le torse se redresse.
- L'anim finit **pas au neutre** : lacet -56, hauteur 2,83.
- Avec « loop » activé, le raccord fin → début est cassé (écart de rotation
  0,79). Déduit : la boucle n'est pas utilisée telle quelle, ou le jeu
  coupe au marqueur `End`.

**Tête : le « spotting » des danseurs** (mesuré, angles dépliés).
- Pendant le 1er quart de tour (f0-f19), la tête RESTE vers la cible : son
  retard sur le torse grandit jusqu'à -80° (torse +177, tête +96 en monde).
- Puis elle **rattrape d'un coup** : de f19 à f22, elle tourne de 111°
  (37°/img) pendant que le torse fait 49° (16°/img).
- Ensuite elle suit le torse avec un retard de 8 à 29°.
- Déduit : c'est ce que font les danseurs et les combattants en vrille. On
  garde le regard, on le fouette, on le retrouve. Ça rend la vrille
  lisible : le spectateur voit le perso « viser » avant de tourner.

**Clés.**
- Jusqu'à f50, presque toutes les clés posent TOUTES les parts, à un
  intervalle régulier de 5-7 images (7, 6, 5, 1, 5, 3, 3, 6, 7, 7).
- Puis 4 clés à 1 image d'écart (le choc), puis des clés espacées de 5-6
  images pendant la tenue.
- Déduit : pour un mouvement de corps entier (vrille), l'animateur
  travaille « pose à pose », tout le corps à chaque clé. Le décalage part
  par part des M1 sert surtout aux bras.

### 1.6 Swift Sweep (Fail) : le balayage qui rate (0,70 s, 43 images, 17 clés)

**Départ.** Part du neutre EXACT (identité) et **revient au neutre exact** à
f40 : écart 0 (mesuré). Il peut donc se raccorder à l'idle sans fondu
visible.

**Pas d'amorce.** Le torse tourne à **20°/img dès l'image 1** (0 → +124 à f6).
C'est l'inverse de Swift Sweep, qui a 7 images lentes.

**Bas du corps.**
- Descente jusqu'à 1,40 à f19 : plus bas que la version réussie.
- La jambe gauche balaie devant (25-56 studs/s).
- Un seul tour de corps : exactement 360° à f40.

**Tête : ici, elle MÈNE.** (mesuré)
- Elle est en avance sur le torse de +27° (f6) à **+67°** (f12), puis
  l'écart se résorbe à 0 en fin de tour.
- C'est l'inverse de la version réussie, où la tête restait en arrière.
- Déduit, deux lectures possibles :
  1. l'échec = un corps emporté par sa vrille, la tête qui part devant sans
     viser ;
  2. c'est un choix pratique (le Fail est plus court).

  Je rattache la 1re lecture à CARNET 2.1d : mener par la tête = contrôle,
  mener par le corps = emporté. Ici, pourtant, c'est la tête qui mène dans
  l'échec, ce qui ne colle pas simplement avec 2.1d. **Je n'ai pas de
  conclusion.**

**Clés.**
- f12-f15 : 4 clés consécutives de la jambe gauche seule. L'animateur
  sculpte l'arc du pied image par image, là où il passe devant.
- f19 à f26 : clés de bras seuls et de tête seule, en alternance. C'est une
  passe de décalage.

### 1.7 Swift Sweep (Victim) : la réaction (0,58 s, 36 images, 9 clés)

**Départ.** Part du neutre.

**f0→f5, repli** : 5 images, 0,083 s.
- Le torse se plie en avant de +35° et descend de 0,66 stud (3,00 → 2,34).
- La jambe gauche part en arrière : pied à -1,42.
- Les bras pendent vers l'avant.

**La tête plonge plus vite et plus loin que le torse** (mesuré).
- Regard à -33° dès f2 (torse -14), -66° à f4 (torse -28).
- À f6, elle regarde **droit vers le sol** : -84 à -90°, sans remonter
  jusqu'à la fin.
- Déduit : tête lâchée, menton sur la poitrine = sonné, sans contrôle.

**f5→f16, poursuite lente.** Le torse continue de +35 à +48° (1°/img) et
descend encore (2,34 → 2,10).

**f16→f35, tenue.** Poings et pieds à 0-2 studs/s. Le torse revient à peine :
+48 → +45.

**Aucun lacet** : 0° sur toute l'anim (mesuré).
- La réaction est purement dans le plan avant-arrière, symétrique.
- La direction du coup est donnée par la jambe qui part (la gauche, en
  arrière) et par la chute vers l'avant, pas par une torsion.

**Timing de réaction** (déduit).
- Le choc est encaissé en 5 images, à une vitesse comparable au coup :
  poing droit à 24 studs/s. Puis 11 images de « dérive d'inertie », puis la
  tenue.
- Même structure que les coups : un bloc rapide, puis une longue fin qui
  ralentit.

**Ce que je ne sais PAS.** Quel marqueur de Swift Sweep lance l'anim de la
victime (`Kick1` à f24 ? `Kick2` à f52 ?). Rien dans le fichier ne le dit :
c'est dans le script du jeu.

---

## 2. LE COMBO M1→M4 COMME UN SEUL OBJET

**2.1 Les fins et les débuts sont identiques au 0,000 près.** (mesuré)
- M1 fin = M2 début, M2 fin = M3 début, M3 fin = M4 début.
- Déduit : l'animateur a copié la dernière pose de chaque coup comme
  première pose du suivant. Si le coup suivant arrive, aucun fondu ne peut
  créer de « glissement ».
- M4 → M1 n'est PAS continu. M1 part de sa propre pose ; la boucle du
  combo se referme par un fondu.

**2.2 Le torse fait des allers-retours de ~115°.** (mesuré)

| coup | lacet du torse | amplitude |
|---|---|---|
| M1 | +48 → -70 | 118° |
| M2 | -65 → +51 | 116° |
| M3 | +51 → -59 | 110° |
| M4 | -58 → +60 | 118° |

- Chaque coup tourne dans le sens opposé du précédent.
- **La fin (la suite) du coup N est l'armé du coup N+1.**
- Déduit : c'est le principe qui rend le combo fluide. On ne revient jamais
  en garde neutre entre deux coups ; le corps oscille d'un côté à l'autre
  comme un balancier.

**2.3 Le membre qui frappe change à chaque coup.**
- Bras gauche en crochet horizontal, puis bras droit en direct plongeant,
  puis bras gauche en direct montant, puis jambe droite sautée.
- L'axe vertical du corps varie aussi :
  - M1 penche en avant pendant l'armé et se redresse à la frappe ;
  - M2 plonge (+37°) ;
  - M3 se redresse (-12°) et monte ;
  - M4 part en arrière (-41°) et saute.

**2.4 La hauteur de garde est basse.** Le torse est entre 2,62 et 2,88 sur M1
à M3, soit 0,1 à 0,4 stud sous le debout (3,0). (mesuré)
- Les jambes n'étant pas posées, elles suivent le torse.
- Dans ma lecture « jambes au repos », les pieds passent de 0,2 à 0,36 stud
  sous le sol.
- **Je ne sais pas ce qu'il en est en jeu** : ça dépend de l'idle ou de la
  course de TSB, absentes du fichier.

**2.5 Le temps de chaque coup.**

| | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| armé | 6 img | 7 | 6 (rapide) | 12 (montée) |
| frappe | 4 | 3 | 2 | 1 (claquement) |
| marqueur `hitreg` | f10 | f10,4 | f8 | f12,7 |
| suite / tenue | 16 | 18 | 19 | 28 |
| total | 26 | 28 | 27 | 41 |

- La frappe est toujours la phase la plus courte ; la suite, la plus longue.
  (mesuré)
- Le coup est compté au **bout** de la phase rapide, ou au milieu du
  claquement pour M4, soit à 0,13-0,21 s du début.

---

## 3. DÉCOUVERTE : l'anim « chef d'orchestre » (KeyframeMarkers)

Jamais lus avant dans le cerveau : `fiches/VFX.md` parle des marqueurs en
général, sans ceux de TSB. (mesuré, extraits du fichier)

**Temps en images à 60 i/s :**
- M1 : `hitreg` f10, `end` f25,3.
- M2 : `hitreg` f10,4, `end` f27,9.
- M3 : `hitreg` f8, `end` f26,7.
- M4 : `hitreg` f12,7, `end` f40,7.
- Swift Sweep : `Kick1` f24, `SmokeSlash` f36, `Kick2` f52, `End` f96.
- Swift Sweep (Fail) : `sweep` f10, `kick` f42.
- Hors de mon périmètre, vus en passant :
  - Collateral Ruin : `SpeedLinesStart`, `SpeedlinesFinale`,
    `SpinnerSmokeEffect`, `StartHitbox`, `EndHitbox`, `DownMesh` ;
  - Stoic Bomb : `ChargingSound`, `Voiceline`, `BeginSlowing`,
    `HitboxExplosion?`, `FinalBoarExplosion` ;
  - Ultimate1 : `ParticleActivate`, `TweenStuff`, `StartLoop`,
    `AwakenFinale` ;
  - WallCombo : `hit1`, `hit2`, `hit3`.

**Ce que j'en comprends** (déduit) :
- Chez TSB, l'animation **porte les rendez-vous** : hitbox, fumée, lignes de
  vitesse, son, voix, ralenti (`BeginSlowing`). Le script écoute les
  marqueurs ; il ne compte pas le temps.
- On peut retimer l'anim sans casser la synchro des VFX.
- `SmokeSlash` tombe en pleine spirale montante (f36), pas sur un coup : la
  fumée habille le mouvement lui-même.
- `hitreg` est posé à la fin du segment rapide, quand le poing arrive.
- `end` est juste avant ou sur la dernière clé. Je suppose que c'est
  l'instant où l'entrée suivante peut enchaîner.

---

## 4. DÉCOUVERTE : les clés de M3 et M4 sont sur une grille ×1,5

(mesuré ; méthode déduite)

- Les temps de clé de **M3 et M4** ne tombent sur des images entières à
  60 i/s que multipliés par 1,5.
  - M4 : 8, 14, 18, 19, 20, 23, 27, 28, 30, 31, 34, 36, 37, 40, 42, 43,
    46, 51, 57, 61, 62.
  - M3 : 9, 12, 15, 18, 25, 34, 40.
- Ceux de M2, de Swift Sweep et du Fail sont entiers directement à 60 i/s.
  M1 est entier dans les deux cas : ambigu.
- Lecture la plus probable : M3 et M4 ont été **animés 1,5 fois plus lents**
  (M4 en ~62 images, soit 1,03 s), puis **l'animation entière a été
  accélérée** à 2/3 de sa durée.
- C'est une méthode d'animateur connue : on pose à une vitesse où l'on voit
  ce qu'on fait, puis on compresse.
- Je n'ai pas de preuve directe de l'outil utilisé (Moon Animator ou
  éditeur Roblox). Autre explication possible : une grille de 90 i/s,
  moins probable car non standard.

---

## 5. GRANDS ENSEIGNEMENTS (transversaux)

**5.1 Peu de clés, et chacune porte une décision.** (mesuré)
- M1 : 7 clés, M2 : 6, M3 : 8.
- Ce qui fait tenir la lecture :
  1. une pose d'armé nette, tenue en dérive lente ;
  2. une pose de contact atteinte d'un bloc (1 à 4 images à vitesse
     constante) ;
  3. une suite qui ralentit par paliers, avec des clés de plus en plus
     espacées.
- En Linear, l'espacement des clés EST la courbe de vitesse.

**5.2 Départ groupé, arrêts étagés.** (mesuré sur les parts posées ; lecture
déduite)
- Sur les coups de poing, toutes les parts sont posées à l'armé.
- Puis on retire la clé aux parts « passagères » (bras libre, bras de garde,
  tête), qui s'arrêtent d'abord ou dérivent seules. Le torse et le membre
  qui frappe gardent des clés plus longtemps.
- Le décalage est dans les **fins**, pas dans les départs.
- Exception : M4, où le claquement f13 est posé SANS les bras, pour qu'ils
  traînent.

**5.3 La tête est stabilisée vers la cible** sur les 4 M (mesuré).
- Le torse balaie 110-118°, la tête 18-37° en monde.
- En vrille (Swift Sweep), elle fait du spotting : elle garde la cible,
  puis se fouette pour la retrouver.
- Pour la victime, au contraire, elle est lâchée, regard au sol.

**5.4 Rien n'est jamais figé à 0.** (mesuré)
- Les tenues les plus calmes, M3 f13-27 et Swift Sweep f52-75, ont des
  extrémités à 1-6 studs/s. Le bassin s'enfonce (Swift Sweep : -0,7 stud en
  23 images).
- Des clés de torse ou de bras continuent d'être posées pendant la tenue.

**5.5 Le choc est parfois cuit dans l'anim.**
- Swift Sweep f51-54 : alternance de hauteur de ±0,06 stud à chaque image,
  et un dépassement d'une image du pied (+0,3 stud) avant le retour à la
  pose tenue.
- Je ne l'ai vu que là parmi mes 7 anims. Les M1-M3 n'en ont pas : le choc
  y est sans doute porté par le jeu (VFX, arrêt sur image ?), **non
  vérifiable ici**.

**5.6 Fluidité par balancier et par spirale.** (déduit, d'après 2.2 et 1.5)
- Le combo oscille de gauche à droite ; la fin d'un coup arme le suivant.
- Le Swift Sweep transforme la vitesse de la vrille en montée : bas et
  rapide, puis haut et plus lent, puis claquement.
- Aucune énergie n'est « jetée » par un arrêt net suivi d'un redémarrage.
- C'est peut-être ce que Milan appelle « smooth et enchaînement » (rappel :
  motif CARNET 4b.30). À soumettre, pas à affirmer.

**5.7 Vitesses de référence** (mesuré, studs/s, extrémité qui frappe) :

| | dérive d'armé | frappe | suite |
|---|---|---|---|
| poings | 11-27 | 65-80, en palier de 2 à 4 images | 6-37, par paliers décroissants |
| pieds | 18-28 (montée) | 88 (M4) ou 165 (Swift Sweep), sur 1 image | — |

Balayage : 66-77 studs/s tenus environ 11 images (f19-f30).

---

## 6. CE QUE JE SAURAIS REFAIRE EN R6, CONCRÈTEMENT

**Un M1 façon TSB, 26 images à 60 i/s, en Linear, jambes non posées.**

| clé | image | parts posées | pose |
|---|---|---|---|
| 1 | f0 | toutes | torse tourné de ~45° du côté du bras qui va frapper à l'envers (fin du coup précédent), hauteur ~2,8 |
| 2 | f6 | torse, 2 bras | armé : torse ramené près de 0, penché +15°, un peu plus bas (-0,2) ; bras qui va frapper tiré derrière |
| 3 | f8 | toutes | torse à ~-30° ; bras arrière arraché en arrière, poing qui frappe devant |
| 4 | f10 | torse, bras qui frappe | torse -45°, poing au bout |
| 5 | f14 | toutes | torse -63° |
| 6 | f20 | torse seul | -70° |
| 7 | f26 | toutes | léger retour à -65° ; tête contre-tournée pour garder la cible |

- Marqueur `hitreg` sur la clé 4.

**Un combo de 4.**
- Copier la pose finale de chaque coup comme pose initiale du suivant.
- Alterner le sens du torse (~115°) et le membre qui frappe.
- Varier l'axe vertical : penché, plongé, redressé, en arrière.
- Finir par un membre différent.

**Une vrille avec spotting.** Garder la tête en arrière du torse jusqu'à ~80°
de retard, puis la fouetter en 3 images, à environ 2 fois la vitesse du torse.

**Un coup tenu vivant.**
- Claquement d'une image.
- 2 à 4 clés à 1 image d'écart, avec une alternance de ±0,06 stud du torse
  et un dépassement d'une image de l'extrémité.
- Puis une tenue de ~20 images où le bassin s'enfonce doucement et les clés
  continuent.

**Une réaction de victime.** Repli de 5 images (torse +35°, -0,66 stud), tête
qui plonge deux fois plus vite que le torse jusqu'au sol, 11 images de
dérive, puis la tenue.

**Méthode.**
- Animer 1,5 fois plus lent, puis compresser.
- Poser les marqueurs VFX et son dans l'anim.

## 7. CE QUE JE NE SAURAIS PAS (ou pas vérifié)

- **L'effet réel en jeu**, faute de voir :
  - l'idle et la course de TSB (les jambes de M1-M3) ;
  - le fondu utilisé par le script, ou l'effet d'un `AnimationTrack.Priority`
    non renseigné (`priorité=None` dans le fichier) ;
  - la caméra, les VFX et le son qui répondent aux marqueurs ;
  - un éventuel arrêt sur image au `hitreg`.
- **Le lien entre les anims.** Quel marqueur lance l'anim de la victime ;
  comment Swift Sweep bascule sur le Fail (probablement : pas de cible
  touchée au `sweep` ou au `Kick1`, mais c'est du script).
- **Le sens de la tête qui mène dans le Fail** : pas conclu (§1.6).
- **L'outil de l'animateur** (Moon Animator ou éditeur Roblox) : l'échelle
  ×1,5 est mesurée, pas l'outil.
- **Mes rendus** : blocs de 200 et 140-170 px, sans visage. Je ne peux pas
  juger l'expression, ni les nuances qu'un vrai rendu montrerait (ombres,
  silhouette à la caméra de jeu réelle).

---

## 8. Comparaison courte avec notre « Un seul coup » (usc_attaquant.rbxmx)

Planche de l'outil : `frames/A1_tsb_coups_courts/nous_usc.png` et `.json`. Mes
vues : `v_nous_frappe.png` (f262-295, caméra qui suit). Mesures :
`c4/a1/m_nous.txt`.

**Précaution.** Notre coup est un coup chargé cinématique (ultime), pas un M1.
Les temps de TSB ne se transposent pas tels quels : ce qui suit décrit des
**façons de faire**, pas des chiffres à copier.

**Ce qu'on fait déjà comme TSB** (mesuré) : la tête garde la cible. Le torse
tourne de -77 à +16, la tête reste entre +7 et -11 en monde.

**Ce qu'un animateur TSB ferait autrement** (mesuré sur nous ; « TSB ferait »
= déduit de §1-5) :

1. **Clés.**
   - Nous : 115 clés, **toutes les parts à chaque clé**, 55 intervalles
     d'une seule image. C'est une courbe cuite.
   - TSB poserait 5 à 8 clés choisies pour le coup lui-même (armé, contact,
     2 ou 3 clés de suite), en retirant les parts passagères après le
     contact.
2. **Vitesse de frappe.**
   - Nous : le torse tourne à 4,6-9°/img pendant 16 images (f267-283) et le
     poing culmine à ~45 studs/s, précédé de 10 images à 27-31.
   - TSB : 13-18°/img de torse et 65-80 studs/s de poing, en palier de 2 à
     4 images, après une dérive lente (11-27).
   - Chez nous, le « lent » et le « rapide » sont trop proches : on ne sent
     pas de claquement.
3. **Après le contact.**
   - Nous : le poing passe à 5, puis 0,2, puis **0,0 studs/s** dès f287.
     De f287 à f632 (≈5,8 s), l'attaquant est quasi figé : poings à 0,4 studs/s au plus, aucune part ne tourne de plus de 0,5°/img (mesuré).
   - TSB continue la rotation après le contact (M2 : +42° de torse de plus,
     poing à 10-15 studs/s) ; ses tenues bougent à 1-6 studs/s, avec le
     bassin qui s'enfonce.
   - Une partie de notre gel peut être voulue (la caméra est sur la
     victime), mais un animateur TSB garderait le corps vivant.
4. **Axe vertical.**
   - Nous, au contact : le torse **se redresse et monte** (penché +21 → +8,
     hauteur 2,37 → 2,73).
   - TSB : M2, le seul direct du droit, **plonge** dans le coup (+20 → +37,
     hauteur fixe). M3 se redresse pourtant (-12°, +0,11 stud) : un coup
     peut monter.
   - Déduit : pour un coup censé tout écraser, un animateur TSB choisirait
     sans doute la plongée de M2, et garderait la montée pour un coup « sec
     et net ».
5. **Le choc.** Nous n'avons ni dépassement d'une image ni vibration cuite au
   contact. Swift Sweep les a (§1.5). Nous avons aussi des marqueurs à
   poser : les VFX et le son de notre coup pourraient être pilotés par
   `hitreg` ou `Impact`.

**Suggestion, pas une règle.** Refaire UNIQUEMENT le segment f262-f300 de
notre coup, à la main, avec 6 clés sélectives :
- l'armé tenu, en dérive lente ;
- le contact en 3 images à pleine vitesse, torse plongeant ;
- 2 clés de suite où le torse continue de 30 à 40° ;
- une tenue vivante, avec le bassin qui s'enfonce et un dépassement d'une
  image au contact.

Puis montrer à Milan l'A/B à vitesse réelle, avec la caméra du plan.

---

## Vérification adverse

Vérificateur indépendant, 2026-09-26. Rien n'a été modifié dans le dépôt.

**Méthode.** Je n'ai pas réutilisé `c4/a1/mesure.py` ni les `m_*.txt` du
lecteur. J'ai écrit mes propres scripts dans
`c4/frames/verif_A1_tsb_coups_courts/` :
- `raw.py` lit le `.rbxm` brut : temps exacts des Keyframes, parts posées
  par clé (poids ≠ 0) et KeyframeMarkers avec le temps du Keyframe parent ;
- `ease.py` décode l'Enum `Pose.EasingStyle` / `EasingDirection` (via
  `rbxm_reader.parse_enum_and_vector2`). Le lecteur générique ne décode pas
  les Enum : la thèse « tout est Linear » n'avait jamais été relue dans ce
  fichier, elle venait d'`ETUDE_TSB.md` ;
- `geo.py` mesure par image, à 60 i/s : lacet et penché du torse, hauteur,
  lacet monde de la tête, vitesse des bouts de membres et position des
  pieds.

J'ai aussi relancé `planche_cles.py` sur M1, M4, Swift Sweep, Victim et sur
notre `usc_attaquant.rbxmx`, et **regardé** les planches M1, M4, Swift Sweep
et Victim. Seule source de ce lot : le `.rbxm` TSB. Il n'y a ni tuto ni
sous-titre à relire.

### V1. Balancier du combo (fin de N = armé de N+1) : **confirmé**
- Regardé : les CFrames brutes de la dernière clé posée de N et de la
  première de N+1. Écart max 0,0000 (rotation et position) sur M1→M2,
  M2→M3 et M3→M4 (4 parts ; M4 ajoute les jambes). M4→M1 : écart
  jusqu'à 0,91 (bras gauche) → discontinu.
- Lacets du torse mesurés : M1 +48→-65 (min -70), M2 -65→+51, M3 +51→-58
  (min -60), M4 -58→**+23** (max +60).
- Correction mineure : M4 **finit** à +23, pas à +60. L'amplitude est
  exacte, mais la fin de M4 revient déjà de 37° vers le centre.
- « La boucle se referme par un fondu » est une déduction : le fichier dit
  seulement que c'est discontinu.

### V2. En Linear, l'espacement des clés est la courbe (M1) : **confirmé**
- Regardé : l'EasingStyle décodé vaut 0 (= Linear) sur 100 % des poses des
  7 anims (M1 22, M2 21, M3 26, M4 65, SS 120, Fail 51, Victim 34). Les
  seules poses Constant du fichier (67) sont dans WallComboPlayer.
- Temps M1 : 0, 6, 8, 10, 14, 20, 26, plus une clé vide à 25,325 qui porte
  `end`.
- Torse : 42° / 34° / 16° / 19° / 7°.
- Poing gauche : ~15 (f1-6), 67-73 (f7-10), 36-37 (f11-14), 6-7 studs/s.
  Tout est retrouvé à 1 près.
- Précision : sur f7-8, le poing **droit** part aussi à 64-71 studs/s.
  Pendant 2 images, les deux poings claquent ensemble ; le palier du poing
  qui frappe n'est pas le seul mouvement rapide.

### V3. Départ groupé, arrêts étagés (clés sélectives) : **nuancé**
Le tableau des parts par clé est exact :
- M1 : f10 = T+BG, f20 = T seul, tête à f0/8/14/26 ;
- M2 : BG libre de f10 à f28 ;
- M3 : BD libre de f10 à f26,7 ;
- M4 f13,3 : T H JD JG, sans bras.

Trois corrections :
1. « Toutes les parts sont posées à l'armé » est faux pour M1 : la clé
   d'armé f6 n'a **pas la tête** (T BD BG).
2. M4 : les bras n'interpolent pas « de f12 à f15 ». Le bras gauche va de
   f12 à f18 et le droit de f12 à f20. De plus, en MONDE, ils ne « traînent »
   pas à f13 : portés par le torse (+23° en 1 image), ils filent à 57-68
   studs/s. Le retard n'existe que dans le repère local.
3. Le schéma vaut aussi pour la victime, que le lecteur n'a pas relevée : le
   torse est posé à f5 et les bras à f7 (2 images plus tard) ; le torse
   seul à f31, le reste à f32.

### V4. Tête vers la cible, spotting en vrille : **nuancé**
- **M1** : la tête ne balaie pas 37° mais **50°** (+21 → -29). À l'armé
  (f0→f6), elle tourne à l'**opposé** du torse, de +8 à +21, pendant que
  le torse va de +48 à +6. M2 : 30° ; M3 : 18° ; M4 : 22°. Stabilisation
  confirmée.
- **Swift Sweep** : la tête ne « reste » vers la cible que jusqu'à ~f13
  (tête +9, torse +73).
  - De f13 à f19, elle tourne déjà à la vitesse du torse (13-19°/img), avec
    un retard de 67→81°.
  - Le fouet f19→f22 est exact : tête 111° (37°/img), torse 49°.
  - La tête ne dépasse jamais le torse : elle reste en retard de 8 à 20°
    ensuite. Ce n'est pas le spotting du danseur, où la tête arrive AVANT
    le corps. C'est une tête « tirée » puis rattrapée.

### V5. Marqueurs (hitreg, end, Kick1, SmokeSlash, Kick2, End) : **confirmé**
- Regardé : les KeyframeMarkers bruts et le temps de leur Keyframe parent.
  - M1 : hitreg f10, end f25,325.
  - M2 : hitreg 10,4, end 27,9.
  - M3 : hitreg 8, end 26,675.
  - M4 : hitreg 12,675, end 40,675.
  - SS : Kick1 f24, SmokeSlash f36, Kick2 f52, End f96.
  - Fail : sweep f10, kick f42.
- `Value` est vide ou « 0 ».
- Aucune occurrence de `hitreg` dans le cerveau (grep) : la découverte est
  réelle.
- Précision : le hitreg de M2 (f10,4) et de M4 (f12,675) est porté par une
  **clé vide** créée exprès, hors des clés de pose. Le marqueur est placé
  au temps voulu, pas collé à une clé.
- « Le script écoute l'anim » reste une déduction : invérifiable sans le
  jeu.

### V6. M3/M4 animés ×1,5 puis compressés : **nuancé**
- Les temps ×90 tombent à **±0,0125 image** d'un entier, pas exactement.
  Exemples M4 : 7,987 / 13,988 / 19,013 / 61,988.
- Trois indices en faveur de la thèse :
  - toutes les clés « entières à 60 » de M3/M4 sont **paires** (6, 8, 10,
    12, 18, 20, 24, 28, 34, 38), donc entières ×1,5 ;
  - aucune n'est impaire, ce qui colle avec la thèse ;
  - le `end` de M1 (25,325) a la même signature : M1 est probablement de
    la même famille, et pas seulement « ambigu ».
- Mais l'écart systématique de ±0,0125 n'est pas expliqué. Le mécanisme (un
  étirement de 2/3) reste une hypothèse ; l'outil est invérifiable.

### V7. Correction de la jambe de M4 (horizontale seulement f13-f14) : **confirmé**
- Élévation de la jambe droite : -78° (f0) → -44° (f9) → -34° (f12) → **+5°
  (f13), +4° (f14)** → -18° (f15) → -61° (f19).
- Pied : 88,5 studs/s à f13, (3,30 de haut ; 3,44 devant).
- Pied d'appui à +0,48 à f12 ; torse de 2,86 à 3,42 (f9).
- Vu sur la planche M4 : jambe diagonale à i12, horizontale à i13.
  `ETUDE_TSB §4 bis` (« horizontale f9-f15 ») est donc bien faux.
- Précision : les 1,25 stud sont la composante avant. Le déplacement 3D du
  pied f12→f13 est de 1,47 stud.

### V8. Victime : repli en 5 images, tête lâchée, aucun lacet : **nuancé**
- Tout est retrouvé sur les chiffres :
  - torse à -35° d'élévation et 3,00 → 2,34 à f5 ;
  - tête à -33° (f2), -66° (f4), -83° (f5), puis -84 à -90° ;
  - dérive jusqu'à 48° à f16 ; lacet 0 partout ;
  - poing droit à 22-24 studs/s.
- Correction : la réaction n'est **pas symétrique**. Seule la jambe gauche
  part en arrière (pied à 1,42-1,73 derrière), la droite reste sous le
  corps. Le plan est bien sagittal, mais le corps est asymétrique.
- La tête dépasse la verticale : de f11 à f23, le lacet monde bascule à 180°
  parce que le regard passe au-delà du sol, légèrement vers l'arrière.
- Les bras sont posés à f7, 2 images après le torse (voir V3).
- La synchro avec l'attaquant (Kick1 ou Kick2) reste invérifiable.

### Autres contrôles rapides (hors des 8)
- **Swift Sweep** : confirmé.
  - Amorce +19° en 7 images, puis 9, puis 17-19°/img.
  - Balayage à 65-77 studs/s, pied à 0,47-1,16 de haut, torse à 1,80 min.
  - Cumul +604° à f50, 165,6 studs/s à f52, torse couché à 98° de la
    verticale, hauteurs 3,03 / 3,16 / 3,03 / 3,15, tenue f52-f75.
  - Précision : ce sont **5** clés à 1 image d'écart (f50 à f54), pas 4. La
    tête n'est plus posée de f51 à f92 (40 images) : sa « dérive » est une
    seule interpolation.
- **Fail** : confirmé (18,9 → 22°/img dès f1, identité à f40, tête +67° à
  f12). Oubli : le tour **dépasse** jusqu'à +377° (f31), puis revient à
  360° en 9 images. C'est un dépassement et un retour, pas un arrêt pile.
- **M2 / M3** : confirmés.
  - M2 : penché +20 → +37, hauteur 2,70 fixe, poing à 78-80.
  - M3 : 91° en 6 images, penché -12, +0,11 stud, tenue à 0,9-1,5
    studs/s.
- **Nous (usc_attaquant)** : confirmé.
  - 115 clés, 55 intervalles d'une image, 6 parts à chaque clé.
  - Torse à 4,5-9°/img sur f268-283 ; poing au max à 44,8 studs/s après
    ~10 images à 22-32.
  - Penché +21 → +8, hauteur 2,37 → 2,73.
  - Poings ≤ 0,45 studs/s de f287 à f632.

### Oublis importants
1. **Enum EasingStyle jamais décodé par l'outillage** (`corpus.py` et
   `rbxm_reader.parse_prop_chunks`). « Tout est Linear » tenait sur une
   étude antérieure ; c'est maintenant vérifié (enum 0). Mais un fichier pro
   en Cubic ou Constant serait lu faux sans alerte : `resample_linear`
   interpole toujours en linéaire.
2. **Les marqueurs vivent sur des clés vides** (M1 f25,3 ; M2 f10,4 et
   f27,9 ; M4 f12,675 et f40,675 ; Fail f10 et f42). L'animateur crée un
   Keyframe sans pose juste pour le rendez-vous. Pour notre exporteur, un
   marqueur n'a donc pas besoin de tomber sur une clé de pose.
3. **À l'armé de M1, la tête part à l'opposé du torse** (+8 → +21 pendant
   que le torse va de +48 à +6). C'est une petite contre-anticipation de la
   tête, absente des notes.
4. **Fail : dépassement de 17° de la vrille** avant le retour au neutre.
   C'est le seul « settle » en rotation de ce lot.
5. **Victime asymétrique** : une seule jambe recule, et les bras finissent
   2 images après le torse. Des arrêts étagés, là aussi.
6. **Swift Sweep : la tête n'est pas posée pendant 40 images** (f51-f92),
   pendant toute la tenue et le retour. Sa vie dans la tenue ne vient que
   de l'interpolation.
7. **M1 f7-8 : les deux poings partent ensemble à ~65-70 studs/s.** Le
   « contre-mouvement » du bras arrière est aussi rapide que le coup
   lui-même pendant 2 images.
