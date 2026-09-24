--[[
	Test du SENS de M1Technique.luau, execute par l'interpreteur Luau officiel.
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
C.__index = function(t, k)
	if k == "Position" then return t.p end
	if k == "LookVector" then return col(t.r, 3) * -1 end
	if k == "RightVector" then return col(t.r, 1) end
	if k == "UpVector" then return col(t.r, 2) end
	return nil
end
CFrame = {
	new = function(x, y, z) return cf(v3(x, y, z), I) end,
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

-- @@MODULE@@  (run_sens_test.py insere ici le source EXACT de M1Technique.luau)

local fails = 0
local function near(a, b, tol, what)
	local d = (a - b).Magnitude
	local ok = d < (tol or 1e-4)
	print(string.format("%s %-58s (%.3f, %.3f, %.3f)", ok and "OK  " or "FAUX", what, a.X, a.Y, a.Z))
	if not ok then fails += 1 end
end

-- attaquant a l'origine, regardant -Z (orientation par defaut de Roblox)
local att = CFrame.new(0, 3, 0)
near(att.LookVector, v3(0, 0, -1), nil, "avant de l'attaquant = -Z")
local vic = M1.victimCFrame(att)
near(vic.Position, v3(0, 3, -M1.CONFIG.DISTANCE), nil, "victime DEVANT l'attaquant (z = -distance)")
near(vic.LookVector, v3(0, 0, 1), nil, "victime tournee VERS l'attaquant (+Z)")
-- attaquant tourne de 90 deg a gauche : tout doit suivre
local att2 = CFrame.new(10, 3, 5) * CFrame.Angles(0, math.rad(90), 0)
local vic2 = M1.victimCFrame(att2)
near((vic2.Position - att2.Position).Unit, att2.LookVector, nil, "attaquant tourne : victime toujours devant lui")
near(vic2.LookVector, att2.LookVector * -1, nil, "attaquant tourne : victime toujours face a lui")

-- impact : Front (-Z) = sens du coup ; anneau d'axe = sens du coup
local dir = att.LookVector
local contact = v3(0.35, 3.38, -3.40)
local frame = M1.impactFrame(contact, dir)
near(frame.LookVector, dir, nil, "repere d'impact : Front = sens du coup (etincelles)")
local ring = M1.ringCFrame(frame)
near(ring.RightVector, dir, nil, "axe du cylindre (X) = sens du coup : anneau perpendiculaire")
near(ring.Position, contact + dir * 0.3, nil, "anneau 0,3 stud en avant du contact")
-- recul : dans le sens du coup, loin de l'attaquant
local kb = M1.knockbackCFrame(vic, dir)
near(kb.Position - vic.Position, dir * M1.CONFIG.KNOCKBACK, nil, "recul de la victime dans le sens du coup")
near(kb.LookVector, vic.LookVector, nil, "le recul ne tourne pas la victime")
local d0 = (vic.Position - att.Position).Magnitude
local d1 = (kb.Position - att.Position).Magnitude
print(string.format("%s distance attaquant-victime %.3f -> %.3f (doit AUGMENTER)", d1 > d0 and "OK  " or "FAUX", d0, d1))
if d1 <= d0 then fails += 1 end

print(fails == 0 and "SENS OK" or ("SENS FAUX : " .. fails .. " echec(s)"))
