shader_type canvas_item;
// Combine outlineSelective + directionalStreak (Phase 2.3, MANDAT SUITE v2)
// sur UN SEUL sprite (Player) — un CanvasItem n'a qu'un slot `material`,
// les deux effets doivent cohabiter dans le meme shader plutot que
// d'inventer un mecanisme de composition de materiaux. outline_enabled
// reste vrai en permanence (allie = bleu, §10.1) ; streak_amount reste a
// 0 hors dash (jamais permanent, meme discipline que directional_streak.
// gdshader standalone utilise par Enemy).
//
// Le sample du streak est ecrit en ligne dans fragment() : le passer par
// une fonction annexe recevant TEXTURE en argument declenche une erreur
// de compilation ("Unknown identifier in expression: 'TEXTURE'" si le nom
// magique est lu depuis l'interieur de la fonction, sinon un warning
// "custom_samplers" du compilateur RD lorsqu'il est passe en parametre) —
// les variables magiques (TEXTURE/UV/COLOR) ne sont fiables que dans le
// corps de fragment() lui-meme en Godot Shading Language.

// Phase R4 (retour croisé Gemini/ChatGPT, MANDAT SUITE v2, verifie par
// capture zoomee reelle avant retouche — tools/capture_scene.tscn
// --mode=player_action) : a alpha=1.0/largeur=1.0, le contour couvrait
// TOUT le contour du sprite en bleu plein des qu'un pixel voisin est
// semi-transparent (pas de degrade), ce qui, sur un petit sprite
// remonte a l'echelle du jeu, saturait la silhouette grise en un bloc
// bleu neon au lieu d'un simple trait fin (§10.1 : allie = bleu, jamais
// une recoloration). Alpha et largeur reduits — reste un vrai contour
// visible, jamais un trait invisible.
uniform vec4 outline_color : source_color = vec4(0.3, 0.55, 1.0, 0.6);
uniform float outline_width_px : hint_range(0.0, 4.0) = 0.6;
uniform bool outline_enabled = true;

uniform vec2 streak_direction = vec2(1.0, 0.0);
uniform float streak_amount : hint_range(0.0, 1.0) = 0.0;
uniform int streak_samples : hint_range(1, 8) = 5;

void fragment() {
	vec4 tex = texture(TEXTURE, UV);
	if (streak_amount > 0.0) {
		vec2 dir = normalize(streak_direction + vec2(0.00001)) * streak_amount * 0.05;
		vec4 accum = tex;
		float total = 1.0;
		for (int i = 1; i <= streak_samples; i++) {
			float t = float(i) / float(streak_samples);
			vec4 s = texture(TEXTURE, UV - dir * t);
			float w = 1.0 - t;
			accum += s * w;
			total += w;
		}
		tex = accum / total;
	}
	COLOR = tex;
	// Godot Shading Language n'autorise pas `return` dans fragment() —
	// early-exit remplace par un if imbrique.
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
