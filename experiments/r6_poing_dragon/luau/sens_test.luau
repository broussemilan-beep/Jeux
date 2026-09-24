--[[
	Test du SENS de DragonFist.luau (mocks repris du test M1), execute par l'interpreteur Luau officiel.
	CFrame/Vector3 minimaux, conventions Roblox : repere droit, Y en haut,
	LookVector = -Z (colonne Z negee), CFrame.Angles(rx, ry, rz) = Rx*Ry*Rz,
	CFrame.lookAt(eye, cible) : -Z vers la cible, Y proche de +Y monde.
	Lancer : python3 run_sens_test.py (assemble mocks + module + tests)
]]

local V = {}
V.__index = V
local function v3(x, y, z) return setmetatable({ X = x, Y = y, Z = z }, V) end
V.__add = function(a, b) return v3(a.X + b.X, a.Y + b.Y, a.Z + b.Z) end
V.__sub = function(a, b) return v3(a.X - b.X, a.Y - b.Y, a.Z - b.Z) end
V.__mul = function(a, k) return v3(a.X * k, a.Y * k, a.Z * k) end
V.__index = function(t, k)
	if k == "Magnitude" then return math.sqrt(t.X * t.X + t.Y * t.Y + t.Z * t.Z) end
	if k == "Unit" then local m = math.sqrt(t.X * t.X + t.Y * t.Y + t.Z * t.Z); return v3(t.X / m, t.Y / m, t.Z / m) end
	return rawget(V, k)
end
local function cross(a, b) return v3(a.Y * b.Z - a.Z * b.Y, a.Z * b.X - a.X * b.Z, a.X * b.Y - a.Y * b.X) end
Vector3 = { new = v3 }

local C = {}
local function cf(p, r) return setmetatable({ p = p, r = r }, C) end -- r[i][j], colonnes = axes X, Y, Z
local function col(r, j) return v3(r[1][j], r[2][j], r[3][j]) end
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
C.__sub = function(a, v) return cf(a.p - v, a.r) end
C.__index = function(t, k)
	if k == "Position" then return t.p end
	if k == "LookVector" then return col(t.r, 3) * -1 end
	if k == "RightVector" then return col(t.r, 1) end
	if k == "UpVector" then return col(t.r, 2) end
	if k == "VectorToWorldSpace" then return function(self, v) return rotv(self.r, v) end end
	return nil
end
CFrame = {
	new = function(x, y, z)
		if type(x) == "table" then return cf(x, I) end
		return cf(v3(x, y, z), I)
	end,
	Angles = function(rx, ry, rz)
		local cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
		local Rx = { { 1, 0, 0 }, { 0, cx, -sx }, { 0, sx, cx } }
		local Ry = { { cy, 0, sy }, { 0, 1, 0 }, { -sy, 0, cy } }
		local Rz = { { cz, -sz, 0 }, { sz, cz, 0 }, { 0, 0, 1 } }
		return cf(v3(0, 0, 0), matmul(matmul(Rx, Ry), Rz))
	end,
	lookAt = function(eye, target)
		local f = (target - eye).Unit
		local zc = f * -1
		local xc = cross(v3(0, 1, 0), zc).Unit
		local yc = cross(zc, xc)
		return cf(eye, { { xc.X, yc.X, zc.X }, { xc.Y, yc.Y, zc.Y }, { xc.Z, yc.Z, zc.Z } })
	end,
}
-- services factices (le module les demande au chargement)
local game = { GetService = function() return {} end }
local workspace = {}
local Color3 = { fromRGB = function(r, g, b) return { r, g, b } end }

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

-- 1. placement : victime devant, tournee vers l'attaquant, meme si l'attaquant est tourne
local att = CFrame.new(0, 3, 0)
local vic = DragonFist.victimCFrame(att, DATA.DISTANCE)
near(vic.Position, v3(0, 3, -DATA.DISTANCE), nil, "victime DEVANT l'attaquant (z = -distance)")
near(vic.LookVector, v3(0, 0, 1), nil, "victime tournee VERS l'attaquant")
local att2 = CFrame.new(10, 8, 5) * CFrame.Angles(0, math.rad(90), 0)
local vic2 = DragonFist.victimCFrame(att2, DATA.DISTANCE)
near((vic2.Position - att2.Position).Unit, att2.LookVector, nil, "attaquant tourne de 90 deg : victime toujours devant")

