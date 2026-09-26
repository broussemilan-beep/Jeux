--!nonstrict
--[[
	M1Technique -- direct du droit + reaction de la victime (rig R6).

	Anime par le cerveau d'animateur (experiments/_shared/animator_brain),
	exporte depuis le rig R6 IK+FK V2.22. Tout le TIMING des effets vient des
	marqueurs poses dans l'animation de l'attaquant :
	    trail_on  (0,167 s) -> la trainee du poing s'allume
	    hit       (0,283 s) -> impact : reaction, hitstop, VFX, recul, secousse
	    trail_off (0,350 s) -> la trainee s'eteint
	Aucun delai code en dur : si l'animation change, les effets suivent.

	SENS (verifie par verify_export.py sur les fichiers exportes) :
	  - l'attaquant frappe vers SON avant : HumanoidRootPart.CFrame.LookVector ;
	  - la victime est placee DEVANT lui, tournee vers lui (placeVictim) ;
	  - les etincelles partent dans le sens du coup, la victime recule dans
	    le sens du coup (jamais vers l'attaquant).
]]

local Debris = game:GetService("Debris")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local KeyframeSequenceProvider = game:GetService("KeyframeSequenceProvider")

local M1 = {}

M1.CONFIG = {
	DISTANCE = 3.899, -- studs entre les deux HumanoidRootPart (calcule : le poing touche la face avant du torse)
	HITSTOP = 0.07, -- s : les deux animations se figent a l'impact
	KNOCKBACK = 0.9, -- studs : recul de la victime dans le sens du coup
	KNOCKBACK_TIME = 0.16,
	SHAKE_AMPLITUDE = 0.28, -- studs
	SHAKE_DURATION = 0.2,
	SHAKE_MAX_DISTANCE = 60, -- pas de secousse si la camera est loin de l'impact
	FLASH_COLOR = Color3.fromRGB(235, 245, 255),
	SPARK_COLOR = Color3.fromRGB(255, 236, 170),
	RING_COLOR = Color3.fromRGB(190, 225, 255),
	TRAIL_COLOR = Color3.fromRGB(215, 235, 255),
}

-- textures integrees au client Roblox (aucun upload necessaire)
local SPARKLE = "rbxasset://textures/particles/sparkles_main.dds"

-- Place la victime DEVANT l'attaquant, tournee vers lui.
function M1.victimCFrame(attackerRootCFrame: CFrame): CFrame
	return attackerRootCFrame * CFrame.new(0, 0, -M1.CONFIG.DISTANCE) * CFrame.Angles(0, math.pi, 0)
end

function M1.placeVictim(attacker: Model, victim: Model)
	local aRoot = attacker:FindFirstChild("HumanoidRootPart") :: BasePart
	local vRoot = victim:FindFirstChild("HumanoidRootPart") :: BasePart
	vRoot.CFrame = M1.victimCFrame(aRoot.CFrame)
end

local cachedIds: { [KeyframeSequence]: string } = {}

-- AnimationId d'une KeyframeSequence : un attribut "AnimationId" (animation
-- publiee sur Roblox) est prioritaire ; sinon id temporaire de Studio.
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

local function emitter(parent: Attachment, props: { [string]: any }): ParticleEmitter
	local e = Instance.new("ParticleEmitter")
	e.Enabled = false
	e.Rate = 0
	e.Texture = SPARKLE
	e.LightInfluence = 0
	for k, v in props do
		(e :: any)[k] = v
	end
	e.Parent = parent
	return e
end

-- Repere d'impact : origine au contact, -Z (face Front) = sens du coup.
function M1.impactFrame(contact: Vector3, dir: Vector3): CFrame
	return CFrame.lookAt(contact, contact + dir)
end

-- Anneau d'onde de choc : le cylindre Roblox a son axe sur X ; tourne de
-- 90 deg autour de Y, cet axe passe sur -Z du repere d'impact, donc sur le
-- sens du coup (anneau perpendiculaire au coup), 0,3 stud en avant.
function M1.ringCFrame(frame: CFrame): CFrame
	return frame * CFrame.new(0, 0, -0.3) * CFrame.Angles(0, math.rad(90), 0)
