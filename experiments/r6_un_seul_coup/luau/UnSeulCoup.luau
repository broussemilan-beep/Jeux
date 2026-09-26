--!nonstrict
--[[
	UnSeulCoup -- « Un seul coup » (Serious Punch), cinématique R6 à 2 personnages.

	Animé par le cerveau d'animateur (experiments/_shared/animator_brain) sur
	deux rigs R6 IK+FK V2.22, exporté en KeyframeSequences à 60 i/s. La mise
	en scène (caméra, destruction, fumées, nuages, écran, sons) vient de
	UnSeulCoupData, généré depuis staging.json : la MÊME source que le
	lecteur HTML. Un ordonnanceur lit la position RÉELLE de la piste
	d'animation (TimePosition) et déclenche chaque événement à sa frame.

	Déroulé : calme -> départ -> glissade -> armé -> UN coup (poing vers
	l'objectif) -> 2 images inversées -> blanc -> le sillon de roches file
	jusqu'à l'horizon, les nuages se fendent -> il se redresse.

	Mode cinématique : les deux HumanoidRootPart sont ANCRÉS pendant la
	technique ; tout le mouvement est dans le RootJoint de l'animation. À la
	fin, chaque HumanoidRootPart est replacé là où son corps a fini.

	SENS : tout point P de UnSeulCoupData est exprimé dans le repère de
	l'attaquant AU LANCEMENT (origine au sol sous le HumanoidRootPart, avant =
	-Z) ; en jeu il devient start * P (vérifié par sens_test.luau).

	À vérifier dans Studio (non testable ici, pas de moteur Roblox dans ce
	bac à sable) : le rendu des 2 images inversées (Highlight noir + ColorCorrection
	qui blanchit le décor), et la tenue des ~450 roches + ~700 boules de nuages.
]]

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Lighting = game:GetService("Lighting")
local KeyframeSequenceProvider = game:GetService("KeyframeSequenceProvider")

local UnSeulCoup = {}

UnSeulCoup.CONFIG = {
	CAMERA = true, -- caméra cinématique pour le joueur qui lance la technique
	SCREEN_FX = true, -- images inversées, blanc, fondu
	NUAGES = true, -- couche de nuages low-poly qui se fend (sinon : garder le ciel du jeu)
	CLEANUP_TIME = 12, -- s : durée de vie du sillon et des fumées après la fin
	-- sons : les WAV du studio (experiments/_shared/vfx_studio/sons/<nom>.wav)
	-- importés dans Studio ; vides = silence (la technique tourne quand même)
	SOUND_IDS = {
		vent_ambiant = "",
		fouet_m1 = "",
		vent_arc = "",
		frappe_m1 = "",
		aspiration = "",
		souffle_projectile = "",
		impact_lourd = "",
		grondement = "",
	},
	ROCHE = { Color3.fromRGB(63, 61, 64), Color3.fromRGB(77, 73, 69), Color3.fromRGB(47, 46, 51) },
	SILLON = Color3.fromRGB(59, 52, 45),
	FUMEE = Color3.fromRGB(239, 236, 230),
}

local TEX = {
	smoke = "rbxasset://textures/particles/smoke_main.dds",
}

local function vec(t): Vector3
	return Vector3.new(t[1], t[2], t[3])
end

local function clamp(x: number, a: number, b: number): number
	return math.max(a, math.min(b, x))
end

local function easeOut(u: number): number
	u = clamp(u, 0, 1)
	return 1 - (1 - u) ^ 3
end

-- ------------------------------------------------------------------ géométrie pure (testée)

UnSeulCoup.ROOT_Y = 3

-- Victime DEVANT l'attaquant, tournée vers lui (même placement qu'à l'export).
function UnSeulCoup.victimCFrame(start: CFrame, distance: number): CFrame
	return start * CFrame.new(0, 0, -distance) * CFrame.Angles(0, math.pi, 0)
end

