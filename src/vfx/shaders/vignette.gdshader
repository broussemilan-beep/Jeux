shader_type canvas_item;
// Vignette d'ambiance (mandat production v1 §6, F "Le monde") — assombrit
// les bords de l'écran en dégradé radial, une seule passe, jamais de blur
// coûteux (§10 "Règle mobile impérative... une seule passe de post-render
// globale par frame"). Posé sur un ColorRect plein écran : `UV` couvre déjà
// exactement le viewport (0..1), pas besoin de SCREEN_UV/SCREEN_TEXTURE —
// ce n'est pas une distorsion de ce qui est dessiné dessous, juste une
// teinte semi-transparente par-dessus (COLOR.a porte tout le dégradé).

uniform float strength : hint_range(0.0, 1.0) = 0.35;
uniform float inner_radius : hint_range(0.0, 1.0) = 0.35;
uniform float outer_radius : hint_range(0.0, 1.5) = 0.9;
uniform vec3 vignette_color : source_color = vec3(0.0, 0.0, 0.0);
// §0 : viewport natif 640x360 — sans ce facteur d'aspect le dégradé
// serait ovale (étiré en largeur) au lieu de circulaire.
uniform float aspect_ratio : hint_range(0.5, 3.0) = 1.7778;

void fragment() {
	vec2 centered = UV - vec2(0.5);
	centered.x *= aspect_ratio;
	float dist = length(centered);
	float darken = smoothstep(inner_radius, outer_radius, dist) * strength;
	COLOR = vec4(vignette_color, darken);
}
