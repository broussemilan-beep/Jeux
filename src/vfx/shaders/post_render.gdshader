shader_type canvas_item;
// Post-render global (Phase 2.3, MANDAT SUITE v2 — docs/ARCHITECTURE_VFX_v3.md
// §10.1) : emissiveBloom + paletteRamp fusionnes en UNE SEULE passe (regle
// mobile imperative §10.1 : "emissiveBloom = une seule passe de post-render
// globale par frame, jamais une passe par VFX" — les fusionner ici respecte
// la contrainte sans sacrifier paletteRamp). Pose sur un ColorRect plein
// ecran, meme convention que Vignette (CanvasLayer dedie, sous Vignette/HUD
// dans l'ordre de la scene).

uniform sampler2D screen_texture : hint_screen_texture, filter_nearest;
uniform float bloom_threshold : hint_range(0.0, 1.0) = 0.72;
uniform float bloom_intensity : hint_range(0.0, 2.0) = 0.6;
uniform float ramp_steps : hint_range(2.0, 16.0) = 6.0;
uniform float value_band_min : hint_range(0.0, 1.0) = 0.05;
uniform float value_band_max : hint_range(0.0, 1.0) = 0.98;

vec3 rgb_to_hsv(vec3 c) {
	vec4 k = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
	vec4 p = mix(vec4(c.bg, k.wz), vec4(c.gb, k.xy), step(c.b, c.g));
	vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
	float d = q.x - min(q.w, q.y);
	float e = 1.0e-10;
	return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv_to_rgb(vec3 c) {
	vec4 k = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
	vec3 p = abs(fract(c.xxx + k.xyz) * 6.0 - k.www);
	return c.z * mix(k.xxx, clamp(p - k.xxx, 0.0, 1.0), c.y);
}

void fragment() {
	vec4 base = texture(screen_texture, SCREEN_UV);

	// emissiveBloom : bright-pass + 4 echantillons diagonaux fixes — pas un
	// vrai flou gaussien multi-passe (cout mobile interdit ici), une
	// approximation "poor man's bloom" suffit pour le halo attendu sur les
	// zones deja tres claires (flashs d'impact, highlights).
	vec2 texel = SCREEN_PIXEL_SIZE * 2.0;
	vec3 bloom = vec3(0.0);
	vec2 offsets[4] = vec2[](vec2(1.0, 1.0), vec2(-1.0, 1.0), vec2(1.0, -1.0), vec2(-1.0, -1.0));
	for (int i = 0; i < 4; i++) {
		vec3 s = texture(screen_texture, SCREEN_UV + offsets[i] * texel).rgb;
		float lum = dot(s, vec3(0.299, 0.587, 0.114));
		bloom += s * smoothstep(bloom_threshold, 1.0, lum);
	}
	bloom *= 0.25 * bloom_intensity;
	vec3 color = base.rgb + bloom;

	// paletteRamp : verrouille le rendu final sur la meme bande de Value
	// deja etablie pour les sprites (quantize.py, value_band_min/max) —
	// l'ecran entier suit la meme discipline "jamais 0% ni 100%" (§3),
	// pas seulement les sprites pris individuellement.
	vec3 hsv = rgb_to_hsv(color);
	hsv.z = clamp(hsv.z, value_band_min, value_band_max);
	hsv.z = floor(hsv.z * ramp_steps) / ramp_steps;
	color = hsv_to_rgb(vec3(hsv.x, hsv.y, hsv.z));

	COLOR = vec4(color, base.a);
}
