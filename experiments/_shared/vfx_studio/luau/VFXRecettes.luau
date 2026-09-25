--!nonstrict
-- GÉNÉRÉ par vfx_studio/compile_roblox.py : ne pas éditer à la main.
-- Recettes VFX compilées (NumberSequence de 0 à 1, <= 20 points ; couleurs 0-1).
return {
	recettes = {
		orbe_impact = {
			nom = "orbe_impact",
			titre = "Orbe : apparition, projection, collision",
			duree = 2.6,
			graine = 7,
			palette = {
				"#fff4d6",
				"#ffb23e",
				"#ff5a1f",
			},
			flashs = {
				{
					t0 = 0.8,
					duree = 0.035,
					couleur = "#fff6e0",
					transparency = {
						{0, 0.1},
						{1, 0.9},
					},
				},
			},
			secousses = {
				{
					t0 = 0.8,
					duree = 0.35,
					amplitude = 0.55,
					direction = {0, -1, -0.6},
					graine = 3,
				},
			},
			gels = {
				{0.8, 0.06},
			},
			sons = {
				{
					son = "naissance_orbe",
					t0 = 0,
					volume = 0.45,
				},
				{
					son = "aspiration",
					t0 = 0,
					volume = 0.55,
				},
				{
					son = "souffle_projectile",
					t0 = 0.3,
					volume = 0.75,
				},
				{
					son = "impact_lourd",
					t0 = 0.8,
					volume = 0.85,
					impact = true,
				},
				{
					son = "grondement",
					t0 = 0.81,
					volume = 0.5,
				},
				{
					son = "vent_arc",
					t0 = 0.83,
					volume = 0.35,
				},
			},
			couches = {
				{
					type = "mesh",
					nom = "naissance",
					t0 = 0,
					duree = 0.3,
					ancre = {
						pos = {0, 3.2, 7},
					},
					mesh = "sphere",
					texture = "bruit_energie",
					defilement = {1.6, 0},
					echelle = {
						{
							0,
							{0, 0, 0},
						},
						{
							0.6,
							{1.2, 1.2, 1.2},
						},
						{
							1,
							{0.9, 0.9, 0.9},
						},
					},
					color = {
						{
							0,
							{1, 0.698, 0.2431},
						},
						{
							1,
							{1, 0.698, 0.2431},
						},
					},
					brightness = 1.8,
					bord = 0.6,
					transparency = {
						{0, 0, 0},
						{1, 0, 0},
					},
					light_emission = 1,
				},
				{
					type = "particules",
					nom = "naissance_etoile",
					t0 = 0,
					ancre = {
						pos = {0, 3.2, 7},
					},
					texture = "etoile4",
					emit = 1,
					lifetime = {0.3, 0.3},
					size = {
						{0, 0, 0},
						{0.4, 6, 0},
						{1, 0, 0},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.9569, 0.8392},
						},
					},
					light_emission = 1,
					transparency = {
						{0, 0, 0},
						{1, 0, 0},
					},
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					speed = {0, 0},
					rotation = {0, 0},
					rotspeed = {0, 0},
					spread = {0, 0},
					accel = {0, 0, 0},
				},
				{
					type = "particules",
					nom = "aspiration",
					t0 = 0,
					ancre = {
						pos = {0, 3.2, 7},
					},
					texture = "eclat",
					rate = 90,
					duree_emission = 0.28,
					lifetime = {0.18, 0.25},
					speed = {-26, -18},
					spread = {180, 180},
					orientation = "VelocityParallel",
					size = {
						{0, 1.2, 0},
						{1, 0.3, 0},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.9569, 0.8392},
						},
					},
					light_emission = 1,
					forme = {
						sphere = 4,
					},
					transparency = {
						{0, 0, 0},
						{1, 0, 0},
					},
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					rotation = {0, 0},
					rotspeed = {0, 0},
					accel = {0, 0, 0},
				},
				{
					type = "mesh",
					nom = "coquille",
					t0 = 0.3,
					duree = 0.5,
					ancre = "projectile",
					mesh = "sphere",
					texture = "bruit_energie",
					defilement = {2.4, 0},
					echelle = {
						{
							0,
							{1.35, 1.35, 1.35},
						},
						{
							1,
							{1.35, 1.35, 1.35},
						},
					},
					color = {
						{
							0,
							{1, 0.698, 0.2431},
						},
						{
							1,
							{1, 0.698, 0.2431},
						},
					},
					brightness = 1.6,
					bord = 0.8,
					transparency = {
						{0, 0, 0},
						{1, 0, 0},
					},
					light_emission = 1,
				},
				{
					type = "particules",
					nom = "halo_orbe",
					t0 = 0.3,
					ancre = "projectile",
					texture = "halo",
					rate = 60,
					duree_emission = 0.5,
					lifetime = {0.06, 0.06},
					size = {
						{0, 5.5, 0},
						{1, 5, 0},
					},
					transparency = {
						{0, 0.35, 0},
						{1, 0.6, 0},
					},
					color = {
						{
							0,
							{1, 0.698, 0.2431},
						},
						{
							1,
							{1, 0.698, 0.2431},
						},
					},
					light_emission = 1,
					bloque_a_l_ancre = true,
					gel = false,
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					speed = {0, 0},
					rotation = {0, 0},
					rotspeed = {0, 0},
					spread = {0, 0},
					accel = {0, 0, 0},
				},
				{
					type = "trail",
					nom = "trainee",
					t0 = 0.3,
					t1 = 0.8,
					ancre = "projectile",
					lifetime = 0.22,
					t1_ancre = 0.8,
					largeur = {
						{0, 1.6, 0},
						{1, 0, 0},
					},
					texture = "ruban",
					segments = 24,
					transparency = {
						{0, 0, 0},
						{1, 1, 0},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.3529, 0.1216},
						},
					},
					light_emission = 1,
				},
				{
					type = "particules",
					nom = "semis",
					t0 = 0.3,
					ancre = "projectile",
					texture = "eclat",
					rate = 90,
					duree_emission = 0.5,
					lifetime = {0.15, 0.3},
					speed = {2, 6},
					spread = {180, 180},
					drag = 4,
					orientation = "FacingCamera",
					size = {
						{0, 0.7, 0},
						{1, 0, 0},
					},
					color = {
						{
							0,
							{1, 0.698, 0.2431},
						},
						{
							1,
							{1, 0.698, 0.2431},
						},
					},
					light_emission = 1,
					bloque_a_l_ancre = false,
					transparency = {
						{0, 0, 0},
						{1, 0, 0},
					},
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					rotation = {0, 0},
					rotspeed = {0, 0},
					accel = {0, 0, 0},
				},
				{
					type = "particules",
					nom = "flash",
					t0 = 0.8,
					ancre = "impact",
					texture = "flash",
					emit = 1,
					lifetime = {0.07, 0.07},
					size = {
						{0, 9, 0},
						{1, 12, 0},
					},
					transparency = {
						{0, 0, 0},
						{0.6, 0.2, 0},
						{1, 1, 0},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.9569, 0.8392},
						},
					},
					light_emission = 1,
					rotation = {0, 360},
					zoffset = 2,
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					speed = {0, 0},
					rotspeed = {0, 0},
					spread = {0, 0},
					accel = {0, 0, 0},
				},
				{
					type = "particules",
					nom = "etoile",
					t0 = 0.8,
					ancre = "impact",
					texture = "etoile4",
					emit = 1,
					lifetime = {0.16, 0.16},
					size = {
						{0, 14, 0},
						{1, 4, 0},
					},
					transparency = {
						{0, 0, 0},
						{1, 1, 0},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.9569, 0.8392},
						},
					},
					light_emission = 1,
					zoffset = 2.5,
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					speed = {0, 0},
					rotation = {0, 0},
					rotspeed = {0, 0},
					spread = {0, 0},
					accel = {0, 0, 0},
				},
				{
					type = "mesh",
					nom = "dome",
					t0 = 0.81,
					duree = 0.32,
					ancre = "impact",
					mesh = "dome",
					texture = "bruit_energie",
					defilement = {0.8, 0},
					echelle = {
						{
							0,
							{0.6, 0.6, 0.6},
						},
						{
							0.35,
							{4.5, 4.5, 4.5},
						},
						{
							1,
							{6.5, 6.5, 6.5},
						},
					},
					transparency = {
						{0, 0.05, 0},
						{0.5, 0.45, 0},
						{1, 1, 0},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.9569, 0.8392},
						},
					},
					bord = 1,
					light_emission = 1,
				},
				{
					type = "mesh",
					nom = "anneau_sol",
					t0 = 0.8,
					duree = 0.42,
					ancre = "impact",
					mesh = "anneau_plat",
					texture = "ruban",
					echelle = {
						{
							0,
							{0.8, 0.8, 0.8},
						},
						{
							0.4,
							{6, 6, 6},
						},
						{
							1,
							{9, 9, 9},
						},
					},
					transparency = {
						{0, 0, 0},
						{0.6, 0.5, 0},
						{1, 1, 0},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.9569, 0.8392},
						},
					},
					decalage = {0, 0.05, 0},
					light_emission = 1,
				},
				{
					type = "particules",
					nom = "eclats",
					t0 = 0.8,
					ancre = "impact",
					texture = "eclat",
					emit = 28,
					lifetime = {0.22, 0.45},
					speed = {40, 75},
					spread = {180, 180},
					drag = 7,
					orientation = "VelocityParallel",
					size = {
						{0, 2.2, 0.6},
						{1, 0.2, 0},
					},
					transparency = {
						{0, 0, 0},
						{0.7, 0.1, 0},
						{1, 1, 0},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.698, 0.2431},
						},
					},
					light_emission = 1,
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					rotation = {0, 0},
					rotspeed = {0, 0},
					accel = {0, 0, 0},
				},
				{
					type = "particules",
					nom = "feu",
					t0 = 0.81,
					ancre = "impact",
					texture = "feu_cel",
					emit = 14,
					flipbook = {
						grille = 4,
						mode = "OneShot",
					},
					lifetime = {0.35, 0.6},
					speed = {16, 28},
					spread = {180, 180},
					drag = 6,
					accel = {0, 4, 0},
					size = {
						{0, 3.2, 0.8},
						{1, 5.5, 1},
					},
					transparency = {
						{0, 0, 0},
						{1, 0, 0},
					},
					color = {
						{
							0,
							{1, 1, 1},
						},
						{
							1,
							{1, 1, 1},
						},
					},
					light_emission = 0,
					rotation = {0, 360},
					rotspeed = {-60, 60},
					forme = {
						sphere = 0.6,
					},
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
				},
				{
					type = "mesh",
					nom = "vent_1",
					t0 = 0.82,
					duree = 0.3,
					ancre = "impact",
					mesh = "croissant_3d",
					texture = "bruit_energie",
					defilement = {2.2, 0},
					echelle = {
						{
							0,
							{2.2, 2.2, 2.2},
						},
						{
							1,
							{6.5, 6.5, 6.5},
						},
					},
					transparency = {
						{0, 0.1, 0},
						{0.7, 0.4, 0},
						{1, 1, 0},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.9569, 0.8392},
						},
					},
					rotation_vitesse = 520,
					rotation = 0,
					inclinaison = {18, 0, 8},
					decalage = {0, 0.6, 0},
					light_emission = 1,
				},
				{
					type = "mesh",
					nom = "vent_2",
					t0 = 0.85,
					duree = 0.3,
					ancre = "impact",
					mesh = "croissant_3d",
					texture = "bruit_energie",
					defilement = {-2, 0},
					echelle = {
						{
							0,
							{2.8, 2.8, 2.8},
						},
						{
							1,
							{7.5, 7.5, 7.5},
						},
					},
					transparency = {
						{0, 0.2, 0},
						{0.7, 0.5, 0},
						{1, 1, 0},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.9569, 0.8392},
						},
					},
					rotation_vitesse = -460,
					rotation = 140,
					inclinaison = {-24, 0, -12},
					decalage = {0, 1.2, 0},
					light_emission = 1,
				},
				{
					type = "mesh",
					nom = "vague",
					t0 = 0.82,
					duree = 0.38,
					ancre = "impact",
					mesh = "vague_sol",
					texture = "ruban",
					echelle = {
						{
							0,
							{1.5, 1.4, 1.5},
						},
						{
							1,
							{8, 0.2, 8},
						},
					},
					transparency = {
						{0, 0.15, 0},
						{1, 1, 0},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.9569, 0.8392},
						},
					},
					light_emission = 1,
				},
				{
					type = "particules",
					nom = "fumee",
					t0 = 0.84,
					ancre = "impact",
					texture = "fumee_cel",
					emit = 12,
					flipbook = {
						grille = 4,
						mode = "OneShot",
					},
					lifetime = {1, 1.6},
					speed = {7, 13},
					spread = {180, 55},
					drag = 2.2,
					accel = {0, 2.5, 0},
					size = {
						{0, 4, 1},
						{1, 8, 1.5},
					},
					transparency = {
						{0, 0, 0},
						{1, 0, 0},
					},
					color = {
						{
							0,
							{1, 1, 1},
						},
						{
							1,
							{0.7255, 0.7059, 0.6824},
						},
					},
					light_emission = 0,
					rotation = {0, 360},
					forme = {
						sphere = 1,
					},
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					rotspeed = {0, 0},
				},
			},
			projectile = {
				de = {0, 3.2, 7},
				a = {0, 1, -7},
				t0 = 0.3,
				t1 = 0.8,
				hauteur = 0.8,
				acceleration = true,
				visuel = {
					mesh = "sphere",
					echelle = {
						{
							0,
							{0.75, 0.75, 0.75},
						},
						{
							1,
							{0.75, 0.75, 0.75},
						},
					},
					color = {
						{
							0,
							{1, 0.9569, 0.8392},
						},
						{
							1,
							{1, 0.9569, 0.8392},
						},
					},
					brightness = 1.2,
					transparency = {
						{0, 0, 0},
						{1, 0, 0},
					},
					light_emission = 1,
					type = "mesh",
					t0 = 0.3,
					duree = 0.5,
					ancre = "projectile",
				},
			},
			bloom = {
				intensite = {
					{0, 0.5, 0},
					{0.3077, 0.7, 0},
					{0.3154, 1.8, 0},
					{0.4423, 0.7, 0},
					{1, 0.5, 0},
				},
				seuil = 0.72,
				taille = 2.2,
			},
		},
		impact_m1 = {
			nom = "impact_m1",
			titre = "Impact M1 (tier 1)",
			duree = 0.8,
			graine = 3,
			palette = {
				"#ffffff",
				"#9fd8ff",
			},
			sons = {
				{
					son = "fouet_m1",
					t0 = 0.07,
					volume = 0.5,
				},
				{
					son = "frappe_m1",
					t0 = 0.2,
					volume = 0.9,
					impact = true,
					vide = 0.025,
				},
			},
			couches = {
				{
					type = "particules",
					nom = "etoile",
					t0 = 0.2,
					ancre = {
						pos = {0, 3.1, -2.2},
						dir = {0, 0, -1},
						coup = {0, 0, -1},
					},
					texture = "etoile4",
					emit = 1,
					lifetime = {0.05, 0.05},
					size = {
						{0, 3.2, 0},
						{1, 2.2, 0},
					},
					color = {
						{
							0,
							{1, 1, 1},
						},
						{
							1,
							{1, 1, 1},
						},
					},
					light_emission = 1,
					zoffset = 1,
					transparency = {
						{0, 0, 0},
						{1, 0, 0},
					},
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					speed = {0, 0},
					rotation = {0, 0},
					rotspeed = {0, 0},
					spread = {0, 0},
					accel = {0, 0, 0},
				},
				{
					type = "particules",
					nom = "anneau",
					t0 = 0.2,
					ancre = {
						pos = {0, 3.1, -2.2},
						dir = {0, 0, -1},
						coup = {0, 0, -1},
					},
					texture = "anneau",
					emit = 1,
					lifetime = {0.12, 0.12},
					size = {
						{0, 0.6, 0},
						{1, 4.2, 0},
					},
					transparency = {
						{0, 0, 0},
						{1, 1, 0},
					},
					color = {
						{
							0,
							{1, 1, 1},
						},
						{
							1,
							{1, 1, 1},
						},
					},
					light_emission = 1,
					orientation = "FacingCamera",
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					speed = {0, 0},
					rotation = {0, 0},
					rotspeed = {0, 0},
					spread = {0, 0},
					accel = {0, 0, 0},
				},
				{
					type = "particules",
					nom = "croissant",
					t0 = 0.19,
					ancre = {
						pos = {0, 3.1, -2.2},
						dir = {0, 0, -1},
						coup = {0, 0, -1},
					},
					texture = "croissant",
					emit = 1,
					lifetime = {0.09, 0.09},
					size = {
						{0, 2.4, 0},
						{1, 3, 0},
					},
					transparency = {
						{0, 0.1, 0},
						{1, 1, 0},
					},
					color = {
						{
							0,
							{1, 1, 1},
						},
						{
							1,
							{1, 1, 1},
						},
					},
					light_emission = 1,
					rotation = {-100, -80},
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					speed = {0, 0},
					rotspeed = {0, 0},
					spread = {0, 0},
					accel = {0, 0, 0},
				},
				{
					type = "particules",
					nom = "eclats",
					t0 = 0.2,
					ancre = {
						pos = {0, 3.1, -2.2},
						dir = {0, 0, -1},
						coup = {0, 0, -1},
					},
					texture = "eclat",
					emit = 6,
					lifetime = {0.1, 0.18},
					speed = {22, 34},
					spread = {60, 60},
					drag = 8,
					orientation = "VelocityParallel",
					size = {
						{0, 0.9, 0},
						{1, 0.1, 0},
					},
					color = {
						{
							0,
							{1, 1, 1},
						},
						{
							1,
							{1, 1, 1},
						},
					},
					light_emission = 1,
					transparency = {
						{0, 0, 0},
						{1, 0, 0},
					},
					squash = {
						{0, 0, 0},
						{1, 0, 0},
					},
					rotation = {0, 0},
					rotspeed = {0, 0},
					accel = {0, 0, 0},
				},
			},
			bloom = {
				intensite = {
					{0, 0.7, 0},
					{1, 0.7, 0},
				},
				seuil = 0.75,
				taille = 2,
			},
		},
	},
	assets = {
		textures = {
			croissant = nil,
			eclat = nil,
			etoile4 = nil,
			anneau = nil,
			flash = nil,
			ligne_vitesse = nil,
			bruit_energie = nil,
			arc_vent = nil,
			ruban = nil,
			halo = nil,
			bruit_energie_d0 = nil,
			bruit_energie_d1 = nil,
			bruit_energie_d2 = nil,
			bruit_energie_d3 = nil,
			bruit_energie_d4 = nil,
			bruit_energie_d5 = nil,
			bruit_energie_d6 = nil,
			bruit_energie_d7 = nil,
			fumee_cel = nil,
			feu_cel = nil,
			flamme_aura = nil,
		},
		variantes = {
			bruit_energie = 8,
		},
		sons = {
			impact_lourd = nil,
			frappe_m1 = nil,
			grondement = nil,
			souffle_projectile = nil,
			aspiration = nil,
			naissance_orbe = nil,
			vent_arc = nil,
			fouet_m1 = nil,
		},
		manquants = {
			"anneau",
			"arc_vent",
			"bruit_energie",
			"bruit_energie_d0",
			"bruit_energie_d1",
			"bruit_energie_d2",
			"bruit_energie_d3",
			"bruit_energie_d4",
			"bruit_energie_d5",
			"bruit_energie_d6",
			"bruit_energie_d7",
			"croissant",
			"eclat",
			"etoile4",
			"feu_cel",
			"flamme_aura",
			"flash",
			"fumee_cel",
			"halo",
			"ligne_vitesse",
			"ruban",
		},
		sons_manquants = {
			"aspiration",
			"fouet_m1",
			"frappe_m1",
			"grondement",
			"impact_lourd",
			"naissance_orbe",
			"souffle_projectile",
			"vent_arc",
		},
		repli_texture = "rbxasset://textures/particles/sparkles_main.dds",
	},
}
