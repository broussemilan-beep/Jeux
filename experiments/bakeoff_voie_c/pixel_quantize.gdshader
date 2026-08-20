shader_type canvas_item;
// Bake-off Animation, Voie C (mandat "BAKE-OFF ANIMATION — 3 voies").
//
// Technique de pixelisation/quantification/dithering/contour ADAPTÉE de
// PixelArt.gdshader, projet GodotPixelRenderer (github.com/bukkbeek/
// GodotPixelRenderer), licence MIT, Copyright (c) 2025 Bukkbeek. Cet outil
// est une appli GUI Godot 4.4+ pilotée à la souris (pas de mode headless/
// CLI, confirmé par lecture du dépôt) — inutilisable tel quel dans notre
// pipeline headless (xvfb+vulkan) ni avec notre Godot 4.3. Reprise du
// SHADER seul (licence MIT = réutilisation libre), pas de l'application.
//
// Différences avec l'original :
//   - palette 8 couleurs fixes retirée : notre "palette" n'est pas 8
//     teintes figées mais une bande de Value HSV (data/palettes/
//     value_bands.json, catégorie "character" : V dans [15,90]%) + une
//     désaturation quasi totale (GDD : "grayscale désaturé"). Remplacée
//     par un uniform `target_saturation` (quasi 0) appliqué avant la
//     quantification de pas (`quantize_color`, conservée telle quelle).
//   - reste (pixelisation par blocs, dithering Bayer 4x4 sur les zones de
//     transition ombre/lumière, contour par détection de bords Sobel) :
//     conservé à l'identique, seul le nom des uniforms a été gardé.

uniform int target_x_pixel_count : hint_range(8, 256) = 64;
uniform int target_y_pixel_count : hint_range(8, 256) = 64;

uniform int color_steps : hint_range(2, 32) = 8;
uniform float target_saturation : hint_range(0.0, 1.0) = 0.12;
// Bande de Value légale (data/palettes/value_bands.json, catégorie
// "character" : V dans [15,90]%) — les paliers de quantification sont
// remappés DANS cette bande (voir fragment()), pas [0,1] : sinon un
// palier proche de 0 tombe sous le plancher, et un pixel totalement à
// l'ombre peut quantifier à V=0% pur, toujours hors bande.
// 0.165, pas 0.15 pile : à V=0.15 exact, l'arrondi PNG 8-bit (0.15*255=38.25
// -> 38) redonne 38/255=14.9% une fois relu — juste SOUS le plancher par
// un artefact d'arrondi, pas par un vrai dépassement de bande. Marge de
// sécurité pour rester ≥15% après export, quel que soit le sens d'arrondi.
uniform float value_band_min : hint_range(0.0, 1.0) = 0.165;
uniform float value_band_max : hint_range(0.0, 1.0) = 0.90;

uniform float edge_strength : hint_range(0.0, 2.0) = 0.35;
uniform float outline_thickness : hint_range(0.0, 20.0) = 3.0;
// V >= 15% (data/palettes/value_bands.json, catégorie "character") : pas
// d'exception "contour sombre" documentée pour cette catégorie (contrairement
// à "ui"), donc le contour doit rester dans la bande comme le reste.
uniform vec4 outline_color : source_color = vec4(0.17, 0.17, 0.185, 1.0);

uniform float dither_amount : hint_range(0.0, 1.0) = 0.35;
uniform float dither_blend : hint_range(0.0, 1.0) = 0.6;
uniform float dither_threshold : hint_range(0.0, 1.0) = 0.5;
uniform float shadow_sensitivity : hint_range(0.1, 2.0) = 1.0;
uniform vec4 dither_color : source_color = vec4(0.17, 0.17, 0.185, 1.0);