-- 2. repere de scene : origine AU SOL sous le HumanoidRootPart
near(DragonFist.toWorld(att2, { 0, 3, 0 }), att2.Position, nil, "point (0,3,0) de la scene = HumanoidRootPart en jeu")
near(DragonFist.toWorld(att2, { 0, 0, 0 }), att2.Position - v3(0, 3, 0), nil, "origine de la scene = sol sous l'attaquant")
near(DragonFist.toWorld(att2, { 0, 3, -5 }), att2.Position + att2.LookVector * 5, nil, "scene -Z = devant l'attaquant tourne")

-- 3. effets : les coups partent vers l'avant, le cratere est devant
for _, e in DATA.EVENTS do
	if e.kind == "impact" and e.name ~= "impact" then
		local d = DragonFist.dirToWorld(att2, e.dir)
		check(dot(d, att2.LookVector) > 0.2 or e.name == "strike", "impact " .. e.name .. " : sens du coup vers l'avant de l'attaquant")
	end
	if e.kind == "crater" then
		local p = DragonFist.toWorld(att2, e.pos)
		check(dot(p - att2.Position, att2.LookVector) > 4, "cratere DEVANT l'attaquant")
		check(math.abs(p.Y - (att2.Position.Y - 3)) < 0.05, "cratere AU SOL (pas a hauteur de hanche)")
	end
	if e.kind == "impact" and e.name == "strike" then
		local d = DragonFist.dirToWorld(att2, e.dir)
		check(d.Y < -0.5, "frappe en l'air : le poing va VERS LE BAS")
	end
end

-- 4. camera : exacte sur chaque cle, tenue avant une coupe, continue ailleurs
for i, k in DATA.CAMERA do
	local eye, look = DragonFist.cameraAt(DATA, k.f)
	near(eye, v3(k.eye[1], k.eye[2], k.eye[3]), 1e-6, "camera cle f" .. k.f .. " : oeil exact")
	if i > 1 and k.cut then
		local e2 = DragonFist.cameraAt(DATA, k.f - 1e-3)
		local p = DATA.CAMERA[i - 1]
		check((e2 - v3(p.eye[1], p.eye[2], p.eye[3])).Magnitude < 1e-6 or not DATA.CAMERA[i - 1], "coupe f" .. k.f .. " : plan precedent tenu jusqu'a la coupe")
	elseif i > 1 then
		local e2 = DragonFist.cameraAt(DATA, k.f - 1e-3)
		check((e2 - eye).Magnitude < 0.05, "f" .. k.f .. " : pas de saut de camera hors coupe")
	end
end
local e0, l0 = DragonFist.cameraAt(DATA, 0)
check(e0.X > 3, "premier plan : camera sur la DROITE de l'attaquant (+X)")
check(dot((l0 - e0).Unit, v3(-1, 0, 0)) > 0.6, "premier plan : elle regarde vers le combat")

-- 5. ordonnanceur : chaque evenement une seule fois, dans l'ordre, malgre les hitstops (frames figees)
local state = { next = 1 }
local fired, last = 0, -1
local ordered = true
local f = 0
while f <= DATA.END + 2 do
	for _, e in DragonFist.due(DATA, state, f) do
		fired += 1
		if e.frame < last then ordered = false end
		last = e.frame
	end
	-- simule un hitstop : la frame n'avance pas pendant 4 pas apres un multiple de 30
	if f % 30 == 0 and f > 0 and state.stall ~= f then state.stall = f else f += 1.3 end
end
check(fired == #DATA.EVENTS, "tous les evenements declenches une fois (" .. fired .. "/" .. #DATA.EVENTS .. ")")
check(ordered, "evenements declenches dans l'ordre des frames")

-- 6. fin : chaque HumanoidRootPart la ou son corps a fini, devant le depart
local fa, fv = DragonFist.finalCFrames(att2, DATA)
check(dot(fa.Position - att2.Position, att2.LookVector) > 4, "fin : attaquant replace dans le cratere (devant)")
check(dot(fv.Position - att2.Position, att2.LookVector) > 15, "fin : victime replacee au loin devant")
near(fv.LookVector, att2.LookVector * -1, 1e-6, "fin : victime toujours tournee vers l'attaquant")
check(math.abs(fa.Position.Y - att2.Position.Y) < 1e-6, "fin : hauteur de hanche conservee")

print(fails == 0 and "SENS OK" or ("SENS FAUX : " .. fails .. " echec(s)"))