-- Point du repère de scène (origine AU SOL sous l'attaquant) -> monde.
function UnSeulCoup.toWorld(start: CFrame, p): Vector3
	return start * Vector3.new(p[1], p[2] - UnSeulCoup.ROOT_Y, p[3])
end

-- Caméra à la frame `f` : (oeil, cible, fov) dans le repère de scène. Une clé
-- "cut" est une coupe franche ; entre une clé et la suivante douce :
-- interpolation linéaire (comme le lecteur HTML).
function UnSeulCoup.cameraAt(data, f: number)
	local K = data.CAMERA
	local i = 1
	while i + 1 <= #K and K[i + 1].f <= f do
		i += 1
	end
	local k1, k2 = K[i], K[i + 1]
	if not k2 or k2.cut then
		return vec(k1.eye), vec(k1.look), k1.fov
	end
	local u = clamp((f - k1.f) / (k2.f - k1.f), 0, 1)
	return vec(k1.eye):Lerp(vec(k2.eye), u), vec(k1.look):Lerp(vec(k2.look), u), k1.fov + (k2.fov - k1.fov) * u
end

-- Pendant les 2 images inversées, pose et caméra sont FIGÉES 4 i chacune.
function UnSeulCoup.frameTenue(data, f: number): number
	local inv = data.INVERSE
	if f >= inv[1] and f < inv[2] then
		return if f < inv[1] + 4 then inv[1] else inv[1] + 4
	end
	return f
end

function UnSeulCoup.finalCFrames(start: CFrame, data): (CFrame, CFrame)
	local rot = start - start.Position
	local a = CFrame.new(UnSeulCoup.toWorld(start, data.FINAL.attacker)) * rot
	local v = CFrame.new(UnSeulCoup.toWorld(start, data.FINAL.victim)) * rot * CFrame.Angles(0, math.pi, 0)
	return a, v
end

-- Ordonnanceur : événements dont la frame est atteinte, dans l'ordre, une fois chacun.
function UnSeulCoup.due(data, state, frame: number)
	local out = {}
	local E = data.EVENTS
	while state.next <= #E and E[state.next].frame <= frame do
		table.insert(out, E[state.next])
		state.next += 1
	end
	return out
end

-- Roche : fraction sortie du sol (0 = enterrée, dépassement ~1,1 puis 1) et
-- fraction d'inclinaison, `t` en secondes depuis le lancement.
function UnSeulCoup.rocheSortie(r, t: number): (number, number)
	local u = (t - r.t) / 0.16
	if u <= 0 then
		return 0, 0
	end
	local up = if u < 1 then 1 - (1 - u) ^ 3 * math.cos(u * 2.2) else 1
	return clamp(up, 0, 1.15), clamp(u, 0, 1)
end

-- Longueur du sillon ouvert à l'instant t.
function UnSeulCoup.sillonLongueur(data, t: number): number
	return clamp((t - data.CONTACT_T) * data.DECOR.vitesse, 0, data.DECOR.sillon.long)
end

-- Décalage latéral (repère de scène, x) d'un nuage : il s'écarte de la ligne
-- du coup quand l'onde l'atteint (même formule que le lecteur).
function UnSeulCoup.nuageDecalage(fente, x0: number, z: number, t: number): number
	local dz = math.max(0, -z - 20)
	local u = easeOut((t - (fente.t0 + dz / fente.vitesse)) / fente.duree)
	local dx = x0 - fente.x
	if math.abs(dx) >= fente.largeur then
		return 0
	end
	local w = 1 - math.abs(dx) / fente.largeur
	local s = if dx < 0 then -1 else 1
	return s * fente.ecart * u * (0.25 + 0.75 * math.sqrt(w))
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

local function ancre(parent: Instance, cf: CFrame, size: Vector3?): Part
	local p = Instance.new("Part")
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch = true, false, false, false
	p.Transparency = 1
	p.Size = size or Vector3.new(0.2, 0.2, 0.2)
	p.CFrame = cf
	p.Parent = parent
	return p
end

local function fumee(parent: Instance, pos: Vector3, rayon: number, hauteur: number, duree: number, couleur: Color3)
	local p = ancre(parent, CFrame.new(pos))
	local a = Instance.new("Attachment")
	a.Parent = p
	local e = Instance.new("ParticleEmitter")
	e.Texture = TEX.smoke
	e.Color = ColorSequence.new(couleur)
	e.LightEmission = 0
	e.Lifetime = NumberRange.new(2.5, 4.5)
	e.Speed = NumberRange.new(hauteur / 3.2, hauteur / 2.4)
	e.SpreadAngle = Vector2.new(12, 12)
	e.Acceleration = Vector3.new(0.9, -hauteur / 12, 0)
	e.Drag = 0.8
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, rayon * 0.9), NumberSequenceKeypoint.new(1, rayon * 2.4) })
	e.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 1),
		NumberSequenceKeypoint.new(0.08, 0.45),
		NumberSequenceKeypoint.new(0.6, 0.65),
		NumberSequenceKeypoint.new(1, 1),
	})
	e.Rotation = NumberRange.new(0, 360)
	e.RotSpeed = NumberRange.new(-20, 20)
	e.Rate = 10
	e.Parent = a
	task.delay(duree, function()
		e.Enabled = false
	end)
	return p
