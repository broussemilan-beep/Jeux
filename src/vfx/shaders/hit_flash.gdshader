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

uniform float flash_amount : hint_range(0.0, 1.0) = 0.0;

void fragment() {
	COLOR = vec4(mix(COLOR.rgb, vec3(1.0, 1.0, 1.0), flash_amount), COLOR.a);
}
