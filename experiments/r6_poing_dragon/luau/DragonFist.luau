--!nonstrict
--[[
	DragonFist -- « Poing du Dragon », technique ultime (rig R6, 2 personnages).

	Anime par le cerveau d'animateur (experiments/_shared/animator_brain) sur
	deux rigs R6 IK+FK V2.22, exporte en KeyframeSequences a 60 i/s. La mise
	en scene (camera, effets, hitstops, planches manga) vient de
	DragonFistData, genere depuis staging.json : la MEME source que le
	lecteur HTML. Aucun delai code en dur : un ordonnanceur lit la position
	REELLE de la piste d'animation (TimePosition) et declenche chaque
	evenement a sa frame, hitstops compris.

	Deroule : rafale de 6 coups -> anticipation -> uppercut -> envol ->
	temps suspendu -> plongee (dragon de fumee doree) -> planches manga ->
	ecran blanc -> revelation du cratere.

	Mode cinematique : les deux HumanoidRootPart sont ANCRES pendant la
	technique ; tout le mouvement (sauts, projection) est dans le RootJoint
	de l'animation. A la fin, chaque HumanoidRootPart est replace la ou son
	corps a fini (sinon il reviendrait au point de depart).

	SENS : tout point P de DragonFistData est exprime dans le repere de
	l'attaquant AU LANCEMENT (origine = HumanoidRootPart, avant = -Z) ;
	en jeu il devient startCFrame * P (verifie par sens_test.luau).
]]

local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local KeyframeSequenceProvider = game:GetService("KeyframeSequenceProvider")

local DragonFist = {}

DragonFist.CONFIG = {
	-- IDs des 3 planches manga (output/manga_1..3.png) une fois importees
	-- dans Studio (Asset Manager). Vides : repli sur des images plein ecran
	-- noires/blanches, la technique fonctionne quand meme.
	MANGA_IDS = { "", "", "" },
	-- v6 : IDs des 3 cartes d'impact du coup charge (output/carte_1..3.png).
	-- Vides : repli noir / blanc / noir, la sequence garde son rythme.
	CARTE_IDS = { "", "", "" },
	CAMERA = true, -- camera cinematique pour le joueur qui lance la technique
	SCREEN_FX = true, -- barres, lignes de vitesse, manga, ecran blanc
	CLEANUP_TIME = 6, -- s : duree de vie du cratere et des debris apres la fin
	GOLD = Color3.fromRGB(255, 197, 61),
	GOLD_DEEP = Color3.fromRGB(255, 138, 31),
	WHITE = Color3.fromRGB(255, 246, 220),
	SMOKE = Color3.fromRGB(125, 116, 104),
}

-- textures integrees au client Roblox (aucun upload necessaire)
local TEX = {
	spark = "rbxasset://textures/particles/sparkles_main.dds",
	smoke = "rbxasset://textures/particles/smoke_main.dds",
	fire = "rbxasset://textures/particles/fire_main.dds",
}

local function color3(hex: string): Color3
	return Color3.fromHex(hex)
end

local function vec(t): Vector3
	return Vector3.new(t[1], t[2], t[3])
end

-- ------------------------------------------------------------------ geometrie pure (testee)

-- Victime DEVANT l'attaquant, tournee vers lui (meme placement qu'a l'export).
function DragonFist.victimCFrame(start: CFrame, distance: number): CFrame
	return start * CFrame.new(0, 0, -distance) * CFrame.Angles(0, math.pi, 0)
end

-- Hauteur du HumanoidRootPart au-dessus du sol (rig R6 standard) : le
-- repere de scene a son origine AU SOL, sous le HumanoidRootPart.
DragonFist.ROOT_Y = 3

-- Point du repere de scene -> monde. `start` = CFrame du HumanoidRootPart
-- de l'attaquant au lancement ; la scene est a l'origine au sol.
function DragonFist.toWorld(start: CFrame, p): Vector3
	return start * Vector3.new(p[1], p[2] - DragonFist.ROOT_Y, p[3])
end

-- Direction du repere de scene -> monde.
function DragonFist.dirToWorld(start: CFrame, d): Vector3
	return start:VectorToWorldSpace(vec(d))
end

local function catmull(p0: Vector3, p1: Vector3, p2: Vector3, p3: Vector3, u: number): Vector3
	local u2, u3 = u * u, u * u * u
	return (p1 * 2 + (p2 - p0) * u + (p0 * 2 - p1 * 5 + p2 * 4 - p3) * u2 + (p1 * 3 - p0 - p2 * 3 + p3) * u3) * 0.5
end

-- Camera a la frame `f` (fractionnaire) : (oeil, cible, fov) dans le repere
-- de scene. Une cle "cut" est une coupe franche ; entre deux cles douces,
-- Catmull-Rom (comme le lecteur HTML) ; le whip pan (cle 196) en ease-in-out.
function DragonFist.cameraAt(data, f: number)
	local K = data.CAMERA
	local i = 1
	while i + 1 <= #K and K[i + 1].f <= f do
		i += 1
	end
	local k1, k2 = K[i], K[i + 1]
	if not k2 or k2.cut then
		return vec(k1.eye), vec(k1.look), k1.fov
	end
	local u = (f - k1.f) / (k2.f - k1.f)
	if k1.f == data.WHIP_FRAME then
		u = if u < 0.5 then 4 * u * u * u else 1 - ((-2 * u + 2) ^ 3) / 2
	end
	local k0 = if i > 1 and not k1.cut then K[i - 1] else k1
	local k3 = if K[i + 2] and not K[i + 2].cut then K[i + 2] else k2
	local eye = catmull(vec(k0.eye), vec(k1.eye), vec(k2.eye), vec(k3.eye), u)
	local look = catmull(vec(k0.look), vec(k1.look), vec(k2.look), vec(k3.look), u)
	return eye, look, k1.fov + (k2.fov - k1.fov) * u
