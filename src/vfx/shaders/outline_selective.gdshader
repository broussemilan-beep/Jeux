shader_type canvas_item;
// outlineSelective (Phase 2.3, MANDAT SUITE v2 — docs/ARCHITECTURE_VFX_v3.md
// §10.1) : contour par equipe (bleu allie / rouge ennemi / couleur cible).
// Materiau POSE SUR LE SPRITE lui-meme (AnimatedSprite2D), jamais un
// post-render global — ce n'est pas "toute la scene", juste CE sprite.
// Detection de bord classique : un pixel transparent dont un voisin
// immediat est opaque devient la couleur de contour.

uniform vec4 outline_color : source_color = vec4(0.3, 0.55, 1.0, 1.0);
uniform float outline_width_px : hint_range(0.0, 4.0) = 1.0;
uniform bool outline_enabled = true;

void fragment() {
	vec4 tex = texture(TEXTURE, UV);
	COLOR = tex;
	// Godot Shading Language n'autorise pas `return` dans fragment() — un
	// seul if imbriqué remplace l'early-exit, pas une limitation GLSL
	// standard mais propre a ce langage.
	if (outline_enabled && tex.a <= 0.5) {
		vec2 texel = outline_width_px * TEXTURE_PIXEL_SIZE;
		float neighbor_alpha = 0.0;
		neighbor_alpha += texture(TEXTURE, UV + vec2(texel.x, 0.0)).a;
		neighbor_alpha += texture(TEXTURE, UV - vec2(texel.x, 0.0)).a;
		neighbor_alpha += texture(TEXTURE, UV + vec2(0.0, texel.y)).a;
		neighbor_alpha += texture(TEXTURE, UV - vec2(0.0, texel.y)).a;
		if (neighbor_alpha > 0.0) {
			COLOR = outline_color;
		}
	}
}