end

local function bouffee(parent: Instance, pos: Vector3, n: number, taille: number, vitesse: number)
	local p = ancre(parent, CFrame.new(pos))
	local a = Instance.new("Attachment")
	a.Parent = p
	local e = Instance.new("ParticleEmitter")
	e.Texture = TEX.smoke
	e.Color = ColorSequence.new(Color3.fromRGB(217, 209, 198))
	e.Lifetime = NumberRange.new(1.2, 2.2)
	e.Speed = NumberRange.new(vitesse * 0.6, vitesse)
	e.SpreadAngle = Vector2.new(180, 20)
	e.Drag = 3
	e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, taille), NumberSequenceKeypoint.new(1, taille * 2.6) })
	e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.35), NumberSequenceKeypoint.new(1, 1) })
	e.Rate = 0
	e.Parent = a
	e:Emit(n)
	return p
end

-- ------------------------------------------------------------------ la destruction

local function construireRoches(ctx)
	local data, cfg = ctx.data, UnSeulCoup.CONFIG
	local dossier = Instance.new("Model")
	dossier.Name = "Sillon"
	dossier.Parent = ctx.fx
	ctx.roches = {}
	for i, r in data.DECOR.roches do
		-- CornerWedge : un bloc à pointe, le plus « roche éclatée » des parts de base
		local p = Instance.new("CornerWedgePart")
		p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch = true, false, false, false
		p.Material = Enum.Material.Slate
		p.Color = cfg.ROCHE[(r.c % 3) + 1]
		p.Size = Vector3.new(r.s[1], r.s[2], r.s[3])
		local base = UnSeulCoup.toWorld(ctx.start, { r.p[1], 0, r.p[2] })
		local rot = (ctx.start - ctx.start.Position) * CFrame.Angles(0, math.rad(r.r[2]), 0)
		ctx.roches[i] = { part = p, base = base, rot = rot, r = r }
		p.CFrame = CFrame.new(base - Vector3.new(0, r.s[2], 0)) * rot
		p.Parent = dossier
	end
	ctx.sillonModel = dossier
	-- fond du sillon : 12 tronçons qui s'ouvrent avec la vague
	local S = data.DECOR.sillon
	ctx.troncons = {}
	for k = 1, 12 do
		local d0, d1 = (k - 1) / 12 * S.long, k / 12 * S.long
		local w = S.l0 + (S.l1 - S.l0) * (d0 + d1) / 2 / S.long
		local p = Instance.new("Part")
		p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch = true, false, false, false
		p.Material = Enum.Material.Ground
		p.Color = cfg.SILLON
		p.Size = Vector3.new(2 * w, 0.2, d1 - d0)
		p.CFrame = CFrame.new(UnSeulCoup.toWorld(ctx.start, { S.x, 0.05, S.z0 - (d0 + d1) / 2 })) * (ctx.start - ctx.start.Position)
		p.Transparency = 1
		p.Parent = dossier
		ctx.troncons[k] = { part = p, d1 = d1 }
	end
