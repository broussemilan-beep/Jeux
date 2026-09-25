--!nonstrict
-- GENERE par scripts/build_roblox_package.py depuis output/staging.json : ne pas editer a la main.
-- Repere de scene : origine au sol sous le HumanoidRootPart de l'attaquant au lancement, avant = -Z.
return {
	FPS = 60,
	END = 526,
	DISTANCE = 3.3,
	WHIP_FRAME = 196,
	CINEMA_DOSE = 0.7,
	FINAL = { attacker = { 0.015, 3.0, -6.831 }, victim = { 0.073, 3.0, -19.334 } },
	CAMERA = {
		{ f = 0, eye = { 10.617, 5.948, 1.46 }, look = { 0.117, 2.748, -1.54 }, fov = 46, cut = true },
		{ f = 26, eye = { 9.672, 5.681, 1.13 }, look = { 0.072, 2.781, -1.47 }, fov = 44, cut = false },
		{ f = 28, eye = { 8.551, 4.187, 2.269 }, look = { -0.049, 2.887, -1.731 }, fov = 44, cut = true },
		{ f = 50, eye = { 7.788, 4.125, 1.798 }, look = { -0.212, 2.925, -1.802 }, fov = 42, cut = false },
		{ f = 52, eye = { 8.47, 7.476, -0.884 }, look = { -0.73, 2.476, -2.284 }, fov = 44, cut = true },
		{ f = 76, eye = { 8.1, 7.12, -1.166 }, look = { -0.5, 2.52, -2.366 }, fov = 42, cut = false },
		{ f = 78, eye = { 11.419, 3.732, -1.434 }, look = { -0.081, 2.332, -2.834 }, fov = 42, cut = true },
		{ f = 116, eye = { 10.586, 3.669, -2.222 }, look = { 0.186, 2.469, -3.222 }, fov = 42, cut = false },
		{ f = 126, eye = { 9.037, 4.006, -0.374 }, look = { 0.29, 3.606, -3.014 }, fov = 46, cut = true },
		{ f = 145, eye = { 8.11, 3.94, -0.651 }, look = { 0.344, 3.54, -3.087 }, fov = 44, cut = false },
		{ f = 146, eye = { 9.029, 3.2, -2.311 }, look = { 0.229, 2.5, -3.311 }, fov = 40, cut = true },
		{ f = 150, eye = { 8.429, 3.1, -2.411 }, look = { 0.229, 2.5, -3.311 }, fov = 38, cut = false },
		{ f = 151, eye = { 26.014, 8.759, 2.111 }, look = { 0.014, 4.759, -4.889 }, fov = 42, cut = true },
		{ f = 165, eye = { 24.166, 11.01, 0.334 }, look = { 0.166, 8.01, -5.666 }, fov = 42, cut = false },
		{ f = 166, eye = { 9.363, 1.2, -1.949 }, look = { 0.31, 3.535, -2.938 }, fov = 54, cut = true },
		{ f = 172, eye = { 8.863, 1.8, -3.349 }, look = { 0.063, 8.172, -4.76 }, fov = 56, cut = false },
		{ f = 196, eye = { 11.763, 16.595, -2.997 }, look = { -0.237, 15.595, -6.497 }, fov = 56, cut = false },
		{ f = 208, eye = { 1.269, 17.964, -14.534 }, look = { -0.331, 19.264, -5.134 }, fov = 40, cut = false },
		{ f = 227, eye = { 1.522, 18.097, -14.447 }, look = { 0.022, 19.297, -5.447 }, fov = 40, cut = false },
		{ f = 228, eye = { 8.738, 17.485, -7.278 }, look = { 0.338, 18.485, -6.478 }, fov = 46, cut = true },
		{ f = 255, eye = { 7.836, 17.655, -7.128 }, look = { 0.436, 18.505, -6.528 }, fov = 44, cut = false },
		{ f = 256, eye = { -1.101, 14.853, -8.392 }, look = { 1.249, 20.333, -5.2 }, fov = 78, cut = true },
		{ f = 260, eye = { -1.101, 14.853, -8.392 }, look = { -0.509, 18.748, -5.612 }, fov = 78, cut = false },
		{ f = 263, eye = { -1.101, 14.853, -8.392 }, look = { 0.506, 18.562, -6.998 }, fov = 78, cut = false },
		{ f = 266, eye = { -1.101, 14.853, -8.392 }, look = { 0.328, 17.892, -6.859 }, fov = 78, cut = false },
		{ f = 270, eye = { -1.101, 14.853, -8.392 }, look = { 0.084, 17.006, -6.668 }, fov = 78, cut = false },
		{ f = 274, eye = { -1.101, 14.853, -8.392 }, look = { -0.064, 16.045, -7.244 }, fov = 78, cut = false },
		{ f = 278, eye = { -1.101, 14.853, -8.392 }, look = { -0.216, 15.087, -7.816 }, fov = 78, cut = false },
		{ f = 279, eye = { 7.987, 11.761, -2.786 }, look = { -0.013, 9.461, -6.986 }, fov = 52, cut = true },
		{ f = 288, eye = { 6.0, 4.766, -3.071 }, look = { 0.0, 2.766, -8.071 }, fov = 46, cut = false },
		{ f = 298, eye = { 9.0, 6.766, -0.471 }, look = { 0.0, 2.566, -8.071 }, fov = 52, cut = false },
		{ f = 314, eye = { 2.926, 6.179, 4.141 }, look = { -0.1, 0.197, -12.847 }, fov = 52, cut = true },
		{ f = 490, eye = { 2.426, 5.679, 2.641 }, look = { -0.1, 0.397, -12.847 }, fov = 50, cut = false },
		{ f = 526, eye = { 2.326, 5.779, 2.441 }, look = { -0.1, 0.597, -12.847 }, fov = 50, cut = false },
	},
	EVENTS = {
		{ frame = 0, kind = "body_flash", who = "attaquant", color = "#fff6dc", frames = 4 },
		{ frame = 0, kind = "ground_burst", pos = { 0.0, 0.05, 0.0 }, color = "#ffc53d", scale = 0.8 },
		{ frame = 6, kind = "studio", name = "hit1", recette = { nom = "dragon_hit1", titre = "dragon_hit1", duree = 0.395, graine = 5, sons = {
					{ son = "fouet_m1", t0 = 0.0033, volume = 0.45, hauteur = 1.04, duree = 0.1 },
					{ son = "frappe_m1", t0 = 0.1333, volume = 0.85, impact = true, vide = 0.025, hauteur = 1.04, duree = 0.22 },
				}, couches = {
					{ type = "particules", nom = "etoile", t0 = 0.1333, ancre = { pos = { -0.0, 3.287, -2.75 }, dir = { 0.086, -0.103, -0.991 }, coup = { 0.086, -0.103, -0.991 } }, texture = "etoile4", emit = 1, lifetime = { 0.0333, 0.0333 }, size = {
							{ 0.0, 3.23, 0.0 },
							{ 1.0, 2.28, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, zoffset = 2.5, transparency = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "anneau", t0 = 0.1333, ancre = { pos = { -0.0, 3.287, -2.75 }, dir = { 0.086, -0.103, -0.991 }, coup = { 0.086, -0.103, -0.991 } }, texture = "anneau", emit = 1, lifetime = { 0.12, 0.12 }, size = {
							{ 0.0, 0.57, 0.0 },
							{ 1.0, 4.37, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "croissant", t0 = 0.1166, ancre = { pos = { -0.0, 3.287, -2.75 }, dir = { 0.086, -0.103, -0.991 }, coup = { 0.086, -0.103, -0.991 } }, texture = "croissant", emit = 1, lifetime = { 0.09, 0.09 }, size = {
							{ 0.0, 2.47, 0.0 },
							{ 1.0, 3.04, 0.0 },
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, rotation = { -100.0, -80.0 }, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "eclats", t0 = 0.1333, ancre = { pos = { -0.0, 3.287, -2.75 }, dir = { 0.086, -0.103, -0.991 }, coup = { 0.086, -0.103, -0.991 } }, texture = "eclat", emit = 6, lifetime = { 0.1, 0.2 }, speed = { 22.8, 36.1 }, spread = { 55, 55 }, drag = 8, orientation = "VelocityParallel", size = {
							{ 0.0, 0.95, 0.0 },
							{ 1.0, 0.1, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1.0,
								{ 1.0, 0.7725, 0.2392 },
							},
						}, light_emission = 1, transparency = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, accel = { 0, 0, 0 } },
				}, bloom = { intensite = {
						{ 0, 0.6, 0 },
						{ 1, 0.6, 0 },
					}, seuil = 0.8, taille = 2 } } },
		{ frame = 14, kind = "impact", pos = { -0.0, 3.287, -2.75 }, dir = { 0.086, -0.103, -0.991 }, scale = 0.6, color = "#ffc53d", hitstop = 0.03, shake = 0.14, name = "hit1", tier = 1, studio = true },
		{ frame = 32, kind = "studio", name = "hit2", recette = { nom = "dragon_hit2", titre = "dragon_hit2", duree = 0.412, graine = 5, sons = {
					{ son = "fouet_m1", t0 = 0.0033, volume = 0.45, hauteur = 0.96, duree = 0.1 },
					{ son = "frappe_m1", t0 = 0.1333, volume = 0.85, impact = true, vide = 0.025, hauteur = 0.96, duree = 0.22 },
				}, couches = {
					{ type = "particules", nom = "etoile", t0 = 0.1333, ancre = { pos = { 0.0, 3.157, -3.0 }, dir = { -0.081, -0.075, -0.994 }, coup = { -0.081, -0.075, -0.994 } }, texture = "etoile4", emit = 1, lifetime = { 0.0333, 0.0333 }, size = {
							{ 0.0, 3.383, 0.0 },
							{ 1.0, 2.388, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, zoffset = 2.5, transparency = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "anneau", t0 = 0.1333, ancre = { pos = { 0.0, 3.157, -3.0 }, dir = { -0.081, -0.075, -0.994 }, coup = { -0.081, -0.075, -0.994 } }, texture = "anneau", emit = 1, lifetime = { 0.12, 0.12 }, size = {
							{ 0.0, 0.597, 0.0 },
							{ 1.0, 4.577, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "croissant", t0 = 0.1166, ancre = { pos = { 0.0, 3.157, -3.0 }, dir = { -0.081, -0.075, -0.994 }, coup = { -0.081, -0.075, -0.994 } }, texture = "croissant", emit = 1, lifetime = { 0.09, 0.09 }, size = {
							{ 0.0, 2.587, 0.0 },
							{ 1.0, 3.184, 0.0 },
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, rotation = { -100.0, -80.0 }, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "eclats", t0 = 0.1333, ancre = { pos = { 0.0, 3.157, -3.0 }, dir = { -0.081, -0.075, -0.994 }, coup = { -0.081, -0.075, -0.994 } }, texture = "eclat", emit = 6, lifetime = { 0.1, 0.2 }, speed = { 23.88, 37.81 }, spread = { 55, 55 }, drag = 8, orientation = "VelocityParallel", size = {
							{ 0.0, 0.995, 0.0 },
							{ 1.0, 0.1, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1.0,
								{ 1.0, 0.7725, 0.2392 },
							},
						}, light_emission = 1, transparency = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, accel = { 0, 0, 0 } },
				}, bloom = { intensite = {
						{ 0, 0.6, 0 },
						{ 1, 0.6, 0 },
					}, seuil = 0.8, taille = 2 } } },
		{ frame = 40, kind = "impact", pos = { 0.0, 3.157, -3.0 }, dir = { -0.081, -0.075, -0.994 }, scale = 0.78, color = "#ffc53d", hitstop = 0.045, shake = 0.22, name = "hit2", tier = 1, studio = true },
		{ frame = 56, kind = "studio", name = "hit3", recette = { nom = "dragon_hit3", titre = "dragon_hit3", duree = 0.387, graine = 5, sons = {
					{ son = "fouet_m1", t0 = 0.0033, volume = 0.45, hauteur = 1.08, duree = 0.1 },
					{ son = "frappe_m1", t0 = 0.1333, volume = 0.85, impact = true, vide = 0.025, hauteur = 1.08, duree = 0.22 },
				}, couches = {
					{ type = "particules", nom = "etoile", t0 = 0.1333, ancre = { pos = { -0.562, 3.156, -3.379 }, dir = { 0.475, -0.135, -0.87 }, coup = { 0.475, -0.135, -0.87 } }, texture = "etoile4", emit = 1, lifetime = { 0.0333, 0.0333 }, size = {
							{ 0.0, 3.5275, 0.0 },
							{ 1.0, 2.49, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, zoffset = 2.5, transparency = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "anneau", t0 = 0.1333, ancre = { pos = { -0.562, 3.156, -3.379 }, dir = { 0.475, -0.135, -0.87 }, coup = { 0.475, -0.135, -0.87 } }, texture = "anneau", emit = 1, lifetime = { 0.12, 0.12 }, size = {
							{ 0.0, 0.6225, 0.0 },
							{ 1.0, 4.7725, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "croissant", t0 = 0.1166, ancre = { pos = { -0.562, 3.156, -3.379 }, dir = { 0.475, -0.135, -0.87 }, coup = { 0.475, -0.135, -0.87 } }, texture = "croissant", emit = 1, lifetime = { 0.09, 0.09 }, size = {
							{ 0.0, 2.6975, 0.0 },
							{ 1.0, 3.32, 0.0 },
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, rotation = { -100.0, -80.0 }, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "eclats", t0 = 0.1333, ancre = { pos = { -0.562, 3.156, -3.379 }, dir = { 0.475, -0.135, -0.87 }, coup = { 0.475, -0.135, -0.87 } }, texture = "eclat", emit = 6, lifetime = { 0.1, 0.2 }, speed = { 24.9, 39.425 }, spread = { 55, 55 }, drag = 8, orientation = "VelocityParallel", size = {
							{ 0.0, 1.0375, 0.0 },
							{ 1.0, 0.1, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1.0,
								{ 1.0, 0.7725, 0.2392 },
							},
						}, light_emission = 1, transparency = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, accel = { 0, 0, 0 } },
				}, bloom = { intensite = {
						{ 0, 0.6, 0 },
						{ 1, 0.6, 0 },
					}, seuil = 0.8, taille = 2 } } },
		{ frame = 64, kind = "impact", pos = { -0.562, 3.156, -3.379 }, dir = { 0.475, -0.135, -0.87 }, scale = 0.95, color = "#ffc53d", hitstop = 0.06, shake = 0.3, name = "hit3", tier = 1, studio = true },
		{ frame = 82, kind = "studio", name = "hit4", recette = { nom = "dragon_hit4", titre = "dragon_hit4", duree = 0.663, graine = 5, sons = {
					{ son = "fouet_m1", t0 = 0.0033, volume = 0.45, hauteur = 0.92, duree = 0.1 },
					{ son = "frappe_m1", t0 = 0.1333, volume = 0.85, impact = true, vide = 0.025, hauteur = 0.92, duree = 0.22 },
					{ son = "impact_lourd", t0 = 0.1333, volume = 0.35, hauteur = 1.25, duree = 0.6 },
				}, couches = {
					{ type = "particules", nom = "etoile", t0 = 0.1333, ancre = { pos = { 0.061, 2.142, -4.291 }, dir = { -0.022, -0.131, -0.991 }, coup = { -0.022, -0.131, -0.991 } }, texture = "etoile4", emit = 1, lifetime = { 0.08, 0.08 }, size = {
							{ 0.0, 3.6975, 0.0 },
							{ 1.0, 2.61, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, zoffset = 2.5, transparency = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "anneau", t0 = 0.1333, ancre = { pos = { 0.061, 2.142, -4.291 }, dir = { -0.022, -0.131, -0.991 }, coup = { -0.022, -0.131, -0.991 } }, texture = "anneau", emit = 1, lifetime = { 0.12, 0.12 }, size = {
							{ 0.0, 0.6525, 0.0 },
							{ 1.0, 5.0025, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "croissant", t0 = 0.1166, ancre = { pos = { 0.061, 2.142, -4.291 }, dir = { -0.022, -0.131, -0.991 }, coup = { -0.022, -0.131, -0.991 } }, texture = "croissant", emit = 1, lifetime = { 0.09, 0.09 }, size = {
							{ 0.0, 2.8275, 0.0 },
							{ 1.0, 3.48, 0.0 },
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, rotation = { -100.0, -80.0 }, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "eclats", t0 = 0.1333, ancre = { pos = { 0.061, 2.142, -4.291 }, dir = { -0.022, -0.131, -0.991 }, coup = { -0.022, -0.131, -0.991 } }, texture = "eclat", emit = 14, lifetime = { 0.1, 0.2 }, speed = { 26.1, 41.325 }, spread = { 55, 55 }, drag = 8, orientation = "VelocityParallel", size = {
							{ 0.0, 1.0875, 0.0 },
							{ 1.0, 0.1, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1.0,
								{ 1.0, 0.7725, 0.2392 },
							},
						}, light_emission = 1, transparency = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, accel = { 0, 0, 0 } },
					{ type = "mesh", nom = "dome", t0 = 0.1333, duree = 0.2, ancre = { pos = { 0.061, 2.142, -4.291 }, dir = { -0.022, -0.131, -0.991 }, coup = { -0.022, -0.131, -0.991 } }, mesh = "dome", orientation = "coup", texture = "bruit_energie", defilement = { 1.2, 0 }, echelle = {
							{
								0,
								{ 0.435, 0.435, 0.435 },
							},
							{
								0.4,
								{ 1.9575, 1.9575, 1.9575 },
							},
							{
								1,
								{ 2.61, 2.61, 2.61 },
							},
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 0.5, 0.5, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, bord = 1.0, light_emission = 1 },
					{ type = "mesh", nom = "vent", t0 = 0.1433, duree = 0.22, ancre = { pos = { 0.061, 2.142, -4.291 }, dir = { -0.022, -0.131, -0.991 }, coup = { -0.022, -0.131, -0.991 } }, mesh = "croissant_3d", orientation = "coup", texture = "bruit_energie", defilement = { 2.2, 0 }, echelle = {
							{
								0,
								{ 1.305, 1.305, 1.305 },
							},
							{
								1,
								{ 3.915, 3.915, 3.915 },
							},
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 0.7, 0.4, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, rotation_vitesse = 480, light_emission = 1 },
				}, bloom = { intensite = {
						{ 0, 0.6, 0 },
						{ 1, 0.6, 0 },
					}, seuil = 0.8, taille = 2 } } },
		{ frame = 90, kind = "body_flash", who = "attaquant", color = "#ffb070", frames = 2 },
		{ frame = 90, kind = "vitesse", duration = 0.1 },
		{ frame = 90, kind = "impact", pos = { 0.061, 2.142, -4.291 }, dir = { -0.022, -0.131, -0.991 }, scale = 1.15, color = "#ffc53d", hitstop = 0.085, shake = 0.42, name = "hit4", tier = 2, studio = true },
		{ frame = 124, kind = "aura", who = "attaquant", frames = 24, color = "#ffc53d", intensity = 0.7 },
		{ frame = 124, kind = "fist_glow", who = "attaquant", side = "R", frames = 26, color = "#ffc53d" },
		{ frame = 142, kind = "studio", name = "coup_charge", recette = { nom = "dragon_coup_charge", titre = "dragon_coup_charge", duree = 2.271, graine = 5, sons = {
					{ son = "fouet_m1", t0 = 0.0033, volume = 0.45, hauteur = 1.0, duree = 0.1 },
					{ son = "frappe_m1", t0 = 0.1333, volume = 0.85, impact = true, vide = 0.025, hauteur = 1.0, duree = 0.22 },
					{ son = "impact_lourd", t0 = 0.2833, volume = 1.0, impact = true, vide = 0.08, duree = 0.6 },
					{ son = "grondement", t0 = 0.2933, volume = 0.7, duree = 1.6 },
					{ son = "vent_arc", t0 = 0.581, volume = 0.5, duree = 0.28 },
				}, couches = {
					{ type = "particules", nom = "etoile", t0 = 0.1333, ancre = { pos = { 0.159, 2.852, -5.018 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, texture = "etoile4", emit = 1, lifetime = { 0.08, 0.08 }, size = {
							{ 0.0, 4.08, 0.0 },
							{ 1.0, 2.88, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, zoffset = 2.5, transparency = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "anneau", t0 = 0.1333, ancre = { pos = { 0.159, 2.852, -5.018 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, texture = "anneau", emit = 1, lifetime = { 0.12, 0.12 }, size = {
							{ 0.0, 0.72, 0.0 },
							{ 1.0, 5.52, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "croissant", t0 = 0.1166, ancre = { pos = { 0.159, 2.852, -5.018 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, texture = "croissant", emit = 1, lifetime = { 0.09, 0.09 }, size = {
							{ 0.0, 3.12, 0.0 },
							{ 1.0, 3.84, 0.0 },
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, rotation = { -100.0, -80.0 }, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "eclats", t0 = 0.1333, ancre = { pos = { 0.159, 2.852, -5.018 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, texture = "eclat", emit = 14, lifetime = { 0.1, 0.2 }, speed = { 28.8, 45.6 }, spread = { 55, 55 }, drag = 8, orientation = "VelocityParallel", size = {
							{ 0.0, 1.2, 0.0 },
							{ 1.0, 0.1, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1.0,
								{ 1.0, 0.7725, 0.2392 },
							},
						}, light_emission = 1, transparency = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, accel = { 0, 0, 0 } },
					{ type = "mesh", nom = "dome", t0 = 0.1333, duree = 0.2, ancre = { pos = { 0.159, 2.852, -5.018 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, mesh = "dome", orientation = "coup", texture = "bruit_energie", defilement = { 1.2, 0 }, echelle = {
							{
								0,
								{ 0.48, 0.48, 0.48 },
							},
							{
								0.4,
								{ 2.16, 2.16, 2.16 },
							},
							{
								1,
								{ 2.88, 2.88, 2.88 },
							},
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 0.5, 0.5, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, bord = 1.0, light_emission = 1 },
					{ type = "mesh", nom = "vent", t0 = 0.1433, duree = 0.22, ancre = { pos = { 0.159, 2.852, -5.018 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, mesh = "croissant_3d", orientation = "coup", texture = "bruit_energie", defilement = { 2.2, 0 }, echelle = {
							{
								0,
								{ 1.44, 1.44, 1.44 },
							},
							{
								1,
								{ 4.32, 4.32, 4.32 },
							},
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 0.7, 0.4, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, rotation_vitesse = 480, light_emission = 1 },
					{ type = "particules", nom = "flash", t0 = 0.581, ancre = { pos = { 0.138, 2.668, -6.607 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, texture = "flash", emit = 1, lifetime = { 0.07, 0.07 }, size = {
							{ 0.0, 8.1, 0.0 },
							{ 1.0, 10.8, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 0.6, 0.2, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1, rotation = { 0.0, 360.0 }, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "etoile", t0 = 0.581, ancre = { pos = { 0.138, 2.668, -6.607 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, texture = "etoile4", emit = 1, lifetime = { 0.16, 0.16 }, size = {
							{ 0.0, 12.6, 0.0 },
							{ 1.0, 3.6, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1, zoffset = 2.5, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "mesh", nom = "dome", t0 = 0.591, duree = 0.32, ancre = { pos = { 0.138, 2.668, -6.607 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, mesh = "dome", texture = "bruit_energie", defilement = { 0.8, 0.0 }, echelle = {
							{
								0,
								{ 0.54, 0.54, 0.54 },
							},
							{
								0.35,
								{ 4.05, 4.05, 4.05 },
							},
							{
								1,
								{ 5.85, 5.85, 5.85 },
							},
						}, transparency = {
							{ 0.0, 0.05, 0.0 },
							{ 0.5, 0.45, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, bord = 1.0, light_emission = 1, orientation = "coup" },
					{ type = "particules", nom = "eclats", t0 = 0.581, ancre = { pos = { 0.138, 2.668, -6.607 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, texture = "eclat", emit = 28, lifetime = { 0.22, 0.45 }, speed = { 36.0, 67.5 }, spread = { 180, 180 }, drag = 7, orientation = "VelocityParallel", size = {
							{ 0.0, 1.98, 0.54 },
							{ 1.0, 0.18, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 0.7, 0.1, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1.0,
								{ 1.0, 0.7725, 0.2392 },
							},
						}, light_emission = 1, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "feu", t0 = 0.591, ancre = { pos = { 0.138, 2.668, -6.607 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, texture = "feu_cel", emit = 14, flipbook = { grille = 4, mode = "OneShot" }, lifetime = { 0.35, 0.6 }, speed = { 14.4, 25.2 }, spread = { 180, 180 }, drag = 6, accel = { 0, 4, 0 }, size = {
							{ 0.0, 2.88, 0.72 },
							{ 1.0, 4.95, 0.9 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 0.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 0, rotation = { 0.0, 360.0 }, rotspeed = { -60.0, 60.0 }, forme = { sphere = 0.54 }, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						} },
					{ type = "mesh", nom = "vent_1", t0 = 0.601, duree = 0.3, ancre = { pos = { 0.138, 2.668, -6.607 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, mesh = "croissant_3d", texture = "bruit_energie", defilement = { 2.2, 0 }, echelle = {
							{
								0,
								{ 1.98, 1.98, 1.98 },
							},
							{
								1,
								{ 5.85, 5.85, 5.85 },
							},
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 0.7, 0.4, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, rotation_vitesse = 520, rotation = 0, inclinaison = { 18, 0, 8 }, decalage = { 0, 0.54, 0 }, light_emission = 1, orientation = "coup" },
					{ type = "mesh", nom = "vent_2", t0 = 0.631, duree = 0.3, ancre = { pos = { 0.138, 2.668, -6.607 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, mesh = "croissant_3d", texture = "bruit_energie", defilement = { -2.0, 0 }, echelle = {
							{
								0,
								{ 2.52, 2.52, 2.52 },
							},
							{
								1,
								{ 6.75, 6.75, 6.75 },
							},
						}, transparency = {
							{ 0.0, 0.2, 0.0 },
							{ 0.7, 0.5, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, rotation_vitesse = -460, rotation = 140, inclinaison = { -24, 0, -12 }, decalage = { 0, 1.08, 0 }, light_emission = 1, orientation = "coup" },
					{ type = "particules", nom = "fumee", t0 = 0.621, ancre = { pos = { 0.138, 2.668, -6.607 }, dir = { -0.013, -0.115, -0.993 }, coup = { -0.013, -0.115, -0.993 } }, texture = "fumee_cel", emit = 12, flipbook = { grille = 4, mode = "OneShot" }, lifetime = { 1.0, 1.6 }, speed = { 6.3, 11.7 }, spread = { 180, 55 }, drag = 2.2, accel = { 0, 2.5, 0 }, size = {
							{ 0.0, 3.6, 0.9 },
							{ 1.0, 7.2, 1.35 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 0.0, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1.0,
								{ 0.7255, 0.7059, 0.6824 },
							},
						}, light_emission = 0, rotation = { 0.0, 360.0 }, forme = { sphere = 0.9 }, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotspeed = { 0.0, 0.0 } },
					{ type = "mesh", nom = "anneau_sol", t0 = 0.581, duree = 0.42, ancre = { pos = { 0.138, 0.0, -6.607 } }, mesh = "anneau_plat", texture = "ruban", echelle = {
							{
								0,
								{ 1.04, 1.04, 1.04 },
							},
							{
								0.4,
								{ 7.8, 7.8, 7.8 },
							},
							{
								1,
								{ 11.7, 11.7, 11.7 },
							},
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 0.6, 0.5, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, decalage = { 0, 0.05, 0 }, light_emission = 1 },
					{ type = "mesh", nom = "vague", t0 = 0.601, duree = 0.38, ancre = { pos = { 0.138, 0.0, -6.607 } }, mesh = "vague_sol", texture = "ruban", echelle = {
							{
								0,
								{ 1.95, 1.82, 1.95 },
							},
							{
								1,
								{ 10.4, 0.2, 10.4 },
							},
						}, transparency = {
							{ 0.0, 0.15, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1 },
					{ type = "trail", nom = "sillage", t0 = 0.581, t1 = 0.8977, ancre = { chemin = {
								{ 0.581, 0.071, 2.975, -5.866 },
								{ 0.5977, 0.047, 3.387, -6.078 },
								{ 0.6143, 0.024, 3.799, -6.29 },
								{ 0.631, -0.0, 4.207, -6.521 },
								{ 0.6477, 0.003, 4.608, -6.59 },
								{ 0.6643, 0.006, 5.01, -6.659 },
								{ 0.681, 0.008, 5.389, -6.725 },
								{ 0.6977, 0.01, 5.768, -6.792 },
								{ 0.7143, 0.013, 6.126, -6.855 },
								{ 0.731, 0.015, 6.483, -6.919 },
								{ 0.7477, 0.016, 6.819, -6.978 },
								{ 0.7643, 0.018, 7.156, -7.038 },
								{ 0.781, 0.019, 7.472, -7.094 },
								{ 0.7977, 0.021, 7.787, -7.149 },
								{ 0.8143, 0.021, 8.078, -7.2 },
								{ 0.831, 0.022, 8.369, -7.25 },
								{ 0.8477, 0.023, 8.66, -7.301 },
								{ 0.8643, 0.023, 8.923, -7.345 },
								{ 0.881, 0.023, 9.186, -7.389 },
								{ 0.8977, 0.024, 9.448, -7.433 },
							} }, lifetime = 0.3, largeur = {
							{ 0.0, 2.2, 0.0 },
							{ 1.0, 0.0, 0.0 },
						}, texture = "ruban", transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1.0,
								{ 1.0, 0.7725, 0.2392 },
							},
						}, light_emission = 1 },
					{ type = "particules", nom = "lignes", t0 = 0.581, ancre = { chemin = {
								{ 0.581, 0.071, 2.975, -5.866 },
								{ 0.5977, 0.047, 3.387, -6.078 },
								{ 0.6143, 0.024, 3.799, -6.29 },
								{ 0.631, -0.0, 4.207, -6.521 },
								{ 0.6477, 0.003, 4.608, -6.59 },
								{ 0.6643, 0.006, 5.01, -6.659 },
								{ 0.681, 0.008, 5.389, -6.725 },
								{ 0.6977, 0.01, 5.768, -6.792 },
								{ 0.7143, 0.013, 6.126, -6.855 },
								{ 0.731, 0.015, 6.483, -6.919 },
								{ 0.7477, 0.016, 6.819, -6.978 },
								{ 0.7643, 0.018, 7.156, -7.038 },
								{ 0.781, 0.019, 7.472, -7.094 },
								{ 0.7977, 0.021, 7.787, -7.149 },
								{ 0.8143, 0.021, 8.078, -7.2 },
								{ 0.831, 0.022, 8.369, -7.25 },
								{ 0.8477, 0.023, 8.66, -7.301 },
								{ 0.8643, 0.023, 8.923, -7.345 },
								{ 0.881, 0.023, 9.186, -7.389 },
								{ 0.8977, 0.024, 9.448, -7.433 },
							} }, texture = "eclat", rate = 70, duree_emission = 0.3167, lifetime = { 0.12, 0.2 }, speed = { -30.0, -18.0 }, spread = { 12, 12 }, orientation = "VelocityParallel", size = {
							{ 0.0, 1.6, 0.0 },
							{ 1.0, 0.3, 0.0 },
						}, squash = {
							{ 0.0, 1.3, 0.0 },
							{ 1.0, 1.3, 0.0 },
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, forme = { sphere = 0.9 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "fumee_sillage", t0 = 0.581, ancre = { chemin = {
								{ 0.581, 0.071, 2.975, -5.866 },
								{ 0.5977, 0.047, 3.387, -6.078 },
								{ 0.6143, 0.024, 3.799, -6.29 },
								{ 0.631, -0.0, 4.207, -6.521 },
								{ 0.6477, 0.003, 4.608, -6.59 },
								{ 0.6643, 0.006, 5.01, -6.659 },
								{ 0.681, 0.008, 5.389, -6.725 },
								{ 0.6977, 0.01, 5.768, -6.792 },
								{ 0.7143, 0.013, 6.126, -6.855 },
								{ 0.731, 0.015, 6.483, -6.919 },
								{ 0.7477, 0.016, 6.819, -6.978 },
								{ 0.7643, 0.018, 7.156, -7.038 },
								{ 0.781, 0.019, 7.472, -7.094 },
								{ 0.7977, 0.021, 7.787, -7.149 },
								{ 0.8143, 0.021, 8.078, -7.2 },
								{ 0.831, 0.022, 8.369, -7.25 },
								{ 0.8477, 0.023, 8.66, -7.301 },
								{ 0.8643, 0.023, 8.923, -7.345 },
								{ 0.881, 0.023, 9.186, -7.389 },
								{ 0.8977, 0.024, 9.448, -7.433 },
							} }, texture = "fumee_cel", rate = 28, duree_emission = 0.3167, flipbook = { grille = 4, mode = "OneShot" }, lifetime = { 0.6, 1.0 }, speed = { 0.5, 2.0 }, spread = { 180, 180 }, drag = 2, size = {
							{ 0.0, 1.8, 0.4 },
							{ 1.0, 3.6, 0.6 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 0.0, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1.0,
								{ 0.7255, 0.7059, 0.6824 },
							},
						}, light_emission = 0, rotation = { 0.0, 360.0 }, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotspeed = { 0.0, 0.0 }, accel = { 0, 0, 0 } },
				}, bloom = { intensite = {
						{ 0, 0.6, 0 },
						{ 1, 0.6, 0 },
					}, seuil = 0.8, taille = 2 } } },
		{ frame = 146, kind = "dust_trail", who = "attaquant", frames = 14 },
		{ frame = 150, kind = "body_flash", who = "attaquant", color = "#ffb070", frames = 3 },
		{ frame = 150, kind = "impact", pos = { 0.159, 2.852, -5.018 }, dir = { -0.013, -0.115, -0.993 }, scale = 1.6, color = "#ffc53d", hitstop = 0.431, shake = 0.65, name = "coup_charge", tier = 3, studio = true },
		{ frame = 150, kind = "cartes", sequence = {
				{
					"contact",
					0.05,
				},
				{
					"noir",
					0.1,
				},
				{
					"carte",
					0.067,
				},
				{
					"carte",
					0.067,
				},
				{
					"carte",
					0.067,
				},
				{
					"blanc",
					0.08,
				},
			}, fade = 0.15, tenue_blanc = 0.02 },
		{ frame = 151, kind = "impact", pos = { 0.138, 2.668, -6.607 }, dir = { -0.013, -0.115, -0.993 }, scale = 1.9, color = "#fff6dc", hitstop = 0.0, shake = 0.3, name = "coup_charge_souffle", tier = 3, studio = true },
		{ frame = 151, kind = "ground_burst", pos = { 0.159, 0.05, -5.018 }, color = "#ffc53d", scale = 1.4 },
		{ frame = 170, kind = "ground_burst", pos = { 0.207, 0.05, -2.09 }, color = "#fff6dc", scale = 1.2 },
		{ frame = 196, kind = "whip", frames = 12 },
		{ frame = 226, kind = "aura", who = "attaquant", frames = 30, color = "#ffc53d", intensity = 1.0 },
		{ frame = 226, kind = "studio", name = "arme", recette = { nom = "dragon_arme", titre = "dragon_arme", duree = 0.47, graine = 5, sons = {
					{ son = "aspiration", t0 = 0.0, volume = 0.5, duree = 0.3 },
					{ son = "naissance_orbe", t0 = 0.02, volume = 0.4, duree = 0.4 },
				}, couches = {  }, bloom = { intensite = {
						{ 0, 0.6, 0 },
						{ 1, 0.6, 0 },
					}, seuil = 0.8, taille = 2 } } },
		{ frame = 228, kind = "fist_glow", who = "attaquant", side = "R", frames = 50, color = "#ffc53d" },
		{ frame = 236, kind = "dragon", who = "attaquant", side = "R", frames = 52, color = "#ffc53d", smoke = "#3b3530" },
		{ frame = 244, kind = "studio", name = "plongee", recette = { nom = "dragon_plongee", titre = "dragon_plongee", duree = 0.917, graine = 5, sons = {
					{ son = "souffle_projectile", t0 = 0.0667, volume = 0.8, duree = 0.44 },
				}, couches = {
					{ type = "trail", nom = "sillage", t0 = 0.2, t1 = 0.5667, ancre = { chemin = {
								{ 0.2, 1.63, 20.815, -3.914 },
								{ 0.2167, 1.164, 20.134, -4.348 },
								{ 0.2333, 0.517, 19.498, -4.611 },
								{ 0.25, -0.283, 19.017, -4.724 },
								{ 0.2667, -1.151, 18.621, -4.639 },
								{ 0.2833, 0.48, 18.692, -5.141 },
								{ 0.3, 1.249, 18.209, -6.211 },
								{ 0.3167, 0.849, 17.503, -7.081 },
								{ 0.3333, 0.796, 17.286, -7.067 },
								{ 0.35, 0.741, 17.071, -7.052 },
								{ 0.3667, 0.686, 16.858, -7.037 },
								{ 0.3833, 0.629, 16.647, -7.021 },
								{ 0.4, 0.576, 16.431, -7.007 },
								{ 0.4167, 0.522, 16.217, -6.992 },
								{ 0.4333, 0.465, 16.006, -6.976 },
								{ 0.45, 0.418, 15.765, -7.152 },
								{ 0.4667, 0.37, 15.526, -7.325 },
								{ 0.4833, 0.321, 15.29, -7.496 },
								{ 0.5, 0.271, 15.057, -7.664 },
								{ 0.5167, 0.224, 14.818, -7.84 },
								{ 0.5333, 0.175, 14.581, -8.012 },
								{ 0.55, 0.126, 14.347, -8.181 },
								{ 0.5667, 0.077, 14.11, -8.353 },
							} }, lifetime = 0.3, largeur = {
							{ 0.0, 1.6, 0.0 },
							{ 1.0, 0.0, 0.0 },
						}, texture = "ruban", transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1.0,
								{ 1.0, 0.7725, 0.2392 },
							},
						}, light_emission = 1 },
					{ type = "particules", nom = "lignes", t0 = 0.2, ancre = { chemin = {
								{ 0.2, 1.63, 20.815, -3.914 },
								{ 0.2167, 1.164, 20.134, -4.348 },
								{ 0.2333, 0.517, 19.498, -4.611 },
								{ 0.25, -0.283, 19.017, -4.724 },
								{ 0.2667, -1.151, 18.621, -4.639 },
								{ 0.2833, 0.48, 18.692, -5.141 },
								{ 0.3, 1.249, 18.209, -6.211 },
								{ 0.3167, 0.849, 17.503, -7.081 },
								{ 0.3333, 0.796, 17.286, -7.067 },
								{ 0.35, 0.741, 17.071, -7.052 },
								{ 0.3667, 0.686, 16.858, -7.037 },
								{ 0.3833, 0.629, 16.647, -7.021 },
								{ 0.4, 0.576, 16.431, -7.007 },
								{ 0.4167, 0.522, 16.217, -6.992 },
								{ 0.4333, 0.465, 16.006, -6.976 },
								{ 0.45, 0.418, 15.765, -7.152 },
								{ 0.4667, 0.37, 15.526, -7.325 },
								{ 0.4833, 0.321, 15.29, -7.496 },
								{ 0.5, 0.271, 15.057, -7.664 },
								{ 0.5167, 0.224, 14.818, -7.84 },
								{ 0.5333, 0.175, 14.581, -8.012 },
								{ 0.55, 0.126, 14.347, -8.181 },
								{ 0.5667, 0.077, 14.11, -8.353 },
							} }, texture = "eclat", rate = 70, duree_emission = 0.3667, lifetime = { 0.12, 0.2 }, speed = { -30.0, -18.0 }, spread = { 12, 12 }, orientation = "VelocityParallel", size = {
							{ 0.0, 1.6, 0.0 },
							{ 1.0, 0.3, 0.0 },
						}, squash = {
							{ 0.0, 1.3, 0.0 },
							{ 1.0, 1.3, 0.0 },
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 1, forme = { sphere = 0.9 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, accel = { 0, 0, 0 } },
				}, bloom = { intensite = {
						{ 0, 0.6, 0 },
						{ 1, 0.6, 0 },
					}, seuil = 0.8, taille = 2 } } },
		{ frame = 278, kind = "body_flash", who = "attaquant", color = "#ffb070", frames = 3 },
		{ frame = 278, kind = "impact", pos = { 0.077, 14.11, -8.353 }, dir = { -0.079, -0.83, -0.553 }, scale = 1.6, color = "#ffc53d", hitstop = 0.13, shake = 0.6, name = "strike", tier = 3, studio = true },
		{ frame = 278, kind = "studio", name = "contact_aerien", recette = { nom = "dragon_contact_aerien", titre = "dragon_contact_aerien", duree = 1.69, graine = 5, sons = {
					{ son = "impact_lourd", t0 = 0.0, volume = 0.8, impact = true, duree = 0.6 },
				}, couches = {
					{ type = "particules", nom = "flash", t0 = 0.0, ancre = { pos = { 0.077, 14.11, -8.353 }, dir = { -0.079, -0.83, -0.553 }, coup = { -0.079, -0.83, -0.553 } }, texture = "flash", emit = 1, lifetime = { 0.07, 0.07 }, size = {
							{ 0.0, 4.95, 0.0 },
							{ 1.0, 6.6, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 0.6, 0.2, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1, rotation = { 0.0, 360.0 }, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "etoile", t0 = 0.0, ancre = { pos = { 0.077, 14.11, -8.353 }, dir = { -0.079, -0.83, -0.553 }, coup = { -0.079, -0.83, -0.553 } }, texture = "etoile4", emit = 1, lifetime = { 0.16, 0.16 }, size = {
							{ 0.0, 7.7, 0.0 },
							{ 1.0, 2.2, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1, zoffset = 2.5, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "mesh", nom = "dome", t0 = 0.01, duree = 0.32, ancre = { pos = { 0.077, 14.11, -8.353 }, dir = { -0.079, -0.83, -0.553 }, coup = { -0.079, -0.83, -0.553 } }, mesh = "dome", texture = "bruit_energie", defilement = { 0.8, 0.0 }, echelle = {
							{
								0,
								{ 0.33, 0.33, 0.33 },
							},
							{
								0.35,
								{ 2.475, 2.475, 2.475 },
							},
							{
								1,
								{ 3.575, 3.575, 3.575 },
							},
						}, transparency = {
							{ 0.0, 0.05, 0.0 },
							{ 0.5, 0.45, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, bord = 1.0, light_emission = 1, orientation = "coup" },
					{ type = "particules", nom = "eclats", t0 = 0.0, ancre = { pos = { 0.077, 14.11, -8.353 }, dir = { -0.079, -0.83, -0.553 }, coup = { -0.079, -0.83, -0.553 } }, texture = "eclat", emit = 28, lifetime = { 0.22, 0.45 }, speed = { 22.0, 41.25 }, spread = { 180, 180 }, drag = 7, orientation = "VelocityParallel", size = {
							{ 0.0, 1.21, 0.33 },
							{ 1.0, 0.11, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 0.7, 0.1, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1.0,
								{ 1.0, 0.7725, 0.2392 },
							},
						}, light_emission = 1, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "feu", t0 = 0.01, ancre = { pos = { 0.077, 14.11, -8.353 }, dir = { -0.079, -0.83, -0.553 }, coup = { -0.079, -0.83, -0.553 } }, texture = "feu_cel", emit = 14, flipbook = { grille = 4, mode = "OneShot" }, lifetime = { 0.35, 0.6 }, speed = { 8.8, 15.4 }, spread = { 180, 180 }, drag = 6, accel = { 0, 4, 0 }, size = {
							{ 0.0, 1.76, 0.44 },
							{ 1.0, 3.025, 0.55 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 0.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 0, rotation = { 0.0, 360.0 }, rotspeed = { -60.0, 60.0 }, forme = { sphere = 0.33 }, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						} },
					{ type = "mesh", nom = "vent_1", t0 = 0.02, duree = 0.3, ancre = { pos = { 0.077, 14.11, -8.353 }, dir = { -0.079, -0.83, -0.553 }, coup = { -0.079, -0.83, -0.553 } }, mesh = "croissant_3d", texture = "bruit_energie", defilement = { 2.2, 0 }, echelle = {
							{
								0,
								{ 1.21, 1.21, 1.21 },
							},
							{
								1,
								{ 3.575, 3.575, 3.575 },
							},
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 0.7, 0.4, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, rotation_vitesse = 520, rotation = 0, inclinaison = { 18, 0, 8 }, decalage = { 0, 0.33, 0 }, light_emission = 1, orientation = "coup" },
					{ type = "mesh", nom = "vent_2", t0 = 0.05, duree = 0.3, ancre = { pos = { 0.077, 14.11, -8.353 }, dir = { -0.079, -0.83, -0.553 }, coup = { -0.079, -0.83, -0.553 } }, mesh = "croissant_3d", texture = "bruit_energie", defilement = { -2.0, 0 }, echelle = {
							{
								0,
								{ 1.54, 1.54, 1.54 },
							},
							{
								1,
								{ 4.125, 4.125, 4.125 },
							},
						}, transparency = {
							{ 0.0, 0.2, 0.0 },
							{ 0.7, 0.5, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, rotation_vitesse = -460, rotation = 140, inclinaison = { -24, 0, -12 }, decalage = { 0, 0.66, 0 }, light_emission = 1, orientation = "coup" },
					{ type = "particules", nom = "fumee", t0 = 0.04, ancre = { pos = { 0.077, 14.11, -8.353 }, dir = { -0.079, -0.83, -0.553 }, coup = { -0.079, -0.83, -0.553 } }, texture = "fumee_cel", emit = 12, flipbook = { grille = 4, mode = "OneShot" }, lifetime = { 1.0, 1.6 }, speed = { 3.85, 7.15 }, spread = { 180, 55 }, drag = 2.2, accel = { 0, 2.5, 0 }, size = {
							{ 0.0, 2.2, 0.55 },
							{ 1.0, 4.4, 0.825 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 0.0, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1.0,
								{ 0.7255, 0.7059, 0.6824 },
							},
						}, light_emission = 0, rotation = { 0.0, 360.0 }, forme = { sphere = 0.55 }, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotspeed = { 0.0, 0.0 } },
				}, bloom = { intensite = {
						{ 0, 0.6, 0 },
						{ 1, 0.6, 0 },
					}, seuil = 0.8, taille = 2 } } },
		{ frame = 288, kind = "crater", pos = { 0.0, 0.0, -8.071 }, radius = 7.5, spikes = 34, seed = 11 },
		{ frame = 288, kind = "impact", pos = { 0.0, 0.6, -8.071 }, dir = { 0, -1, 0 }, scale = 2.4, color = "#ffc53d", hitstop = 0.16, shake = 1.0, name = "impact", tier = 3, studio = true },
		{ frame = 288, kind = "smoke_cloud", pos = { 0.0, 0.0, -8.071 }, radius = 9.0, frames = 238, color = "#7d7468" },
		{ frame = 288, kind = "embers", pos = { 0.0, 0.0, -8.071 }, frames = 238, color = "#ff8a1f" },
		{ frame = 288, kind = "studio", name = "impact_sol", recette = { nom = "dragon_impact_sol", titre = "dragon_impact_sol", duree = 1.942, graine = 5, sons = {
					{ son = "impact_lourd", t0 = 0.0, volume = 1.0, hauteur = 0.8, impact = true, vide = 0.03, duree = 0.6 },
					{ son = "grondement", t0 = 0.01, volume = 0.9, hauteur = 0.85, duree = 1.6 },
				}, couches = {
					{ type = "particules", nom = "flash", t0 = 0.0, ancre = { pos = { 0.0, 0.0, -8.071 } }, texture = "flash", emit = 1, lifetime = { 0.07, 0.07 }, size = {
							{ 0.0, 12.6, 0.0 },
							{ 1.0, 16.8, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 0.6, 0.2, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1, rotation = { 0.0, 360.0 }, zoffset = 2, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "etoile", t0 = 0.0, ancre = { pos = { 0.0, 0.0, -8.071 } }, texture = "etoile4", emit = 1, lifetime = { 0.16, 0.16 }, size = {
							{ 0.0, 19.6, 0.0 },
							{ 1.0, 5.6, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1, zoffset = 2.5, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, speed = { 0.0, 0.0 }, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, spread = { 0, 0 }, accel = { 0, 0, 0 } },
					{ type = "mesh", nom = "dome", t0 = 0.01, duree = 0.32, ancre = { pos = { 0.0, 0.0, -8.071 } }, mesh = "dome", texture = "bruit_energie", defilement = { 0.8, 0.0 }, echelle = {
							{
								0,
								{ 0.84, 0.84, 0.84 },
							},
							{
								0.35,
								{ 6.3, 6.3, 6.3 },
							},
							{
								1,
								{ 9.1, 9.1, 9.1 },
							},
						}, transparency = {
							{ 0.0, 0.05, 0.0 },
							{ 0.5, 0.45, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, bord = 1.0, light_emission = 1 },
					{ type = "mesh", nom = "anneau_sol", t0 = 0.0, duree = 0.42, ancre = { pos = { 0.0, 0.0, -8.071 } }, mesh = "anneau_plat", texture = "ruban", echelle = {
							{
								0,
								{ 1.12, 1.12, 1.12 },
							},
							{
								0.4,
								{ 8.4, 8.4, 8.4 },
							},
							{
								1,
								{ 12.6, 12.6, 12.6 },
							},
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 0.6, 0.5, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, decalage = { 0, 0.05, 0 }, light_emission = 1 },
					{ type = "particules", nom = "eclats", t0 = 0.0, ancre = { pos = { 0.0, 0.0, -8.071 } }, texture = "eclat", emit = 28, lifetime = { 0.22, 0.45 }, speed = { 56.0, 105.0 }, spread = { 180, 180 }, drag = 7, orientation = "VelocityParallel", size = {
							{ 0.0, 3.08, 0.84 },
							{ 1.0, 0.28, 0.0 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 0.7, 0.1, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1.0,
								{ 1.0, 0.7725, 0.2392 },
							},
						}, light_emission = 1, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotation = { 0.0, 0.0 }, rotspeed = { 0.0, 0.0 }, accel = { 0, 0, 0 } },
					{ type = "particules", nom = "feu", t0 = 0.01, ancre = { pos = { 0.0, 0.0, -8.071 } }, texture = "feu_cel", emit = 14, flipbook = { grille = 4, mode = "OneShot" }, lifetime = { 0.35, 0.6 }, speed = { 22.4, 39.2 }, spread = { 180, 180 }, drag = 6, accel = { 0, 4, 0 }, size = {
							{ 0.0, 4.48, 1.12 },
							{ 1.0, 7.7, 1.4 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 0.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1,
								{ 1.0, 1.0, 1.0 },
							},
						}, light_emission = 0, rotation = { 0.0, 360.0 }, rotspeed = { -60.0, 60.0 }, forme = { sphere = 0.84 }, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						} },
					{ type = "mesh", nom = "vent_1", t0 = 0.02, duree = 0.3, ancre = { pos = { 0.0, 0.0, -8.071 } }, mesh = "croissant_3d", texture = "bruit_energie", defilement = { 2.2, 0 }, echelle = {
							{
								0,
								{ 3.08, 3.08, 3.08 },
							},
							{
								1,
								{ 9.1, 9.1, 9.1 },
							},
						}, transparency = {
							{ 0.0, 0.1, 0.0 },
							{ 0.7, 0.4, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, rotation_vitesse = 520, rotation = 0, inclinaison = { 18, 0, 8 }, decalage = { 0, 0.84, 0 }, light_emission = 1 },
					{ type = "mesh", nom = "vent_2", t0 = 0.05, duree = 0.3, ancre = { pos = { 0.0, 0.0, -8.071 } }, mesh = "croissant_3d", texture = "bruit_energie", defilement = { -2.0, 0 }, echelle = {
							{
								0,
								{ 3.92, 3.92, 3.92 },
							},
							{
								1,
								{ 10.5, 10.5, 10.5 },
							},
						}, transparency = {
							{ 0.0, 0.2, 0.0 },
							{ 0.7, 0.5, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, rotation_vitesse = -460, rotation = 140, inclinaison = { -24, 0, -12 }, decalage = { 0, 1.68, 0 }, light_emission = 1 },
					{ type = "mesh", nom = "vague", t0 = 0.02, duree = 0.38, ancre = { pos = { 0.0, 0.0, -8.071 } }, mesh = "vague_sol", texture = "ruban", echelle = {
							{
								0,
								{ 2.1, 1.96, 2.1 },
							},
							{
								1,
								{ 11.2, 0.2, 11.2 },
							},
						}, transparency = {
							{ 0.0, 0.15, 0.0 },
							{ 1.0, 1.0, 0.0 },
						}, color = {
							{
								0,
								{ 1.0, 0.9647, 0.8627 },
							},
							{
								1,
								{ 1.0, 0.9647, 0.8627 },
							},
						}, light_emission = 1 },
					{ type = "particules", nom = "fumee", t0 = 0.04, ancre = { pos = { 0.0, 0.0, -8.071 } }, texture = "fumee_cel", emit = 12, flipbook = { grille = 4, mode = "OneShot" }, lifetime = { 1.0, 1.6 }, speed = { 9.8, 18.2 }, spread = { 180, 55 }, drag = 2.2, accel = { 0, 2.5, 0 }, size = {
							{ 0.0, 5.6, 1.4 },
							{ 1.0, 11.2, 2.1 },
						}, transparency = {
							{ 0.0, 0.0, 0.0 },
							{ 1.0, 0.0, 0.0 },
						}, color = {
							{
								0.0,
								{ 1.0, 1.0, 1.0 },
							},
							{
								1.0,
								{ 0.7255, 0.7059, 0.6824 },
							},
						}, light_emission = 0, rotation = { 0.0, 360.0 }, forme = { sphere = 1.4 }, squash = {
							{ 0, 0.0, 0 },
							{ 1, 0.0, 0 },
						}, rotspeed = { 0.0, 0.0 } },
				}, bloom = { intensite = {
						{ 0, 0.6, 0 },
						{ 1, 0.6, 0 },
					}, seuil = 0.8, taille = 2 } } },
		{ frame = 298, kind = "manga", frames = { 298, 300, 302, 304 } },
		{ frame = 304, kind = "white", frames = { 304, 316, 334 } },
		{ frame = 314, kind = "studio", name = "calme", recette = { nom = "dragon_calme", titre = "dragon_calme", duree = 3.65, graine = 5, sons = {
					{ son = "vent_ambiant", t0 = 0.0, volume = 0.3, duree = 3.6 },
				}, couches = {  }, bloom = { intensite = {
						{ 0, 0.6, 0 },
						{ 1, 0.6, 0 },
					}, seuil = 0.8, taille = 2 } } },
	},
}
