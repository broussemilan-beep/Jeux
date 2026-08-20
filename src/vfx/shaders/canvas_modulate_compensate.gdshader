shader_type canvas_item;
// MANDAT NUIT phase 1 — un CanvasModulate d'ambiance chaude teinte
// TOUT le canvas, y compris Rank Zero, qui doit rester seule en
// grayscale désaturé (contraste narratif, Classe = NONE). Comme
// CanvasModulate multiplie le rendu final de chaque CanvasItem après
// son propre shader, diviser ici par la même couleur avant la
// multiplication annule exactement la teinte reçue : (COLOR / C) * C
// = COLOR. Le uniform doit être tenu synchronisé avec la couleur du
// CanvasModulate de la scène parente (documenté à l'endroit où il est
// posé) — pas de découverte dynamique, juste un contre-poids scoped.

uniform vec3 compensate_color : source_color = vec3(1.0, 1.0, 1.0);

void fragment() {
	vec4 tex = texture(TEXTURE, UV);
	vec3 safe = max(compensate_color, vec3(0.001));
	COLOR = vec4(tex.rgb / safe, tex.a);
}