end

local function placerRoches(ctx, t: number)
	for _, R in ctx.roches do
		local sortie, incl = UnSeulCoup.rocheSortie(R.r, t)
		if sortie > 0 and not R.fini then
			local r = R.r
			local tilt = CFrame.Angles(math.rad(r.r[1]) * incl, 0, math.rad(r.r[3]) * incl)
			local y = r.s[2] * (sortie - 1) * 0.5 + r.s[2] * 0.32
			R.part.CFrame = CFrame.new(R.base + Vector3.new(0, y, 0)) * R.rot * tilt
			if t - r.t > 0.3 then
				R.fini = true
			end
		end
	end
	local L = UnSeulCoup.sillonLongueur(ctx.data, t)
	for _, T in ctx.troncons do
		T.part.Transparency = if L >= T.d1 - ctx.data.DECOR.sillon.long / 24 then 0 else 1
	end
end

local function construireNuages(ctx)
	local N = {}
	local dossier = Instance.new("Model")
	dossier.Name = "Nuages"
	dossier.Parent = ctx.fx
	for _, n in ctx.data.DECOR.nuages do
		local boules = {}
		for _, b in n.b do
			local p = Instance.new("Part")
			p.Shape = Enum.PartType.Ball
			p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, false
			p.Material = Enum.Material.SmoothPlastic
			p.Color = Color3.new(1, 1, 1)
			-- une Ball reste ronde : l'aplatissement se fait par un SpecialMesh
			p.Size = Vector3.new(2, 2, 2)
			local m = Instance.new("SpecialMesh")
			m.MeshType = Enum.MeshType.Sphere
			m.Scale = Vector3.new(b[4], b[4] * 0.45, b[4] * 0.8)
			m.Parent = p
			p.Parent = dossier
			table.insert(boules, { part = p, off = { b[1], b[2], b[3] } })
		end
		table.insert(N, { n = n, boules = boules })
	end
	ctx.nuages = N
end

local function placerNuages(ctx, t: number)
	local F = ctx.data.DECOR.fente
	for _, c in ctx.nuages do
		local n = c.n
		local x = n.p[1] + UnSeulCoup.nuageDecalage(F, n.p[1], n.p[3], t)
		for _, b in c.boules do
			b.part.CFrame = CFrame.new(UnSeulCoup.toWorld(ctx.start, { x + b.off[1], n.p[2] + b.off[2], n.p[3] + b.off[3] }))
		end
	end
end

-- ------------------------------------------------------------------ écran

local function ecran(ctx)
	local player = Players.LocalPlayer
	if not player or not UnSeulCoup.CONFIG.SCREEN_FX then
		return nil
	end
	local gui = Instance.new("ScreenGui")
	gui.Name = "UnSeulCoupEcran"
	gui.IgnoreGuiInset = true
	gui.DisplayOrder = 50
	gui.ResetOnSpawn = false
	local function plein(nom: string, couleur: Color3)
		local f = Instance.new("Frame")
		f.Name = nom
		f.Size = UDim2.fromScale(1, 1)
		f.BorderSizePixel = 0
		f.BackgroundColor3 = couleur
		f.BackgroundTransparency = 1
		f.Parent = gui
		return f
	end
	local scr = { gui = gui, blanc = plein("Blanc", Color3.new(1, 1, 0.98)), noir = plein("Noir", Color3.new(0, 0, 0)) }
	gui.Parent = player:WaitForChild("PlayerGui")
	table.insert(ctx.cleanup, gui)
	return scr
end