vec3 rgb_to_hsv(vec3 c) {
	vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
	vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
	vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
	float d = q.x - min(q.w, q.y);
	float e = 1.0e-10;
	return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv_to_rgb(vec3 c) {
	vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
	vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
	return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

vec3 quantize_color(vec3 color) {
	float step_size = 1.0 / float(color_steps - 1);
	return floor(color / step_size) * step_size;
}

vec3 detect_edges(sampler2D tex, vec2 uv, vec2 tex_size) {
	vec2 texel = 1.0 / tex_size;
	vec3 tl = texture(tex, uv + vec2(-texel.x, -texel.y)).rgb;
	vec3 tc = texture(tex, uv + vec2(0.0, -texel.y)).rgb;
	vec3 tr = texture(tex, uv + vec2(texel.x, -texel.y)).rgb;
	vec3 ml = texture(tex, uv + vec2(-texel.x, 0.0)).rgb;
	vec3 mr = texture(tex, uv + vec2(texel.x, 0.0)).rgb;
	vec3 bl = texture(tex, uv + vec2(-texel.x, texel.y)).rgb;
	vec3 bc = texture(tex, uv + vec2(0.0, texel.y)).rgb;
	vec3 br = texture(tex, uv + vec2(texel.x, texel.y)).rgb;
	vec3 gx = -tl + tr - 2.0 * ml + 2.0 * mr - bl + br;
	vec3 gy = -tl - 2.0 * tc - tr + bl + 2.0 * bc + br;
	return sqrt(gx * gx + gy * gy);
}

float get_bayer_matrix(ivec2 pos) {
	int bayer[16] = int[16](
		0,  8,  2,  10,
		12, 4,  14, 6,
		3,  11, 1,  9,
		15, 7,  13, 5
	);
	int x = pos.x % 4;
	int y = pos.y % 4;
	return float(bayer[y * 4 + x]) / 15.0;
}

vec3 detect_shadow_transitions(sampler2D tex, vec2 uv, vec2 tex_size) {
	vec2 texel = 1.0 / tex_size;
	vec3 center = texture(tex, uv).rgb;
	vec3 right = texture(tex, uv + vec2(texel.x, 0.0)).rgb;
	vec3 down = texture(tex, uv + vec2(0.0, texel.y)).rgb;
	vec3 left = texture(tex, uv + vec2(-texel.x, 0.0)).rgb;
	vec3 up = texture(tex, uv + vec2(0.0, -texel.y)).rgb;
	float lum_center = dot(center, vec3(0.299, 0.587, 0.114));
	float lum_right = dot(right, vec3(0.299, 0.587, 0.114));
	float lum_down = dot(down, vec3(0.299, 0.587, 0.114));
	float lum_left = dot(left, vec3(0.299, 0.587, 0.114));
	float lum_up = dot(up, vec3(0.299, 0.587, 0.114));
	float grad_x = abs(lum_right - lum_left) * 0.5;
	float grad_y = abs(lum_down - lum_up) * 0.5;
	return vec3(sqrt(grad_x * grad_x + grad_y * grad_y), lum_center, 0.0);
}

vec3 apply_dithering(vec3 color, vec2 screen_pos, sampler2D tex, vec2 uv, vec2 tex_size) {
	if (dither_amount <= 0.0) {
		return color;
	}
	vec3 transition_data = detect_shadow_transitions(tex, uv, tex_size);
	float gradient_strength = transition_data.x;
	float luminance = transition_data.y;
	float transition_factor = smoothstep(0.05, 0.2, gradient_strength * shadow_sensitivity);
	if (transition_factor < 0.01) {
		return color;
	}
	ivec2 pixel_pos = ivec2(floor(screen_pos));
	float bayer_value = get_bayer_matrix(pixel_pos);
	float threshold = dither_threshold + (bayer_value - 0.5) * dither_amount;
	float is_dot = step(threshold, luminance);
	vec3 dot_color = mix(dither_color.rgb, color * 1.2, luminance);
	vec3 dithered = mix(dot_color, color, is_dot);
	return mix(color, dithered, transition_factor * dither_blend);
}

void fragment() {
	vec2 texture_size = vec2(textureSize(TEXTURE, 0));

	vec2 pixel_uv = UV;
	float scale_x = texture_size.x / float(target_x_pixel_count);
	float scale_y = texture_size.y / float(target_y_pixel_count);
	float scale_factor = max(scale_x, scale_y);
	if (scale_factor > 1.0) {
		vec2 pixel_size = vec2(scale_factor) / texture_size;
		pixel_uv = floor(UV / pixel_size) * pixel_size + pixel_size * 0.5;
	}

	vec4 tex_color = texture(TEXTURE, pixel_uv);
	vec3 color = tex_color.rgb;

	// Quantifier le Value APRÈS désaturation (pas les 3 canaux RGB
	// indépendamment, `quantize_color` de l'original) : sur une couleur
	// quasi neutre (target_saturation proche de 0), un floor() séparé
	// par canal R/G/B peut arrondir chacun vers un palier différent —
	// un bruit de teinte visible (bandes roses/mauves) sur un gris
	// censé rester gris. Quantifier V seul, puis reconvertir, garantit
	// R=G=B (donc un vrai gris) à chaque palier.
	vec3 hsv = rgb_to_hsv(color);
	hsv.y = target_saturation;
	if (color_steps < 32) {
		float step_size = 1.0 / float(color_steps - 1);
		float step_index = floor(hsv.z / step_size);
		float v_norm = step_index * step_size;
		hsv.z = mix(value_band_min, value_band_max, v_norm);
	}
	color = hsv_to_rgb(hsv);

	if (outline_thickness > 0.0) {
		vec3 edges = detect_edges(TEXTURE, pixel_uv, texture_size);
		float edge_strength_calc = length(edges);
		if (edge_strength_calc > edge_strength) {
			float outline_intensity = clamp(outline_thickness / 10.0, 0.0, 1.0);
			color = mix(color, outline_color.rgb, outline_intensity);
		}
	}

	vec2 screen_pos = pixel_uv * texture_size;
	color = apply_dithering(color, screen_pos, TEXTURE, pixel_uv, texture_size);

	color = clamp(color, 0.0, 1.0);
	COLOR = vec4(color, tex_color.a);
}
