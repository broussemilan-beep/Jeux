--[[
	Test du SENS de UnSeulCoup.luau, exécuté par l'interpréteur Luau officiel.
	Les mocks CFrame/Vector3 sont ceux du Poing du Dragon (copiés par
	run_sens_test.py depuis r6_poing_dragon/luau/sens_test.luau).
	Lancer : python3 run_sens_test.py <luau>
]]
-- @@MOCKS@@
V.Lerp = function(a, b, u) return a + (b - a) * u end

-- @@DATA@@
-- @@MODULE@@

local fails = 0
local function near(a, b, tol, what)
	local d = (a - b).Magnitude
	local ok = d < (tol or 1e-4)
	print(string.format("%s %-62s (%.3f, %.3f, %.3f)", ok and "OK  " or "FAUX", what, a.X, a.Y, a.Z))
	if not ok then fails += 1 end
end
local function check(ok, what)
	print((ok and "OK   " or "FAUX ") .. what)
	if not ok then fails += 1 end
end
local function dot(a, b) return a.X * b.X + a.Y * b.Y + a.Z * b.Z end

-- 1. placement : victime devant, tournée vers l'attaquant, même attaquant tourné
local att = CFrame.new(0, 3, 0)
local vic = UnSeulCoup.victimCFrame(att, DATA.DISTANCE)
near(vic.Position, v3(0, 3, -DATA.DISTANCE), nil, "victime DEVANT l'attaquant (z = -distance)")
near(vic.LookVector, v3(0, 0, 1), nil, "victime tournée VERS l'attaquant")
local att2 = CFrame.new(10, 8, 5) * CFrame.Angles(0, math.rad(90), 0)
near((UnSeulCoup.victimCFrame(att2, DATA.DISTANCE).Position - att2.Position).Unit, att2.LookVector, nil, "attaquant tourné de 90° : victime toujours devant")
near(UnSeulCoup.toWorld(att2, { 0, 3, 0 }), att2.Position, nil, "point (0,3,0) de la scène = HumanoidRootPart en jeu")
near(UnSeulCoup.toWorld(att2, { 0, 3, -5 }), att2.Position + att2.LookVector * 5, nil, "scène -Z = devant l'attaquant tourné")

-- 2. la DESTRUCTION : toutes les roches DEVANT l'attaquant, au sol, dans l'axe du coup,
--    et elles sortent dans l'ordre de la distance (la vague file vers l'horizon)
local devant, sol, tri = true, true, true
local loin, tLoin = 0, 0
for _, r in DATA.DECOR.roches do
	local p = UnSeulCoup.toWorld(att2, { r.p[1], 0, r.p[2] })
	local d = dot(p - att2.Position, att2.LookVector)
	if d < 10 then devant = false end
	if math.abs(p.Y - (att2.Position.Y - 3)) > 1e-6 then sol = false end
	if d > loin + 60 and r.t < tLoin then tri = false end
	if d > loin then loin, tLoin = d, r.t end
end
check(devant, "toutes les roches DEVANT l'attaquant (> 10 studs)")
check(sol, "roches posées AU SOL (pas à hauteur de hanche)")
check(tri, "la vague file vers l'horizon (plus loin = plus tard)")
check(loin > 400, "le sillon va jusqu'à l'horizon (> 400 studs)")
local r1 = DATA.DECOR.roches[1]
local s0 = UnSeulCoup.rocheSortie(r1, r1.t - 0.01)
local s1 = UnSeulCoup.rocheSortie(r1, r1.t + 1)
check(s0 == 0 and math.abs(s1 - 1) < 1e-6, "roche : enterrée avant son temps, sortie après")
check(UnSeulCoup.sillonLongueur(DATA, DATA.CONTACT_T - 0.1) == 0, "sillon fermé avant le coup")
check(UnSeulCoup.sillonLongueur(DATA, DATA.CONTACT_T + 10) == DATA.DECOR.sillon.long, "sillon ouvert en entier à la fin")

-- 3. les NUAGES s'écartent de la ligne du coup (jamais vers elle), après l'onde
local F = DATA.DECOR.fente
local ecarte, avant = true, true
for _, n in DATA.DECOR.nuages do
	local dx = n.p[1] - F.x
	local o = UnSeulCoup.nuageDecalage(F, n.p[1], n.p[3], 99)
	if dx * o < 0 then ecarte = false end
	if UnSeulCoup.nuageDecalage(F, n.p[1], n.p[3], F.t0 - 0.01) ~= 0 then avant = false end
end
check(ecarte, "nuages : ils s'ÉCARTENT de la ligne du coup")
check(avant, "nuages : immobiles avant l'onde")

-- 4. caméra : exacte sur chaque clé, tenue jusqu'à la coupe, continue ailleurs
for i, k in DATA.CAMERA do
	local eye = UnSeulCoup.cameraAt(DATA, k.f)
	if not (DATA.CAMERA[i + 1] and DATA.CAMERA[i + 1].f == k.f) then
		near(eye, v3(k.eye[1], k.eye[2], k.eye[3]), 1e-6, "caméra clé f" .. k.f .. " : œil exact")
	end
	if i > 1 and not k.cut then
		local e2 = UnSeulCoup.cameraAt(DATA, k.f - 1e-3)
		check((e2 - eye).Magnitude < 0.05, "f" .. k.f .. " : pas de saut de caméra hors coupe")
	end
end
check(UnSeulCoup.frameTenue(DATA, DATA.INVERSE[1] + 2) == DATA.INVERSE[1], "1re image inversée : tenue 4 i")
check(UnSeulCoup.frameTenue(DATA, DATA.INVERSE[1] + 6) == DATA.INVERSE[1] + 4, "2e image inversée : tenue 4 i")

-- 5. ordre de l'impact : contact -> inversées -> blanc -> conséquence ; le son lourd AU contact
check(DATA.INVERSE[1] == DATA.CONTACT_F and DATA.INVERSE[2] <= DATA.BLANC[1], "inversées au contact, avant le blanc")
local impactSon, silence = false, true
for _, e in DATA.EVENTS do
	if e.kind == "son" and e.son == "impact_lourd" then impactSon = e.frame == DATA.CONTACT_F end
	if e.kind == "son" and e.frame > DATA.CONTACT_F - 4 and e.frame < DATA.CONTACT_F and e.son ~= "souffle_projectile" then silence = false end
end
check(impactSon, "son d'impact lourd exactement au contact")
check(silence, "rien ne démarre dans les 4 images avant l'impact (le vide avant)")

-- 6. ordonnanceur : chaque événement une fois, dans l'ordre
local state = { next = 1 }
local fired, last, ordered = 0, -1, true
for f = 0, DATA.END + 5, 0.5 do
	for _, e in UnSeulCoup.due(DATA, state, f) do
		fired += 1
		if e.frame < last then ordered = false end
		last = e.frame
	end
end
check(fired == #DATA.EVENTS and ordered, "ordonnanceur : " .. fired .. "/" .. #DATA.EVENTS .. " événements, dans l'ordre")

-- 7. fin : attaquant replacé où il a fini (devant son point de départ), victime au loin devant
local fa, fv = UnSeulCoup.finalCFrames(att2, DATA)
check(dot(fa.Position - att2.Position, att2.LookVector) > 8, "fin : attaquant replacé DEVANT (il a avancé)")
check(dot(fv.Position - att2.Position, att2.LookVector) > 150, "fin : victime au loin, dans l'axe du coup")

print(fails == 0 and "SENS OK" or ("SENS FAUX : " .. fails))
