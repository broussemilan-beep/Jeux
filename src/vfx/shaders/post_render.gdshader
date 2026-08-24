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
uniform float ramp_steps : hint_range(2.0, 16.0) = 10.0;
uniform float value_band_min : hint_range(0.0, 1.0) = 0.05;
// Plafond de posterize pour un pixel "point-lumiere/vfx actif" (cf. la note
// deja ecrite pour la bande "character" dans data/palettes/value_bands.json :
// "le coeur direct d'une source de lumiere ... traite comme un point-lumiere/
// vfx actif, pas comme du decor plat"). Applique quand bright_mask ~ 1.
uniform float value_band_max : hint_range(0.0, 1.0) = 0.98;
// Plafond de posterize pour tout le reste ("decor plat" — sol, murs, materiau
// non-emissif). Corrige le defaut de sursaturation (docs/STATUS.md,
// "Plafond de bande decor systematiquement depasse pres de toute source de
// lumiere") : sans ce 2e plafond, ramp_steps=6 poussait TOUT pixel deja
// clair (sol sous un halo de PointLight2D, pas seulement la flamme) au
// palier haut fixe (~83% V), au-dessus de la bande decor [15,78].
uniform float value_band_max_flat : hint_range(0.0, 1.0) = 0.76;
// Seuil de luminance (pixel BRUT, avant bloom de cette passe) au-dela duquel
// un pixel est considere "coeur de source active" plutot que "decor eclaire"
// — volontairement haut (voir commentaire dans fragment()).
uniform float active_luma_threshold : hint_range(0.0, 1.0) = 0.95;

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
	//
	// bright_mask distingue le coeur d'une source active (flamme elle-meme,
	// flash VFX quasi blanc) du reste — MEME un sol largement eclaire par
	// son halo. Volontairement un seuil tres haut (active_luma_threshold,
	// pas bloom_threshold) : bloom_threshold (0.72) sert a decider QUOI
	// rayonne (halo large, discipline visuelle), pas a decider QUOI est
	// exempte de la discipline de bande decor (question differente — un
	// seuil bas ici avait l'effet inverse du but recherche : le halo,
	// deja elargi par le bloom lui-meme, se qualifiait "actif" sur une
	// zone bien plus large que la flamme, aggravant le defaut au lieu de
	// le corriger). Lu sur `base` (le pixel BRUT, avant l'ajout du bloom
	// de cette passe) pour ne pas boucler sur sa propre contribution.
	float scene_lum = dot(base.rgb, vec3(0.299, 0.587, 0.114));
	float bright_mask = smoothstep(active_luma_threshold, active_luma_threshold + 0.05, scene_lum);
	float local_value_band_max = mix(value_band_max_flat, value_band_max, bright_mask);

	vec3 hsv = rgb_to_hsv(color);
	hsv.z = clamp(hsv.z, value_band_min, local_value_band_max);
	hsv.z = floor(hsv.z * ramp_steps) / ramp_steps;
	color = hsv_to_rgb(vec3(hsv.x, hsv.y, hsv.z));

	COLOR = vec4(color, base.a);
}