-- 2 images inversées : silhouettes NOIRES (Highlight opaque) sur un décor
-- blanchi (ColorCorrection) -- approximation Roblox de l'image inversée de Pew
local function inversion(ctx)
	local hs = {}
	for _, m in { ctx.attacker, ctx.victim, ctx.sillonModel } do
		if m then
			local h = Instance.new("Highlight")
			h.Adornee = m
			h.FillColor = Color3.new(0, 0, 0)
			h.FillTransparency = 0
			h.OutlineTransparency = 1
			h.DepthMode = Enum.HighlightDepthMode.Occluded
			h.Enabled = false
			h.Parent = ctx.fx
			table.insert(hs, h)
		end
	end
	local cc = Instance.new("ColorCorrectionEffect")
	cc.Name = "UnSeulCoupInverse"
	cc.Enabled = false
	cc.Brightness = 0.9
	cc.Contrast = -1
	cc.Saturation = -1
	cc.Parent = Lighting
	table.insert(ctx.cleanup, cc)
	return function(on: boolean)
		for _, h in hs do
			h.Enabled = on
		end
		cc.Enabled = on
	end
end

-- ------------------------------------------------------------------ jouer

function UnSeulCoup.play(attacker: Model, victim: Model, animations: Folder, data, forceCamera: boolean?)
	local cfg = UnSeulCoup.CONFIG
	local aRoot = attacker:FindFirstChild("HumanoidRootPart") :: BasePart
	local vRoot = victim:FindFirstChild("HumanoidRootPart") :: BasePart
	local start = aRoot.CFrame
	aRoot.Anchored, vRoot.Anchored = true, true
	vRoot.CFrame = UnSeulCoup.victimCFrame(start, data.DISTANCE)

	local fx = Instance.new("Folder")
	fx.Name = "UnSeulCoupFX"
	fx.Parent = workspace

	local attTrack = animatorOf(attacker):LoadAnimation(animationFor(animations:FindFirstChild("UnSeulCoup_Attaquant") :: KeyframeSequence))
	local vicTrack = animatorOf(victim):LoadAnimation(animationFor(animations:FindFirstChild("UnSeulCoup_Victime") :: KeyframeSequence))
	for _, tr in { attTrack, vicTrack } do
		tr.Priority = Enum.AnimationPriority.Action4
		tr.Looped = false
	end

	local ctx = { start = start, data = data, attacker = attacker, victim = victim, fx = fx, cleanup = {} }
	construireRoches(ctx)
	if cfg.NUAGES then
		construireNuages(ctx)
	end
	local scr = ecran(ctx)
	local inverser = inversion(ctx)

	local camera = workspace.CurrentCamera
	local player = Players.LocalPlayer
	local useCam = camera ~= nil and (forceCamera == true or (cfg.CAMERA and player ~= nil and player.Character == attacker))
	local oldType, oldFov = camera and camera.CameraType, camera and camera.FieldOfView
	if useCam then
		camera.CameraType = Enum.CameraType.Scriptable
	end

	-- victime masquée (pour ce client) : pendant le plan « regard de la
	-- victime » (la caméra est à sa place) et une fois partie à l'horizon
	local function cacherVictime(on: boolean)
		for _, d in victim:GetDescendants() do
			if d:IsA("BasePart") or d:IsA("Decal") then
				d.LocalTransparencyModifier = if on then 1 else 0
			end
		end
	end

	local handlers = {}
	handlers.son = function(_, ev)
		local id = cfg.SOUND_IDS[ev.son]
		if id and id ~= "" then
			local s = Instance.new("Sound")
			s.SoundId = id
			s.Volume = ev.volume
			s.PlaybackSpeed = ev.hauteur
			s.Parent = fx
			s:Play()
		end
	end
	handlers.poussiere = function(_, ev)
		bouffee(fx, UnSeulCoup.toWorld(start, ev.pos), 3, 1.2, 4)
	end
	handlers.tourbillon = function(_, ev)
		local bras = attacker:FindFirstChild("Right Arm") :: BasePart
		if not bras then
			return
		end
		local a = Instance.new("Attachment")
		a.Position = Vector3.new(0, -1, 0)
		a.Parent = bras
		local e = Instance.new("ParticleEmitter")
		e.Texture = TEX.smoke
		e.Color = ColorSequence.new(Color3.fromRGB(141, 138, 134), Color3.fromRGB(230, 225, 216))
		e.Lifetime = NumberRange.new(0.3, 0.5)
		e.Speed = NumberRange.new(1, 3)
		e.SpreadAngle = Vector2.new(180, 180)
		e.RotSpeed = NumberRange.new(-400, 400)
		e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.9), NumberSequenceKeypoint.new(1, 1.8) })
		e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.5), NumberSequenceKeypoint.new(1, 1) })
		e.Rate = 60
		e.LockedToPart = true
		e.Parent = a
		table.insert(ctx.cleanup, a)
		task.delay((ev.fin - ev.frame) / data.FPS, function()
			e.Enabled = false
		end)
	end
	handlers.souffle_sol = function(_, ev)
		bouffee(fx, UnSeulCoup.toWorld(start, ev.pos), 40, 3, 16)
	end
	handlers.destruction = function()
		for _, c in data.DECOR.fumees do
			task.delay(math.max(0, c.t - data.CONTACT_T), function()
				fumee(fx, UnSeulCoup.toWorld(start, { c.p[1], 1, c.p[2] }), c.r, c.h, 1.2, cfg.FUMEE)
			end)
		end
		local cm = data.DECOR.choc_montagne
		task.delay(math.max(0, cm.t - data.CONTACT_T), function()
			fumee(fx, UnSeulCoup.toWorld(start, { cm.p[1], 8, cm.p[2] }), 30, 60, 2, Color3.fromRGB(226, 221, 212))
		end)
	end

	local state = { next = 1 }
	local stepName = "UnSeulCoup_" .. tostring(os.clock())
	local done = false
	local t0 = os.clock()
	RunService:BindToRenderStep(stepName, Enum.RenderPriority.Camera.Value + 1, function()
		if done then
			return
		end
		local f = attTrack.TimePosition * data.FPS
		local t = os.clock() - t0
		for _, ev in UnSeulCoup.due(data, state, f) do
			local h = handlers[ev.kind]
			if h then
				task.spawn(h, ctx, ev)
			end
		end
		placerRoches(ctx, t)
		if ctx.nuages then
			placerNuages(ctx, t)
		end
		cacherVictime(f >= data.VICTIME.cachee or (f >= data.VICTIME.pov[1] and f < data.VICTIME.pov[2]))
		local inv = f >= data.INVERSE[1] and f < data.INVERSE[2]
		inverser(inv)
		if useCam then
			local fc = UnSeulCoup.frameTenue(data, f)
			local eye, look, fov = UnSeulCoup.cameraAt(data, fc)
			local cf = CFrame.lookAt(UnSeulCoup.toWorld(start, { eye.X, eye.Y, eye.Z }), UnSeulCoup.toWorld(start, { look.X, look.Y, look.Z }))
			local S = data.SECOUSSE
			if f >= S[1] and f < S[2] then
				local a = S[3] * (1 - (f - S[1]) / (S[2] - S[1])) ^ 2
				cf *= CFrame.new(a * math.sin(f * 1.9), a * math.sin(f * 2.7 + 1), 0)
			end
			camera.CFrame = cf
			camera.FieldOfView = fov
		end
		if scr then
			local B = data.BLANC
			local blanc = 1
			if f >= B[1] and f < B[3] then
				blanc = if f < B[2] then 0 else (f - B[2]) / (B[3] - B[2])
			end
			scr.blanc.BackgroundTransparency = blanc
			local N = data.FONDU_NOIR
			scr.noir.BackgroundTransparency = if f >= N[1] then 1 - clamp((f - N[1]) / (N[2] - N[1]), 0, 1) else 1
		end
	end)

	local function finish()
		if done then
			return
		end
		done = true
		RunService:UnbindFromRenderStep(stepName)
		local acf, vcf = UnSeulCoup.finalCFrames(start, data)
		aRoot.CFrame, vRoot.CFrame = acf, vcf
		aRoot.Anchored, vRoot.Anchored = false, false
		cacherVictime(false)
		inverser(false)
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

return UnSeulCoup