end

-- Ou replacer chaque HumanoidRootPart a la fin : la ou son corps a fini
-- (FINAL = positions du HumanoidRootPart dans le repere de scene) ;
-- l'attaquant garde son orientation, la victime reste tournee vers lui.
function DragonFist.finalCFrames(start: CFrame, data): (CFrame, CFrame)
	local a = CFrame.new(DragonFist.toWorld(start, data.FINAL.attacker)) * (start - start.Position)
	local v = CFrame.new(DragonFist.toWorld(start, data.FINAL.victim)) * (start - start.Position) * CFrame.Angles(0, math.pi, 0)
	return a, v
end

-- Ordonnanceur : evenements dont la frame est atteinte, dans l'ordre, une
-- seule fois chacun. `state.next` = index du prochain evenement.
function DragonFist.due(data, state, frame: number)
	local out = {}
	local E = data.EVENTS
	while state.next <= #E and E[state.next].frame <= frame do
		table.insert(out, E[state.next])
		state.next += 1
	end
	return out
end

-- ------------------------------------------------------------------ outils Roblox

local cachedIds: { [KeyframeSequence]: string } = {}

local function animationFor(kfs: KeyframeSequence): Animation
	local anim = Instance.new("Animation")
	local published = kfs:GetAttribute("AnimationId")
	if typeof(published) == "string" and published ~= "" then
		anim.AnimationId = published
	else
		if not cachedIds[kfs] then
			cachedIds[kfs] = KeyframeSequenceProvider:RegisterKeyframeSequence(kfs)
		end
		anim.AnimationId = cachedIds[kfs]
	end
	return anim
end

local function animatorOf(model: Model): Animator
	local humanoid = model:FindFirstChildOfClass("Humanoid") :: Humanoid
	local animator = humanoid:FindFirstChildOfClass("Animator")
	if not animator then
		animator = Instance.new("Animator")
		animator.Parent = humanoid
	end
	return animator :: Animator
end

local function holderAt(cf: CFrame, parent: Instance): (Part, Attachment)
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Transparency = 1
	p.Size = Vector3.new(0.1, 0.1, 0.1)
	p.CFrame = cf
	p.Parent = parent
	local a = Instance.new("Attachment")
	a.Parent = p
	return p, a
end

-- Emetteur desactive, joue par emitAll : convention des packs pro (corpus
-- VFX : 98 % des emetteurs desactives, attributs EmitCount / EmitDelay).
local function emitter(parent: Attachment, props: { [string]: any }, count: number, delay: number?): ParticleEmitter
	local e = Instance.new("ParticleEmitter")
	e.Enabled = false
	e.Rate = 0
	e.LightInfluence = 0
	e.Texture = TEX.spark
	for k, v in props do
		(e :: any)[k] = v
	end
	e:SetAttribute("EmitCount", count)
	e:SetAttribute("EmitDelay", delay or 0)
	e.Parent = parent
	return e
end

local function emitAll(root: Instance)
	for _, d in root:GetDescendants() do
		if d:IsA("ParticleEmitter") then
			local n = d:GetAttribute("EmitCount") or 1
			local delay = d:GetAttribute("EmitDelay") or 0
			if delay > 0 then
				task.delay(delay, function()
					d:Emit(n)
				end)
			else
				d:Emit(n)
			end
		end
	end
end

local function seq(points): NumberSequence
	local kps = {}
	for _, p in points do
		table.insert(kps, NumberSequenceKeypoint.new(p[1], p[2]))
	end
	return NumberSequence.new(kps)
end

-- ------------------------------------------------------------------ effets 3D
-- Dimensions : medianes du corpus VFX (pack 100 Combat VFX) x scale.

