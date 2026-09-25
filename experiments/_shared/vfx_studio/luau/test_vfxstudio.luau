--[[
	Test de VFXStudio.luau hors Roblox, exécuté par l'interpréteur Luau officiel.
	Lancer : python3 run_test.py (assemble les mocks, les données compilées,
	les valeurs de référence de l'aperçu, le module et ce test).

	Les mocks REFUSENT ce que Roblox refuse (doc officielle) :
	NumberSequence / ColorSequence qui ne vont pas de 0 à 1 ou dépassent 20
	points, transparence hors [0, 1], Rate > 400, Lifetime > 20 s,
	FlipbookFramerate > 30. Un module qui passe ce test ne plante donc pas
	sur ces règles-là dans Studio.
]]

-- ------------------------------------------------------------ Vector3
local V = {}
local function v3(x, y, z)
	return setmetatable({ X = x, Y = y, Z = z }, V)
end
V.__add = function(a, b) return v3(a.X + b.X, a.Y + b.Y, a.Z + b.Z) end
V.__sub = function(a, b) return v3(a.X - b.X, a.Y - b.Y, a.Z - b.Z) end
V.__mul = function(a, k) return v3(a.X * k, a.Y * k, a.Z * k) end
V.__div = function(a, k) return v3(a.X / k, a.Y / k, a.Z / k) end
local VM = {}
function VM.Dot(a, b) return a.X * b.X + a.Y * b.Y + a.Z * b.Z end
function VM.Cross(a, b) return v3(a.Y * b.Z - a.Z * b.Y, a.Z * b.X - a.X * b.Z, a.X * b.Y - a.Y * b.X) end
function VM.Lerp(a, b, u) return a + (b - a) * u end
V.__index = function(t, k)
	if k == "Magnitude" then return math.sqrt(t.X * t.X + t.Y * t.Y + t.Z * t.Z) end
	if k == "Unit" then local m = math.sqrt(t.X * t.X + t.Y * t.Y + t.Z * t.Z); return v3(t.X / m, t.Y / m, t.Z / m) end
	return VM[k]
end
Vector3 = { new = v3 }

-- ------------------------------------------------------------ CFrame
local C = {}
local function cf(p, r) return setmetatable({ p = p, r = r }, C) end
local function matmul(a, b)
	local m = {}
	for i = 1, 3 do m[i] = {}; for j = 1, 3 do m[i][j] = a[i][1] * b[1][j] + a[i][2] * b[2][j] + a[i][3] * b[3][j] end end
	return m
end
local function rotv(r, v) return v3(r[1][1] * v.X + r[1][2] * v.Y + r[1][3] * v.Z, r[2][1] * v.X + r[2][2] * v.Y + r[2][3] * v.Z, r[3][1] * v.X + r[3][2] * v.Y + r[3][3] * v.Z) end
local I = { { 1, 0, 0 }, { 0, 1, 0 }, { 0, 0, 1 } }
C.__mul = function(a, b)
	if getmetatable(b) == C then return cf(a.p + rotv(a.r, b.p), matmul(a.r, b.r)) end
	return a.p + rotv(a.r, b)
end
C.__add = function(a, v) return cf(a.p + v, a.r) end
local CM = {}
function CM.PointToWorldSpace(self, v) return self.p + rotv(self.r, v) end
function CM.VectorToWorldSpace(self, v) return rotv(self.r, v) end
C.__index = function(t, k)
	if k == "Position" then return t.p end
	if k == "UpVector" then return v3(t.r[1][2], t.r[2][2], t.r[3][2]) end
	return CM[k]
end
CFrame = {
	new = function(x, y, z)
		if type(x) == "table" then return cf(x, I) end
		return cf(v3(x or 0, y or 0, z or 0), I)
	end,
	Angles = function(rx, ry, rz)
		local cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
		local Rx = { { 1, 0, 0 }, { 0, cx, -sx }, { 0, sx, cx } }
		local Ry = { { cy, 0, sy }, { 0, 1, 0 }, { -sy, 0, cy } }
		local Rz = { { cz, -sz, 0 }, { sz, cz, 0 }, { 0, 0, 1 } }
		return cf(v3(0, 0, 0), matmul(matmul(Rx, Ry), Rz))
	end,
	fromAxisAngle = function(a, th)
		local c, s, t = math.cos(th), math.sin(th), 1 - math.cos(th)
		local x, y, z = a.X, a.Y, a.Z
		return cf(v3(0, 0, 0), {
			{ t * x * x + c, t * x * y - s * z, t * x * z + s * y },
			{ t * x * y + s * z, t * y * y + c, t * y * z - s * x },
			{ t * x * z - s * y, t * y * z + s * x, t * z * z + c },
		})
	end,
}

-- ------------------------------------------------ types valeur Roblox
local fautes = {}
local function refuse(msg) table.insert(fautes, msg); error(msg, 0) end
local function verifSeq(kp, quoi)
	if #kp < 2 or #kp > 20 then refuse(quoi .. " : " .. #kp .. " points (2 à 20)") end
	if math.abs(kp[1].Time) > 1e-6 or math.abs(kp[#kp].Time - 1) > 1e-6 then refuse(quoi .. " : doit aller de 0 à 1") end
	for i = 2, #kp do if kp[i].Time < kp[i - 1].Time then refuse(quoi .. " : temps non croissants") end end
end
NumberSequenceKeypoint = { new = function(t, v, e) return { Time = t, Value = v, Envelope = e or 0 } end }
NumberSequence = { new = function(kp) verifSeq(kp, "NumberSequence"); return { Keypoints = kp } end }
ColorSequenceKeypoint = { new = function(t, c) return { Time = t, Value = c } end }
ColorSequence = { new = function(kp) verifSeq(kp, "ColorSequence"); return { Keypoints = kp } end }
NumberRange = { new = function(a, b) return { Min = a, Max = b or a } end }
Vector2 = { new = function(x, y) return { X = x, Y = y } end }
Color3 = {
	new = function(r, g, b) return { R = r, G = g, B = b } end,
	fromRGB = function(r, g, b) return { R = r / 255, G = g / 255, B = b / 255 } end,
}
UDim2 = { fromScale = function(x, y) return { x, y } end }
Enum = setmetatable({}, { __index = function(_, cat)
	return setmetatable({}, { __index = function(_, v) return cat .. "." .. v end })
end })

-- ------------------------------------------------------------ Instances
local tous = {}
local LIMITES = {
	ParticleEmitter = function(o, k, v)
		if k == "Rate" and v > 400 then refuse("Rate " .. v .. " > 400") end
		if k == "Lifetime" and v.Max > 20 then refuse("Lifetime > 20 s") end
		if k == "FlipbookFramerate" and v.Max > 30 then refuse("FlipbookFramerate > 30") end
		if k == "Transparency" then for _, p in ipairs(v.Keypoints) do if p.Value < 0 or p.Value > 1 then refuse("transparence hors [0,1]") end end end
	end,
	Trail = function(o, k, v)
		if k == "Lifetime" and (v < 0.01 or v > 20) then refuse("Trail.Lifetime hors [0.01, 20]") end
	end,
	BasePart = function(o, k, v)
		if k == "Transparency" and (v < 0 or v > 1) then refuse("Part.Transparency hors [0,1]") end
	end,
}
local Obj = {}
Obj.__index = function(o, k)
	local m = rawget(Obj, k)
	if m then return m end
	return rawget(o, "_p")[k]
end
Obj.__newindex = function(o, k, v)
	local cls = rawget(o, "ClassName")
	local lim = LIMITES[cls] or ((cls == "Part") and LIMITES.BasePart)
	if lim then lim(o, k, v) end
	local p = rawget(o, "_p")
	if k == "Parent" then
		local old = p.Parent
		if old and type(old) == "table" and rawget(old, "_enfants") then
			for i, c in ipairs(rawget(old, "_enfants")) do if c == o then table.remove(rawget(old, "_enfants"), i); break end end
		end
		if v and type(v) == "table" and rawget(v, "_enfants") then table.insert(rawget(v, "_enfants"), o) end
	end
	if k == "WorldPosition" then p.Position = v end
	p[k] = v
end
function Obj.GetChildren(o) return table.clone(rawget(o, "_enfants")) end
function Obj.GetDescendants(o)
	local out = {}
	for _, c in ipairs(rawget(o, "_enfants")) do
		table.insert(out, c)
		for _, d in ipairs(c:GetDescendants()) do table.insert(out, d) end
	end
	return out
end
function Obj.Destroy(o) o.Parent = nil; rawset(o, "_detruit", true) end
function Obj.Emit(o, n) table.insert(rawget(o, "_emis"), { t = TEMPS, n = n }) end
function Obj.Play(o) rawset(o, "_joue", TEMPS) end
local function nouvelle(cls)
	local o = setmetatable({ ClassName = cls, _p = { Name = cls }, _enfants = {}, _emis = {} }, Obj)
	table.insert(tous, o)
	return o
end
Instance = { new = nouvelle }
workspace = nouvelle("Workspace")
local lighting = nouvelle("Lighting")
game = { GetService = function(_, n)
	if n == "Lighting" then return lighting end
	return { Heartbeat = { Connect = function() return { Disconnect = function() end } end } }
end }
TEMPS = 0

-- @@DATA@@
-- @@REFS@@
-- @@MODULE@@

-- ======================================================================
local echecs = 0
local function ok(cond, quoi)
	print((cond and "OK   " or "FAUX ") .. quoi)
	if not cond then echecs += 1 end
end
local function trouver(racine, nom)
	for _, d in ipairs(racine:GetDescendants()) do if d.Name == nom then return d end end
	return nil
end

-- 1. même hasard que l'aperçu (mulberry32)
do
	local r = VFXStudio.mulberry(3000)
	local a, b = r(), r()
	ok(a >= 0 and a < 1 and b ~= a, string.format("mulberry32 produit des nombres dans [0,1[ (%.6f, %.6f)", a, b))
end

-- 2. secousse caméra = aperçu, instant par instant
for nom, rec in pairs(DATA.recettes) do
	local ecart = 0
	for _, x in ipairs(REFS.secousse[nom] or {}) do
		local d = VFXStudio.secousse(rec, x[1])
		ecart = math.max(ecart, math.abs(d.X - x[2]), math.abs(d.Y - x[3]), math.abs(d.Z - x[4]))
	end
	-- 1e-5 : les références passent par la sérialisation Luau, arrondie à 5 décimales
	ok(ecart < 1e-5, string.format("%s : secousse identique à l'aperçu (écart max %.2e)", nom, ecart))
end

-- 3. lecture complète de chaque recette, pas à pas (60 i/s)
VFXStudio.configurer(DATA.assets)
for nom, rec in pairs(DATA.recettes) do
	fautes = {}
	local cam = { CFrame = CFrame.new(0, 5, 10) }
	local ecran = nouvelle("PlayerGui")
	local okJouer, h = pcall(VFXStudio.jouer, rec, CFrame.new(0, 0, 0), { manuel = true, camera = cam, ecran = ecran })
	ok(okJouer, nom .. " : création sans erreur Roblox " .. (okJouer and "" or tostring(h)))
	if not okJouer then continue end
	local dossier = h.Dossier
	local bloom = trouver(lighting, "VFX_Bloom")
	local ecartBloom, ecartFlash, gelVu, degelVu = 0, 0, false, false
	local positionsProjectile = {}
	local transparenceHorsBornes = false
	local refBloom, refFlash = {}, {}
	for _, x in ipairs(REFS.bloom[nom] or {}) do refBloom[math.floor(x[1] * 60 + 0.5)] = x[2] end
	for _, x in ipairs(REFS.flash[nom] or {}) do refFlash[math.floor(x[1] * 60 + 0.5)] = x[2] end
	local fin = math.ceil(h.Duree * 60) + 2
	for i = 0, fin do
		TEMPS = i / 60
		local okEtape, err = pcall(h._etape, TEMPS)
		if not okEtape then ok(false, nom .. " : erreur à t=" .. TEMPS .. " : " .. tostring(err)); break end
		if dossier._detruit then break end
		if bloom and refBloom[i] then ecartBloom = math.max(ecartBloom, math.abs(bloom.Intensity - refBloom[i])) end
		local fl = trouver(ecran, "VFX_Flash")
		if fl and refFlash[i] then
			local fr = fl:GetChildren()[1]
			ecartFlash = math.max(ecartFlash, math.abs(fr.BackgroundTransparency - refFlash[i]))
		end
		for _, pe in ipairs(dossier:GetDescendants()) do
			if pe.ClassName == "ParticleEmitter" and pe.TimeScale == 0 then gelVu = TEMPS end
		end
		if gelVu and not degelVu then
			local tous1 = true
			for _, pe in ipairs(dossier:GetDescendants()) do
				if pe.ClassName == "ParticleEmitter" and pe.TimeScale == 0 then tous1 = false end
			end
			if tous1 then degelVu = TEMPS end
		end
		local mv = trouver(dossier, "M_projectile")
		if rec.projectile and mv then positionsProjectile[i] = mv.CFrame and mv.CFrame.Position end
	end
	ok(#fautes == 0, nom .. " : aucune valeur refusée par Roblox (" .. #fautes .. ")")
	for _, f in ipairs(fautes) do print("      " .. f) end
	if bloom then ok(ecartBloom < 1e-3, string.format("%s : bloom = aperçu (écart max %.4f)", nom, ecartBloom)) end
	if rec.flashs then ok(ecartFlash < 1e-3, string.format("%s : flash d'écran = aperçu (écart max %.4f)", nom, ecartFlash)) end

	-- les émissions tombent au bon instant, jamais avant (le bug « impact avant la collision »)
	local avant = 0
	for _, L in ipairs(rec.couches) do
		if L.type == "particules" and L.emit then
			local pe = nil
			for _, d in ipairs(tous) do
				if d.ClassName == "ParticleEmitter" and d.Name == L.nom and #d._emis > 0 and d._verif == nil then pe = d; d._verif = true; break end
			end
			if not pe then ok(false, nom .. "/" .. L.nom .. " : jamais émis"); continue end
			local e = pe._emis[1]
			if e.t < L.t0 - 1e-9 or e.t > L.t0 + 1 / 60 + 1e-9 or e.n ~= L.emit then avant += 1
				print(string.format("      %s émis à %.3f (attendu %.3f), n=%d", L.nom, e.t, L.t0, e.n)) end
		end
	end
	ok(avant == 0, nom .. " : chaque Emit tombe dans l'image de son t0, avec le bon nombre")
	if rec.gels then
		local g = rec.gels[1]
		ok(gelVu and math.abs(gelVu - (g[1] + g[2])) < 2 / 60 + 1e-9 or false,
			string.format("%s : gel TimeScale 0 de %.2f à %.2f s", nom, g[1], g[1] + g[2]))
		local halo = trouver(dossier, "halo_orbe")
		ok(halo == nil or halo.TimeScale ~= 0, nom .. " : la couche gel=false n'est pas gelée")
	end
	if rec.projectile then
		local P = rec.projectile
		local p0 = positionsProjectile[math.floor(P.t0 * 60 + 0.5)]
		local p1 = positionsProjectile[math.floor(P.t1 * 60 + 0.5)]
		ok(p0 and (p0 - Vector3.new(P.de[1], P.de[2], P.de[3])).Magnitude < 1e-3 or false, nom .. " : projectile part de « de »")
		ok(p1 and (p1 - Vector3.new(P.a[1], P.a[2], P.a[3])).Magnitude < 1e-3 or false, nom .. " : projectile arrive sur « a » à t1")
		local asp = trouver(dossier, "aspiration")
		if asp then ok(asp.ShapeInOut == "ParticleEmitterShapeInOut.Inward" and asp.Speed.Min > 0, nom .. " : aspiration = forme Inward, vitesse positive") end
	end
	ok(dossier._detruit == true, nom .. " : tout est nettoyé à la fin (" .. string.format("%.2f", h.Duree) .. " s)")
	ok(trouver(lighting, "VFX_Bloom") == nil, nom .. " : BloomEffect retiré")
	ok((cam.CFrame.Position - Vector3.new(0, 5, 10)).Magnitude < 1e-9, nom .. " : caméra rendue à sa place après la secousse")
end

-- 4. sons : sans identifiant, rien ; avec identifiant, chaque Sound part à son t0
do
	local rec = DATA.recettes.orbe_impact
	local h0 = VFXStudio.jouer(rec, CFrame.new(0, 0, 0), { manuel = true })
	local n0 = 0
	for _, d in ipairs(h0.Dossier:GetDescendants()) do if d.ClassName == "Sound" then n0 += 1 end end
	ok(n0 == 0, "sans rbxassetid, aucun son inventé")
	h0.Annuler()
	local ids = {}
	-- (les sons sans identifiant valent nil dans DATA.assets.sons : on prend les noms de la recette)
	for _, so in ipairs(rec.sons) do ids[so.son] = "rbxassetid://1" end
	VFXStudio.configurer({ sons = ids })
	local h = VFXStudio.jouer(rec, CFrame.new(0, 0, 0), { manuel = true })
	local joues = {}
	for i = 0, math.ceil(rec.duree * 60) do
		TEMPS = i / 60
		h._etape(TEMPS)
		if h.Dossier._detruit then break end
		for _, d in ipairs(h.Dossier:GetDescendants()) do
			if d.ClassName == "Sound" and d._joue and not joues[d.Name] then joues[d.Name] = d._joue end
		end
	end
	local bons = 0
	for _, s in ipairs(rec.sons) do
		local t = joues[s.son]
		if t and t >= s.t0 - 1e-9 and t <= s.t0 + 1 / 60 + 1e-9 then bons += 1 else print("      " .. s.son .. " joué à " .. tostring(t)) end
	end
	ok(bons == #rec.sons, string.format("chaque son part dans l'image de son t0 (%d/%d)", bons, #rec.sons))
	VFXStudio.configurer({ sons = {} })
end

-- 5. Annuler au milieu (technique interrompue)
do
	local rec = DATA.recettes.orbe_impact
	local h = VFXStudio.jouer(rec, CFrame.new(10, 0, 0), { manuel = true })
	h._etape(0.5)
	h.Annuler()
	ok(h.Dossier._detruit == true and trouver(lighting, "VFX_Bloom") == nil, "Annuler() nettoie tout en cours de route")
	-- repère : la recette est jouée à l'endroit donné
	local h2 = VFXStudio.jouer(rec, CFrame.new(10, 0, 0) * CFrame.Angles(0, math.pi / 2, 0), { manuel = true })
	h2._etape(rec.projectile.t1)
	local mv = trouver(h2.Dossier, "M_projectile")
	local attendu = CFrame.new(10, 0, 0) * CFrame.Angles(0, math.pi / 2, 0) * Vector3.new(rec.projectile.a[1], rec.projectile.a[2], rec.projectile.a[3])
	ok(mv and (mv.CFrame.Position - attendu).Magnitude < 1e-3 or false, "le repère (CFrame) déplace et tourne tout l'effet")
	h2.Annuler()
end

print(echecs == 0 and "TOUT OK" or (echecs .. " ÉCHEC(S)"))
