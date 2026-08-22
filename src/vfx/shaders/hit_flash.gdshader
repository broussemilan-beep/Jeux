shader_type canvas_item;
// Flash blanc côté cible (mandat production v1 §4, HitResponse) — mélange
// vers du blanc plein proportionnellement à `flash_amount`, jamais un
// remplacement de couleur qui perdrait l'alpha du sprite (silhouette
// toujours correcte, seule la teinte change).
//
// BUG CORRIGÉ (rapport Milan, captures réelles du 2026-08-22) : la version
// précédente ré-échantillonnait `texture(TEXTURE, UV)` elle-même. Pour un
// AnimatedSprite2D (texture réelle), ça marchait. Pour un `Polygon2D` sans
// texture assignée (le mannequin générique d'Enemy ET boss_gate_maw.tscn,
// TOUS DEUX présents dans les scènes de jeu réelles, pas seulement des
// mannequins de test) — Godot lie `TEXTURE` à sa texture blanche 1x1 par
// défaut quand aucune n'est assignée, donc `tex.rgb`/`tex.a` valaient
// TOUJOURS (1,1,1,1), quel que soit `flash_amount` : un rectangle blanc
// opaque plein, jamais la couleur réelle du polygone, jamais un fondu —
// exactement les "rectangles blancs flottants" des captures. `COLOR` en
// entrée de fragment() est DÉJÀ pré-rempli par Godot avec le résultat
// correct pour CE nœud (texture×modulate pour un sprite, couleur de
// vertex×modulate pour un Polygon2D sans texture) — le lire au lieu de
// re-échantillonner `TEXTURE` à la main corrige les deux cas d'un coup,
// sans branche `if` ni changement de comportement pour les sprites déjà
// corrects.

// BUG RÉEL CONFIRMÉ (retour Milan, "MANDAT ROUND 2", 2026-08-22, CHANTIER
// 1) : rejoué --enemy_scene=enemy_brute.tscn (vrai AnimatedSprite2D, pas
// le Placeholder de test) sur le MÊME pouvoir/tick que les captures
// signalées — le même carré blanc plein apparaît, à l'identique, sur la
// vraie créature. Donc PAS un artefact du rig de capture (ÉTAPE 1 du
// mandat) : le fix ci-dessus (TEXTURE->COLOR) était nécessaire mais pas
// suffisant, un second bug distinct restait dessous.
//
// Cause précise : `flash_amount` parvient bien à 1.0 puis décroît sur
// HitResponse.FLASH_TICKS (4) — MAIS HitResponse._physics_process() ne
// décrémente ce compteur que si `not CombatFeedback.is_frozen()`
// (délibéré, combat_feedback.gd : une minuterie cosmétique "reste
// synchrone avec l'impact"). Or le hit-stop "medium" (Bras-Faux/Poing
// Belluaire, TARGET_HITSTOP_MS) dure ~4 ticks lui aussi — quasi le même
// nombre que FLASH_TICKS. Pendant TOUTE cette fenêtre gelée,
// `flash_amount` reste ÉPINGLÉ à 1.0 (jamais décrémenté), donc `mix(...,
// 1.0)` == blanc opaque PLEIN sans AUCUNE trace de la couleur/texture
// réelle — pas un bref flash d'un tick, un vrai "trou blanc" qui tient
// toute la durée du gel (~65ms, largement perceptible), day exactement
// au moment où le jeu veut montrer l'impact le plus clairement. Ce
// module violait aussi une règle déjà posée ailleurs dans ce projet
// (impact_flash_frame.gd, MAX_VALUE_HSV=0.92, §3 : "jamais blanc pur,
// V=100%, collision UI/décor") — seul ce shader-ci allait jusqu'à 1.0.
//
// Fix : plafonner la CONTRIBUTION effective du mélange (MAX_FLASH_MIX),
// pas juste sa cible — à `flash_amount`=1.0 (pic), la cible garde encore
// 1-MAX_FLASH_MIX de sa propre couleur/lisibilité au lieu de disparaître
// entièrement sous un aplat uni, gelé ou non. Valeur choisie par lecture
// visuelle directe (captures avant/après, pas un calcul) : assez haute
// pour rester un VRAI flash qui se voit, assez basse pour ne jamais
// effacer complètement la silhouette/texture de la cible.
const float MAX_FLASH_MIX = 0.6;

uniform float flash_amount : hint_range(0.0, 1.0) = 0.0;

void fragment() {
	COLOR = vec4(mix(COLOR.rgb, vec3(1.0, 1.0, 1.0), flash_amount * MAX_FLASH_MIX), COLOR.a);
}