local function impact(ctx, ev)
	local cfg = DragonFist.CONFIG
	local pos = DragonFist.toWorld(ctx.start, ev.pos)
	local dir = DragonFist.dirToWorld(ctx.start, ev.dir)
	local s = ev.scale
	local holder, att = holderAt(CFrame.lookAt(pos, pos + dir), ctx.fx)
	local col = color3(ev.color)
	-- v6 hierarchie : tier 1 (coup de base) = eclat 2 f + un anneau blanc ;
	-- tier 2 = sans fumee ; tier 3 = complet
	local tier = ev.tier or 3
	-- flash : 0,1 s (mediane corpus 0,10 s) ; 2 f pour un coup de base
	local flashLife = if tier == 1 then 2 / 60 else 0.09
	emitter(att, {
		Color = ColorSequence.new(cfg.WHITE, col),
		LightEmission = 1,
		Brightness = 6,
		Lifetime = NumberRange.new(flashLife, flashLife),
		Speed = NumberRange.new(0),
		Size = seq({ { 0, 1.2 * s }, { 0.2, 4.2 * s }, { 1, 0 } }),
		Rotation = NumberRange.new(0, 360),
		ZOffset = 2,
	}, 2)
	-- etincelles : VelocityParallel, ~75 studs/s, drag 5 (freinage)
	emitter(att, {
		Color = ColorSequence.new(cfg.WHITE, col),
		LightEmission = 1,
		Brightness = 4,
		EmissionDirection = Enum.NormalId.Front,
		SpreadAngle = Vector2.new(42, 42),
		Speed = NumberRange.new(45 * math.min(1.6, s), 95 * math.min(1.6, s)),
		Drag = 5,
		Lifetime = NumberRange.new(0.18, 0.43),
		Orientation = Enum.ParticleOrientation.VelocityParallel,
		Size = seq({ { 0, 0.3 * math.min(1.4, s) }, { 1, 0 } }),
		Squash = seq({ { 0, 2.2 }, { 1, 1 } }),
		ZOffset = 1,
	}, if tier >= 2 then math.floor(10 + 10 * s) else 0)
	-- fumee : 1 s, drag 5,4 (la couche qui manquait a nos M1)
	emitter(att, {
		Texture = TEX.smoke,
		Color = ColorSequence.new(Color3.fromRGB(217, 210, 195)),
		LightEmission = 0,
		EmissionDirection = Enum.NormalId.Front,
		SpreadAngle = Vector2.new(80, 80),
		Speed = NumberRange.new(6 * s, 16 * s),
		Drag = 5.4,
		Lifetime = NumberRange.new(0.7, 1.2),
		Size = seq({ { 0, 1 * s }, { 1, 3.2 * s } }),
		Transparency = seq({ { 0, 0.45 }, { 1, 1 } }),
		Rotation = NumberRange.new(0, 360),
		RotSpeed = NumberRange.new(-30, 30),
	}, if tier >= 3 then math.floor(4 + 5 * s) else 0)
	emitAll(holder)
	-- onde : anneau perpendiculaire au coup, 0,32 s (tier 1 : l'anneau blanc seul)
	local rings = if tier >= 2 then { { 0.32, 5.5 * s, 0.1 }, { 0.2, 3.2 * s, 0 } } else { { 0.2, 3.2 * s, 0 } }
	for _, r in rings do
		local ring = Instance.new("Part")
		ring.Shape = Enum.PartType.Cylinder
		ring.Anchored = true
		ring.CanCollide = false
		ring.CanQuery = false
		ring.CanTouch = false
		ring.CastShadow = false
		ring.Material = Enum.Material.Neon
		ring.Color = if r[3] > 0 then col else cfg.WHITE
		ring.Transparency = 0.1
		ring.Size = Vector3.new(0.1, 0.6, 0.6)
		-- le cylindre a son axe sur X : tourne de 90 deg, l'axe passe sur -Z = sens du coup
		ring.CFrame = CFrame.lookAt(pos, pos + dir) * CFrame.new(0, 0, -0.25) * CFrame.Angles(0, math.rad(90), 0)
		ring.Parent = ctx.fx
		TweenService:Create(ring, TweenInfo.new(r[1], Enum.EasingStyle.Cubic, Enum.EasingDirection.Out), {
			Size = Vector3.new(0.04, r[2], r[2]),
			Transparency = 1,
		}):Play()
		Debris:AddItem(ring, r[1] + 0.05)
	end
	Debris:AddItem(holder, 2)
	-- hitstop : les deux pistes se figent, les effets continuent
	if ev.hitstop > 0 then
		ctx.hitstop(ev.hitstop)
	end
	ctx.shake(ev.shake, if ev.name == "impact" then 10 else 6 * math.min(1.2, s))
end

local function bodyFlash(ctx, ev)
	local h = Instance.new("Highlight")
	h.Adornee = ctx.attacker
	h.FillColor = color3(ev.color)
	h.FillTransparency = 0
	h.OutlineTransparency = 1
	h.DepthMode = Enum.HighlightDepthMode.Occluded
	h.Parent = ctx.fx
	Debris:AddItem(h, ev.frames / 60)
end

local function groundBurst(ctx, ev)
	local pos = DragonFist.toWorld(ctx.start, ev.pos)
	local col = color3(ev.color)
	-- etoile a pointes posee au sol : 12 lames neon qui jaillissent et s'effacent
	for i = 1, 12 do
		local a = (i / 12) * math.pi * 2
		local len = (if i % 2 == 0 then 3.2 else 2.0) * ev.scale
		local blade = Instance.new("Part")
		blade.Anchored = true
		blade.CanCollide = false
		blade.CanQuery = false
		blade.CanTouch = false
		blade.CastShadow = false
		blade.Material = Enum.Material.Neon
		blade.Color = col
		blade.Size = Vector3.new(0.35, 0.05, 0.2)
		local cf = CFrame.new(pos + Vector3.new(0, 0.06, 0)) * CFrame.Angles(0, a, 0)
		blade.CFrame = cf
		blade.Parent = ctx.fx
		TweenService:Create(blade, TweenInfo.new(0.22, Enum.EasingStyle.Cubic, Enum.EasingDirection.Out), {
			Size = Vector3.new(0.05, 0.05, len),
			CFrame = cf * CFrame.new(0, 0, -len / 2),
			Transparency = 1,
		}):Play()
		Debris:AddItem(blade, 0.3)
	end
	local holder, att = holderAt(CFrame.new(pos + Vector3.new(0, 0.4, 0)), ctx.fx)
	emitter(att, {
		Texture = TEX.smoke,
		Color = ColorSequence.new(Color3.fromRGB(207, 198, 182)),
		EmissionDirection = Enum.NormalId.Top,
		SpreadAngle = Vector2.new(85, 85),
		Speed = NumberRange.new(5, 9),
		Drag = 4,
		Lifetime = NumberRange.new(0.6, 0.9),
		Size = seq({ { 0, 1.4 }, { 1, 3.6 } }),
		Transparency = seq({ { 0, 0.5 }, { 1, 1 } }),
	}, 12)
	emitAll(holder)
	Debris:AddItem(holder, 1.5)
end

-- emetteur CONTINU attache a une partie, coupe apres `frames`
local function sustained(ctx, part: BasePart, offset: CFrame, props, frames: number): Attachment
	local a = Instance.new("Attachment")
	a.CFrame = offset
	a.Parent = part
	local e = Instance.new("ParticleEmitter")
	e.LightInfluence = 0
	for k, v in props do
		(e :: any)[k] = v
	end
	e.Parent = a
	task.delay(frames / 60, function()
		e.Enabled = false
	end)
	Debris:AddItem(a, frames / 60 + 1.5)
	table.insert(ctx.cleanup, a)
	return a
end

local function aura(ctx, ev)
	local torso = ctx.attacker:FindFirstChild("Torso") :: BasePart
	sustained(ctx, torso, CFrame.new(0, -0.8, 0), {
		Texture = TEX.fire,
		Color = ColorSequence.new(color3(ev.color), DragonFist.CONFIG.WHITE),
		LightEmission = 1,
		Brightness = 3,
		Rate = 60 * ev.intensity,
		Lifetime = NumberRange.new(0.4, 0.6),
		Speed = NumberRange.new(2, 4),
		SpreadAngle = Vector2.new(25, 25),
		EmissionDirection = Enum.NormalId.Top,
		Acceleration = Vector3.new(0, 6, 0),
		Size = seq({ { 0, 1.2 }, { 1, 0 } }),
		Transparency = seq({ { 0, 0.3 }, { 1, 1 } }),
		LockedToPart = true,
	}, ev.frames)
end

local function fistGlow(ctx, ev)
	local arm = ctx.attacker:FindFirstChild(if ev.side == "R" then "Right Arm" else "Left Arm") :: BasePart
	local a = sustained(ctx, arm, CFrame.new(0, -1, 0), {
		Color = ColorSequence.new(DragonFist.CONFIG.WHITE, color3(ev.color)),
		LightEmission = 1,
		Brightness = 5,
		Rate = 40,
		Lifetime = NumberRange.new(0.15, 0.25),
		Speed = NumberRange.new(0),
		Size = seq({ { 0, 2.2 }, { 1, 0 } }),
		Rotation = NumberRange.new(0, 360),
		LockedToPart = true,
	}, ev.frames)
	local light = Instance.new("PointLight")
	light.Color = color3(ev.color)
	light.Range = 9
	light.Brightness = 3
	light.Parent = a
end

-- DRAGON : trois attaches qui tournent en helice autour du bras droit, de
-- l'epaule au poing, chacune avec une trainee (or, blanc, fumee sombre) --
-- les trainees dessinent des rubans enroules, de plus en plus vite.
local function dragon(ctx, ev)
	local arm = ctx.attacker:FindFirstChild("Right Arm") :: BasePart
	local trails = {}
	local specs = {
		{ phase = 0, color = color3(ev.color), width = 0.5, light = 1 },
		{ phase = 0.4, color = DragonFist.CONFIG.WHITE, width = 0.2, light = 1 },
		{ phase = math.pi, color = color3(ev.smoke), width = 0.9, light = 0 },
	}
	for _, sp in specs do
		local a0, a1 = Instance.new("Attachment"), Instance.new("Attachment")
		a0.Parent, a1.Parent = arm, arm
		local t = Instance.new("Trail")
		t.Attachment0, t.Attachment1 = a0, a1
		t.Color = ColorSequence.new(sp.color)
		t.LightEmission = sp.light
		t.LightInfluence = 0
		t.Lifetime = 0.18
		t.FaceCamera = true
		t.Transparency = seq({ { 0, 0.05 }, { 1, 1 } })
		t.Parent = arm
		table.insert(trails, { a0 = a0, a1 = a1, t = t, sp = sp })
		table.insert(ctx.cleanup, a0)
		table.insert(ctx.cleanup, a1)
		table.insert(ctx.cleanup, t)
	end
	local t0 = os.clock()
	local dur = ev.frames / 60
	ctx.bind("dragon", function()
		local age = os.clock() - t0
		if age > dur then
			for _, k in trails do
				k.t.Enabled = false
			end
			return false
		end
		local spin = age * (9 + 10 * math.min(1, age / dur))
		for _, k in trails do
			-- position le long du bras (Y local : +1 epaule -> -1 poing), rayon qui se resserre
			local u = (age * 1.7 + k.sp.phase / (math.pi * 2)) % 1
			local y = 1 - 2.6 * u
			local r = 0.9 - 0.55 * u
			local a = spin + k.sp.phase + u * math.pi * 6.4
			local c = Vector3.new(math.cos(a) * r, y, math.sin(a) * r)
			local w = k.sp.width
			k.a0.Position = c + Vector3.new(0, w / 2, 0)
			k.a1.Position = c - Vector3.new(0, w / 2, 0)
		end
		return true
	end)
end

local function crater(ctx, ev)
	local center = DragonFist.toWorld(ctx.start, ev.pos)
	local rng = Random.new(ev.seed)
	local model = Instance.new("Model")
	model.Name = "Crater"
	model.Parent = ctx.fx
	-- cicatrice sombre au sol
	local scar = Instance.new("Part")
	scar.Shape = Enum.PartType.Cylinder
	scar.Anchored, scar.CanCollide = true, false
	scar.Material = Enum.Material.Slate
	scar.Color = Color3.fromRGB(34, 30, 27)
	scar.Size = Vector3.new(0.12, ev.radius * 1.45, ev.radius * 1.45)
	scar.CFrame = CFrame.new(center + Vector3.new(0, 0.02, 0)) * CFrame.Angles(0, 0, math.rad(90))
	scar.Parent = model
	-- pics de pierre qui sortent du sol en 0,12 s, inclines vers l'exterieur
	for i = 1, ev.spikes do
		local outer = i > ev.spikes * 0.45
		local a = rng:NextNumber(0, math.pi * 2)
		local r = ev.radius * (if outer then rng:NextNumber(0.75, 1.1) else rng:NextNumber(0.45, 0.73))
		local h = (if outer then 1.4 else 2.4) + rng:NextNumber(0, 1.8)
		local w = rng:NextNumber(0.6, 1.3)
		local base = center + Vector3.new(math.cos(a) * r, 0, math.sin(a) * r)
		local tilt = rng:NextNumber(0.35, 0.7)
		local rot = CFrame.lookAt(base, base + Vector3.new(math.cos(a), 0, math.sin(a))) * CFrame.Angles(-tilt, 0, rng:NextNumber(0, 6))
		local spike = Instance.new("Part")
		spike.Anchored = true
		spike.CanCollide = true
		spike.Material = Enum.Material.Slate
		spike.Color = if rng:NextNumber() < 0.5 then Color3.fromRGB(119, 112, 106) else Color3.fromRGB(91, 85, 80)
		spike.Size = Vector3.new(w, h, w)
		spike.CFrame = rot * CFrame.new(0, -h / 2, 0)
		spike.Parent = model
		TweenService:Create(spike, TweenInfo.new(0.12, Enum.EasingStyle.Cubic, Enum.EasingDirection.Out, 0, false, r / ev.radius * 0.08), {
			CFrame = rot * CFrame.new(0, h * 0.12, 0),
		}):Play()
	end
	-- debris physiques
	for _ = 1, 26 do
		local d = Instance.new("Part")
		d.Size = Vector3.new(rng:NextNumber(0.35, 0.85), rng:NextNumber(0.3, 0.7), rng:NextNumber(0.35, 0.85))
		d.Material = Enum.Material.Slate
		d.Color = Color3.fromRGB(91, 85, 80)
		d.CFrame = CFrame.new(center + Vector3.new(0, 0.8, 0))
		d.Parent = model
		local a = rng:NextNumber(0, math.pi * 2)
		d.AssemblyLinearVelocity = Vector3.new(math.cos(a) * rng:NextNumber(8, 20), rng:NextNumber(14, 30), math.sin(a) * rng:NextNumber(8, 20))
		d.AssemblyAngularVelocity = Vector3.new(rng:NextNumber(-9, 9), rng:NextNumber(-9, 9), rng:NextNumber(-9, 9))
	end
	ctx.leftovers(model)
end

-- DOME : onde de choc en demi-sphere + mur de poussiere au ras du sol (v2 :
-- l'impact final se VOIT avant les planches manga, LECONS.md 3)
local function dome(ctx, ev)
	local pos = DragonFist.toWorld(ctx.start, ev.pos)
	local dur = ev.frames / 60
	local ball = Instance.new("Part")
	ball.Shape = Enum.PartType.Ball
	ball.Anchored, ball.CanCollide, ball.CanQuery, ball.CanTouch = true, false, false, false
	ball.CastShadow = false
	ball.Material = Enum.Material.ForceField
	ball.Color = color3(ev.color)
	ball.Transparency = 0.2
	ball.Size = Vector3.new(1, 1, 1)
	ball.CFrame = CFrame.new(pos)
	ball.Parent = ctx.fx
	TweenService:Create(ball, TweenInfo.new(dur, Enum.EasingStyle.Cubic, Enum.EasingDirection.Out), {
		Size = Vector3.new(ev.radius * 2, ev.radius * 1.6, ev.radius * 2),
		Transparency = 1,
	}):Play()
	Debris:AddItem(ball, dur + 0.1)
	local holder, att = holderAt(CFrame.new(pos + Vector3.new(0, 0.6, 0)), ctx.fx)
	emitter(att, {
		Texture = TEX.smoke,
		Color = ColorSequence.new(Color3.fromRGB(189, 179, 163)),
		EmissionDirection = Enum.NormalId.Top,
		SpreadAngle = Vector2.new(88, 88),
		Speed = NumberRange.new(28, 40),
		Drag = 3.5,
		Lifetime = NumberRange.new(2.5, 3.5),
		Size = seq({ { 0, 2.2 }, { 1, 5 } }),
		Transparency = seq({ { 0, 0.3 }, { 1, 1 } }),
		Acceleration = Vector3.new(0, -2, 0),
	}, 36)
	emitAll(holder)
	ctx.leftovers(holder)
end

local function smokeCloud(ctx, ev)
	local pos = DragonFist.toWorld(ctx.start, ev.pos)
	local holder, att = holderAt(CFrame.new(pos + Vector3.new(0, 1, 0)), ctx.fx)
	emitter(att, {
		Texture = TEX.smoke,
		Color = ColorSequence.new(color3(ev.color)),
		EmissionDirection = Enum.NormalId.Top,
		SpreadAngle = Vector2.new(90, 90),
		Speed = NumberRange.new(10, 26),
		Drag = 2.2,
		Lifetime = NumberRange.new(3.5, 5),
		Size = seq({ { 0, 3 }, { 1, 8 } }),
		Transparency = seq({ { 0, 0.35 }, { 0.6, 0.6 }, { 1, 1 } }),
		Rotation = NumberRange.new(0, 360),
		RotSpeed = NumberRange.new(-10, 10),
		Acceleration = Vector3.new(0, 0.8, 0),
	}, 46)
	emitAll(holder)
	ctx.leftovers(holder)
end

local function embers(ctx, ev)
	local pos = DragonFist.toWorld(ctx.start, ev.pos)
	local holder = holderAt(CFrame.new(pos + Vector3.new(0, 0.3, 0)), ctx.fx)
	local e = Instance.new("ParticleEmitter")
	e.Texture = TEX.spark
	e.Color = ColorSequence.new(color3(ev.color))
	e.LightEmission = 1
	e.LightInfluence = 0
	e.Rate = 25
	e.Lifetime = NumberRange.new(2, 3)
	e.Speed = NumberRange.new(1.5, 3)
	e.SpreadAngle = Vector2.new(60, 60)
	e.EmissionDirection = Enum.NormalId.Top
	e.Shape = Enum.ParticleEmitterShape.Box
	e.Size = seq({ { 0, 0.25 }, { 1, 0 } })
	holder.Size = Vector3.new(12, 0.1, 12)
	e.Parent = holder -- forme boite : la surface de la part (le cratere)
	task.delay(ev.frames / 60, function()
		e.Enabled = false
	end)
	ctx.leftovers(holder)
end

local function dustTrail(ctx, ev)
	for _, legName in { "Left Leg", "Right Leg" } do
		local leg = ctx.attacker:FindFirstChild(legName) :: BasePart
		sustained(ctx, leg, CFrame.new(0, -1, 0), {
			Texture = TEX.smoke,
			Color = ColorSequence.new(Color3.fromRGB(203, 194, 178)),
			Rate = 22,
			Lifetime = NumberRange.new(0.6, 0.9),
			Speed = NumberRange.new(1, 2),
			Size = seq({ { 0, 0.8 }, { 1, 2.6 } }),
			Transparency = seq({ { 0, 0.45 }, { 1, 1 } }),
		}, ev.frames)
	end
end

-- ------------------------------------------------------------------ effets ecran

-- Phase de la sequence de cartes a l'age reel `age` (s) : { kind, i, u } ou
-- nil hors sequence. Meme regle que le lecteur HTML (cartePhase).
function DragonFist.cartePhase(ev, age: number)
	if age < 0 then
		return nil
	end
	local t, ci = 0, 0
	for _, step in ev.sequence do
		local kind, d = step[1], step[2]
		if kind == "carte" then
			ci += 1
		end
		if age < t + d then
			return { kind = kind, i = ci, u = (age - t) / d }
		end
		t += d
	end
	if age < t + ev.fade then
		return { kind = "fondu", i = ci, u = (age - t) / ev.fade }
	end
	return nil
end

local function screen(ctx)
	local player = Players.LocalPlayer
	if not player or not DragonFist.CONFIG.SCREEN_FX then
		return nil
	end
	local gui = Instance.new("ScreenGui")
	gui.Name = "DragonFistScreen"
	gui.IgnoreGuiInset = true
	gui.DisplayOrder = 50
	gui.ResetOnSpawn = false
	gui.Parent = player:WaitForChild("PlayerGui")
	local function frame(name, color, z)
		local f = Instance.new("Frame")
		f.Name = name
		f.BorderSizePixel = 0
		f.BackgroundColor3 = color
		f.Size = UDim2.fromScale(1, 1)
		f.BackgroundTransparency = 1
		f.ZIndex = z
		f.Parent = gui
		return f
	end
	local bars = {}
	for i, y in { 0, 0.93 } do
		local b = frame("Bar" .. i, Color3.new(0, 0, 0), 1)
		b.Size = UDim2.fromScale(1, 0.07)
		b.Position = UDim2.fromScale(0, y)
		b.BackgroundTransparency = 0
		table.insert(bars, b)
	end
	local tint = frame("Tint", Color3.fromRGB(255, 190, 60), 2)
	local white = frame("White", Color3.fromRGB(255, 253, 246), 5)
	local manga = Instance.new("ImageLabel")
	manga.Name = "Manga"
	manga.Size = UDim2.fromScale(1, 1)
	manga.BackgroundColor3 = Color3.new(0, 0, 0)
	manga.BorderSizePixel = 0
	manga.ScaleType = Enum.ScaleType.Crop
	manga.Visible = false
	manga.ZIndex = 6
	manga.Parent = gui
	-- v6 fond de vitesse : lignes de concentration a la peripherie (le centre
	-- reste lisible), voile sombre
	local vitesse = frame("Vitesse", Color3.fromRGB(20, 16, 10), 3)
	local rng = Random.new(90)
	for _ = 1, 48 do
		local a = rng:NextNumber(0, math.pi * 2)
		local r0 = rng:NextNumber(0.32, 0.5)
		local line = Instance.new("Frame")
		line.BorderSizePixel = 0
		line.BackgroundColor3 = Color3.fromRGB(255, 248, 230)
		-- une Frame tourne autour de son CENTRE : on place le centre du trait
		-- a mi-longueur (unites : hauteur d'ecran, 16:9)
		local d = r0 + 0.35
		line.AnchorPoint = Vector2.new(0.5, 0.5)
		line.Size = UDim2.new(0.4, 0, 0, rng:NextInteger(2, 6))
		line.Position = UDim2.fromScale(0.5 + math.cos(a) * d * 9 / 16, 0.5 + math.sin(a) * d)
		line.Rotation = math.deg(a)
		line.ZIndex = 3
		line.Parent = vitesse
	end
	vitesse.Visible = false
	-- v6 cartes d'impact : noir + etoile, 3 cartes (ImageLabel), puis le blanc
	local cartes = Instance.new("ImageLabel")
	cartes.Name = "Cartes"
	cartes.Size = UDim2.fromScale(1, 1)
	cartes.BackgroundColor3 = Color3.new(0, 0, 0)
	cartes.BorderSizePixel = 0
	cartes.ScaleType = Enum.ScaleType.Crop
	cartes.Visible = false
	cartes.ZIndex = 6
	cartes.Parent = gui
	local star = Instance.new("Frame")
	star.Name = "Etoile"
	star.BackgroundTransparency = 1
	star.AnchorPoint = Vector2.new(0.5, 0.5)
	star.Position = UDim2.fromScale(0.5, 0.5)
	star.SizeConstraint = Enum.SizeConstraint.RelativeYY
	star.ZIndex = 7
	star.Parent = cartes
	for _, rot in { 0, 90 } do
		local blade = Instance.new("Frame")
		blade.BorderSizePixel = 0
		blade.BackgroundColor3 = Color3.new(1, 1, 1)
		blade.AnchorPoint = Vector2.new(0.5, 0.5)
		blade.Position = UDim2.fromScale(0.5, 0.5)
		blade.Size = UDim2.fromScale(1, 0.08)
		blade.Rotation = rot + 17
		blade.ZIndex = 7
		blade.Parent = star
	end
	table.insert(ctx.cleanup, gui)
	return { gui = gui, tint = tint, white = white, manga = manga, vitesse = vitesse, cartes = cartes, star = star }
end

-- ------------------------------------------------------------------ lecture

-- Joue la technique. `animations` contient les KeyframeSequences
-- "PoingDuDragon_Attaquant" et "PoingDuDragon_Victime" ; `data` = DragonFistData.
function DragonFist.play(attacker: Model, victim: Model, animations: Folder, data, forceCamera: boolean?)
	local cfg = DragonFist.CONFIG
	local aRoot = attacker:FindFirstChild("HumanoidRootPart") :: BasePart
	local vRoot = victim:FindFirstChild("HumanoidRootPart") :: BasePart
	local start = aRoot.CFrame
	aRoot.Anchored, vRoot.Anchored = true, true
	vRoot.CFrame = DragonFist.victimCFrame(start, data.DISTANCE)

	local fx = Instance.new("Folder")
	fx.Name = "DragonFistFX"
	fx.Parent = workspace

	local attTrack = animatorOf(attacker):LoadAnimation(animationFor(animations:FindFirstChild("PoingDuDragon_Attaquant") :: KeyframeSequence))
	local vicTrack = animatorOf(victim):LoadAnimation(animationFor(animations:FindFirstChild("PoingDuDragon_Victime") :: KeyframeSequence))
	for _, t in { attTrack, vicTrack } do
		t.Priority = Enum.AnimationPriority.Action4
		t.Looped = false
	end

	local binds = {}
	local shakes = {}
	local ctx
	ctx = {
		start = start,
		attacker = attacker,
		victim = victim,
		fx = fx,
		cleanup = {},
		kept = {},
		hitstop = function(d: number)
			attTrack:AdjustSpeed(0)
			vicTrack:AdjustSpeed(0)
			task.delay(d, function()
				attTrack:AdjustSpeed(1)
				vicTrack:AdjustSpeed(1)
			end)
		end,
		shake = function(amp: number, punch: number)
			table.insert(shakes, { t0 = os.clock(), amp = amp, punch = punch })
		end,
		bind = function(name: string, fn)
			binds[name] = fn
		end,
		leftovers = function(inst: Instance)
			table.insert(ctx.kept, inst)
		end,
	}
	local scr = screen(ctx)

	-- camera cinematique (joueur qui lance la technique)
	local camera = workspace.CurrentCamera
	local player = Players.LocalPlayer
	local useCam = camera ~= nil and (forceCamera == true or (cfg.CAMERA and player ~= nil and player.Character == attacker))
	local oldType, oldFov = camera and camera.CameraType, camera and camera.FieldOfView
	if useCam then
		camera.CameraType = Enum.CameraType.Scriptable
	end

	local state = { next = 1 }
	local handlers = {
		impact = impact,
		body_flash = bodyFlash,
		ground_burst = groundBurst,
		aura = aura,
		fist_glow = fistGlow,
		dragon = dragon,
		crater = crater,
		smoke_cloud = smokeCloud,
		embers = embers,
		dust_trail = dustTrail,
		dome = dome,
	}
	local mangaEv, whiteEv
	for _, e in data.EVENTS do
		if e.kind == "manga" then
			mangaEv = e
		elseif e.kind == "white" then
			whiteEv = e
		end
	end
	-- v6 : sequences d'ecran en TEMPS REEL (elles jouent pendant le hitstop,
	-- l'animation etant gelee) : on note l'instant de declenchement
	local screenT0 = {}
	handlers.vitesse = function(_, ev)
		screenT0.vitesse = { t0 = os.clock(), ev = ev }
	end
	handlers.cartes = function(_, ev)
		screenT0.cartes = { t0 = os.clock(), ev = ev }
	end

	local stepName = "DragonFist_" .. tostring(os.clock())
	local done = false
	RunService:BindToRenderStep(stepName, Enum.RenderPriority.Camera.Value + 1, function()
		if done then
			return
		end
		local f = attTrack.TimePosition * data.FPS
		for _, ev in DragonFist.due(data, state, f) do
			local h = handlers[ev.kind]
			if h then
				task.spawn(h, ctx, ev)
			end
		end
		for name, fn in binds do
			if not fn() then
				binds[name] = nil
			end
		end
		-- camera + secousse + punch-in de FOV
		local amp, punch = 0, 0
		for i = #shakes, 1, -1 do
			local age = os.clock() - shakes[i].t0
			if age > 0.6 then
				table.remove(shakes, i)
			else
				amp += shakes[i].amp * math.exp(-age / 0.09)
				punch += shakes[i].punch * math.exp(-age / 0.07)
			end
		end
		if useCam then
			local eye, look, fov = DragonFist.cameraAt(data, f)
			local cf = CFrame.lookAt(DragonFist.toWorld(start, { eye.X, eye.Y, eye.Z }), DragonFist.toWorld(start, { look.X, look.Y, look.Z }))
			if amp > 0.001 then
				cf *= CFrame.new((math.random() * 2 - 1) * amp * 0.35, (math.random() * 2 - 1) * amp * 0.35, 0)
					* CFrame.Angles(0, 0, (math.random() * 2 - 1) * amp * 0.03)
			end
			camera.CFrame = cf
			camera.FieldOfView = math.max(18, fov - punch)
		end
		-- ecran : teinte du temps suspendu, planches manga, blanc puis brouillard
		if scr then
			scr.tint.BackgroundTransparency = if f >= 196 and f < 290 then 0.9 else 1
			if mangaEv and f >= mangaEv.frames[1] and f < mangaEv.frames[4] then
				local i = if f < mangaEv.frames[2] then 1 elseif f < mangaEv.frames[3] then 2 else 3
				local id = cfg.MANGA_IDS[i]
				scr.manga.Visible = true
				scr.manga.Image = id
				-- repli sans image : alternance noir / blanc / noir (impact frames)
				scr.manga.BackgroundColor3 = if i == 2 then Color3.new(1, 1, 1) else Color3.new(0, 0, 0)
			else
				scr.manga.Visible = false
			end
			local whiteT = 1
			if whiteEv and f >= whiteEv.frames[1] and f < whiteEv.frames[3] then
				local a, b, c = whiteEv.frames[1], whiteEv.frames[2], whiteEv.frames[3]
				whiteT = if f < b then 0 else (f - b) / (c - b)
			end
			local vs = screenT0.vitesse
			local vage = if vs then os.clock() - vs.t0 else math.huge
			scr.vitesse.Visible = vage < (if vs then vs.ev.duration else 0)
			if scr.vitesse.Visible then
				scr.vitesse.BackgroundTransparency = 1 - 0.35 * (1 - vage / vs.ev.duration)
			end
			local ph = if screenT0.cartes then DragonFist.cartePhase(screenT0.cartes.ev, os.clock() - screenT0.cartes.t0) else nil
			scr.cartes.Visible = ph ~= nil and (ph.kind == "noir" or ph.kind == "carte")
			if ph and ph.kind == "noir" then
				scr.cartes.Image = ""
				scr.cartes.BackgroundColor3 = Color3.new(0, 0, 0)
				scr.star.Visible = true
				scr.star.Size = UDim2.fromScale(0.2 + 0.32 * ph.u, 0.2 + 0.32 * ph.u)
			elseif ph and ph.kind == "carte" then
				scr.star.Visible = false
				scr.cartes.Image = cfg.CARTE_IDS[ph.i]
				scr.cartes.BackgroundColor3 = if ph.i == 2 then Color3.new(1, 1, 1) else Color3.new(0, 0, 0)
			elseif ph and ph.kind == "blanc" then
				whiteT = 0
			elseif ph and ph.kind == "fondu" then
				whiteT = math.min(whiteT, ph.u)
			end
			scr.white.BackgroundTransparency = whiteT
		end
	end)

	local function finish()
		if done then
			return
		end
		done = true
		RunService:UnbindFromRenderStep(stepName)
		-- chaque HumanoidRootPart la ou son corps a fini (fin : attaquant
		-- dans le cratere, victime couchee au loin)
		aRoot.CFrame = DragonFist.finalCFrames(start, data)
		local _, vcf = DragonFist.finalCFrames(start, data)
		vRoot.CFrame = vcf
		aRoot.Anchored, vRoot.Anchored = false, false
		if useCam then
			camera.CameraType = oldType
			camera.FieldOfView = oldFov
		end
		for _, inst in ctx.cleanup do
			if inst and inst.Parent then
				inst:Destroy()
			end
		end
		task.delay(cfg.CLEANUP_TIME, function()
			fx:Destroy()
		end)
	end
	attTrack.Stopped:Connect(finish)
	attTrack:Play(0)
	vicTrack:Play(0)
	return attTrack, vicTrack, finish
end

return DragonFist