end

-- Position de recul : dans le sens du coup (a plat), loin de l'attaquant.
function M1.knockbackCFrame(rootCFrame: CFrame, dir: Vector3): CFrame
	local flat = Vector3.new(dir.X, 0, dir.Z)
	if flat.Magnitude < 1e-3 then
		return rootCFrame
	end
	return rootCFrame + flat.Unit * M1.CONFIG.KNOCKBACK
end

-- Effets d'impact au point de contact, orientes dans le sens du coup `dir`.
function M1.impactVFX(contact: Vector3, dir: Vector3)
	local cfg = M1.CONFIG
	local frame = M1.impactFrame(contact, dir)

	local holder = Instance.new("Part")
	holder.Name = "M1_ImpactFX"
	holder.Anchored = true
	holder.CanCollide = false
	holder.CanQuery = false
	holder.CanTouch = false
	holder.Transparency = 1
	holder.Size = Vector3.new(0.1, 0.1, 0.1)
	holder.CFrame = frame
	holder.Parent = workspace
	local att = Instance.new("Attachment")
	att.Parent = holder

	-- 1. flash : une grosse particule tres breve
	local flash = emitter(att, {
		Color = ColorSequence.new(cfg.FLASH_COLOR),
		LightEmission = 1,
		Brightness = 4,
		Lifetime = NumberRange.new(0.09, 0.11),
		Speed = NumberRange.new(0),
		Size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.5),
			NumberSequenceKeypoint.new(0.25, 3.4),
			NumberSequenceKeypoint.new(1, 0),
		}),
		Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0),
			NumberSequenceKeypoint.new(1, 0.6),
		}),
		ZOffset = 2,
	})
	flash:Emit(1)

	-- 2. etincelles : partent DANS LE SENS DU COUP (Front de l'attachment)
	local sparks = emitter(att, {
		Color = ColorSequence.new(cfg.SPARK_COLOR, cfg.FLASH_COLOR),
		LightEmission = 1,
		Brightness = 3,
		EmissionDirection = Enum.NormalId.Front,
		SpreadAngle = Vector2.new(38, 38),
		Speed = NumberRange.new(28, 46),
		Drag = 9,
		Acceleration = Vector3.new(0, -35, 0),
		Lifetime = NumberRange.new(0.16, 0.3),
		Orientation = Enum.ParticleOrientation.VelocityParallel,
		Size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.32),
			NumberSequenceKeypoint.new(1, 0),
		}),
		Squash = NumberSequence.new(1.6), -- etirees le long de la vitesse
		ZOffset = 1,
	})
	sparks:Emit(16)

	-- 3. onde de choc : anneau perpendiculaire au coup, qui s'ouvre et s'efface
	local ring = Instance.new("Part")
	ring.Name = "M1_Shockwave"
	ring.Shape = Enum.PartType.Cylinder
	ring.Anchored = true
	ring.CanCollide = false
	ring.CanQuery = false
	ring.CanTouch = false
	ring.CastShadow = false
	ring.Material = Enum.Material.Neon
	ring.Color = cfg.RING_COLOR
	ring.Transparency = 0.25
	ring.Size = Vector3.new(0.12, 0.8, 0.8)
	ring.CFrame = M1.ringCFrame(frame)
	ring.Parent = workspace
	TweenService:Create(ring, TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Size = Vector3.new(0.05, 7, 7),
		Transparency = 1,
	}):Play()

	Debris:AddItem(holder, 1)
	Debris:AddItem(ring, 0.3)
end

-- Trainee du poing : ruban entre le milieu et le bout du bras droit.
local function fistTrail(attacker: Model): Trail
	local arm = attacker:FindFirstChild("Right Arm") :: BasePart
	local existing = arm:FindFirstChild("M1_FistTrail")
	if existing then
		return existing :: Trail
	end
	local a0 = Instance.new("Attachment")
	a0.Name = "M1_TrailTop"
	a0.Position = Vector3.new(0, -0.2, 0)
	a0.Parent = arm
	local a1 = Instance.new("Attachment")
	a1.Name = "M1_TrailFist"
	a1.Position = Vector3.new(0, -1, 0)
	a1.Parent = arm
	local trail = Instance.new("Trail")
	trail.Name = "M1_FistTrail"
	trail.Attachment0 = a0
	trail.Attachment1 = a1
	trail.Lifetime = 0.1
	trail.LightEmission = 0.8
	trail.LightInfluence = 0
	trail.Color = ColorSequence.new(M1.CONFIG.TRAIL_COLOR)
	trail.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.25),
		NumberSequenceKeypoint.new(1, 1),
	})
	trail.Enabled = false
	trail.Parent = arm
	return trail
