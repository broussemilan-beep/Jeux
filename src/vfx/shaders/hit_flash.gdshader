shader_type canvas_item;
// Flash blanc côté cible (mandat production v1 §4, HitResponse) — mélange
// vers du blanc plein proportionnellement à `flash_amount`, jamais un
// remplacement de couleur qui perdrait l'alpha du sprite (silhouette
// toujours correcte, seule la teinte change).

uniform float flash_amount : hint_range(0.0, 1.0) = 0.0;

void fragment() {
	vec4 tex = texture(TEXTURE, UV);
	COLOR = vec4(mix(tex.rgb, vec3(1.0, 1.0, 1.0), flash_amount), tex.a);
}
