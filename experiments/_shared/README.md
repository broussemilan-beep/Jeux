# `_shared/` — outils réutilisables entre prototypes

## `rbxm_reader.py` — lecteur du format binaire `.rbxm`/`.rbxl`

Tous les rigs de ce dépôt jusqu'ici étaient fournis en `.rbxmx` (XML), pour
lequel `resolve_rbxmx.py` (dans chaque prototype) suffit. Le 2026-09-03,
Milan a fourni 3 packs Roblox en `.rbxm` **binaire** (chunks compressés
LZ4) — un format totalement différent, illisible tel quel (un premier
`Read` direct ne rendait que du binaire brut). `rbxm_reader.py` est un
parseur écrit et **validé empiriquement** pour cet usage (pas une lib
tierce vendorisée — aucune lib Python n'était disponible/joignable dans ce
bac à sable pour ce format).

### Méthode de validation (pas de confiance à l'oeil sur un layout deviné)

Le format binaire Roblox n'est pas documenté officiellement — reconstruit
par la communauté (rbx-dom). Chaque hypothèse de layout ici a été
confirmée contre des faits vérifiables, jamais supposée :

- **String/Bool/Int32** : confirmés en relisant `LocalScript.Source` d'un
  des packs et en obtenant le script `Animate.lua` standard de Roblox
  **caractère pour caractère identique** à l'original connu — impossible
  par coïncidence.
- **Float32** (scalaire ou tableau) : passe par le même pipeline que les
  entiers (transposition colonne-par-colonne + zigzag) mais le résultat
  est une **réinterprétation de bits** en IEEE754, pas une conversion de
  valeur. Trouvé en décodant `Humanoid.MaxHealth` : octets bruts
  `0x85900000`, zigzag-décodé (sans cumsum) → entier `1120133120` =
  `0x42C80000` en bits = **100.0f pile** (valeur par défaut plausible).
- **CFrame** (`Motor6D.C0/C1`, `Pose.CFrame`) : la partie ROTATION (matrice
  3x3, quand non-identité) est stockée en flottants **little-endian
  séquentiels bruts** — PAS le pipeline transposé des tableaux. Validé par
  orthonormalité de la matrice (`M @ M.T ≈ identité`) : ~4e-08 d'erreur
  avec ce layout contre ~1e51 (garbage) avec big-endian ou le bit-trick
  zigzag. Sur `battleground_animation_pack`, orthonormalité **parfaite
  (erreur max = 0.0000)** sur les 5052 matrices non-identité du fichier.

### Limite connue, non résolue

La partie POSITION des tableaux `CFrame`/`Vector3` de **grande taille**
(`Pose.CFrame`, ~5900 instances) contient une fraction significative
(~15-35 %) de valeurs manifestement fausses (magnitudes absurdes, ex.
`-50331644.0` studs). Le décompte total d'octets tombe exactement juste
(zéro reliquat), ce qui exclut un désalignement — cause exacte non
identifiée après plusieurs heures d'investigation (zigzag simple, cumsum,
XOR-chain testés, aucun ne corrige tous les cas). **Ne pas faire confiance
aux positions issues de grands tableaux CFrame sans filtrage de
plausibilité** (`|valeur| > ~50 studs` = suspect). La ROTATION, elle,
reste fiable (validée à part, indépendante du bug de position).

### Dépendances

`pip install lz4 numpy` (le venv `experiments/r6_aerial_kick_combo/.venv`
les a déjà).

### Usage

```python
import rbxm_reader as R
classes, chunks = R.inventory("mon_pack.rbxm")          # inventaire classes
props = R.parse_prop_chunks(chunks, classes)              # String/Bool/Int32/Float32
parent_of = R.parse_prnt_chunk(chunks)                     # hierarchie
res = R.parse_prop_extended(chunks, classes,
        {("Pose", "CFrame"): "cframe"})                    # CFrame/NumberSequence/...
```