end

local function hitstop(tracks: { AnimationTrack })
	for _, t in tracks do
		t:AdjustSpeed(0)
	end
	task.delay(M1.CONFIG.HITSTOP, function()
		for _, t in tracks do
			t:AdjustSpeed(1)
		end
	end)
end

local function knockback(victim: Model, dir: Vector3)
	local root = victim:FindFirstChild("HumanoidRootPart") :: BasePart
	local goal = M1.knockbackCFrame(root.CFrame, dir)
	task.delay(M1.CONFIG.HITSTOP, function()
		TweenService:Create(root, TweenInfo.new(M1.CONFIG.KNOCKBACK_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
			CFrame = goal,
		}):Play()
	end)
end

local function cameraShake(at: Vector3)
	local camera = workspace.CurrentCamera
	if not camera or (camera.CFrame.Position - at).Magnitude > M1.CONFIG.SHAKE_MAX_DISTANCE then
		return
	end
	local start = os.clock()
	local name = "M1_Shake_" .. tostring(start)
	RunService:BindToRenderStep(name, Enum.RenderPriority.Camera.Value + 1, function()
		local k = (os.clock() - start) / M1.CONFIG.SHAKE_DURATION
		if k >= 1 then
			RunService:UnbindFromRenderStep(name)
			return
		end
		local a = M1.CONFIG.SHAKE_AMPLITUDE * (1 - k) ^ 2
		camera.CFrame = camera.CFrame * CFrame.new((math.random() * 2 - 1) * a, (math.random() * 2 - 1) * a, 0)
	end)
end

-- Joue la technique complete. `animations` contient les deux
-- KeyframeSequence "M1_Attaquant" et "M1_Victime_Reaction".
function M1.play(attacker: Model, victim: Model, animations: Folder)
	local attTrack = animatorOf(attacker):LoadAnimation(animationFor(animations:FindFirstChild("M1_Attaquant") :: KeyframeSequence))
	local vicTrack = animatorOf(victim):LoadAnimation(animationFor(animations:FindFirstChild("M1_Victime_Reaction") :: KeyframeSequence))
	attTrack.Priority = Enum.AnimationPriority.Action
	vicTrack.Priority = Enum.AnimationPriority.Action
	attTrack.Looped = false
	vicTrack.Looped = false

	local trail = fistTrail(attacker)
	local conns = {}
	table.insert(conns, attTrack:GetMarkerReachedSignal("trail_on"):Connect(function()
		trail.Enabled = true
	end))
	table.insert(conns, attTrack:GetMarkerReachedSignal("trail_off"):Connect(function()
		trail.Enabled = false
	end))
	table.insert(conns, attTrack:GetMarkerReachedSignal("hit"):Connect(function()
		local root = attacker:FindFirstChild("HumanoidRootPart") :: BasePart
		local arm = attacker:FindFirstChild("Right Arm") :: BasePart
		local dir = root.CFrame.LookVector -- sens du coup = avant de l'attaquant
		local contact = (arm.CFrame * CFrame.new(0, -1, 0)).Position -- bout du poing
		vicTrack:Play(0) -- reaction immediate, figee pendant le hitstop
		hitstop({ attTrack, vicTrack })
		M1.impactVFX(contact, dir)
		knockback(victim, dir)
		cameraShake(contact)
	end))
	table.insert(conns, attTrack.Stopped:Connect(function()
		trail.Enabled = false
		for _, c in conns do
			c:Disconnect()
		end
	end))
	attTrack:Play(0.08)
	return attTrack, vicTrack
end

return M1
