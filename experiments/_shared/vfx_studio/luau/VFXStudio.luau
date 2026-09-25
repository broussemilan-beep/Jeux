--!nonstrict
--[[
	VFXStudio : moteur d'EXÉCUTION Roblox des recettes du studio VFX
	(vfx_studio/recettes.py -> compile_roblox.py -> VFXRecettes.luau).

	Même sémantique que l'aperçu (vfx_studio/lab/moteur.js) :
	- particules = ParticleEmitter (Emit / Rate, séquences, flipbook,
	  LightEmission, et LightInfluence fixé À LA MAIN, car Instance.new le met
	  à 0 [doc officielle]) ;
	- mesh = Part + SpecialMesh (FileMesh), dont MeshId, TextureId, Scale et
	  VertexColor sont modifiables en jeu (un MeshPart ne l'est pas). Le
	  défilement de texture (UV scrolling) n'existe pas nativement sur un
	  mesh : on fait tourner des variantes pré-décalées de la texture
	  (`<texture>_d0..7`), comme les flipbooks par échange de texture de
	  Qwinkle ;
	- Trail / Beam natifs ; projectile = Part déplacée à chaque image ;
	- BloomEffect animé, flash d'écran (ScreenGui), secousse directionnelle
	  (même générateur pseudo-aléatoire que l'aperçu, mulberry32), gel du
	  hitstop (TimeScale = 0) ;
	- son : Sound, si un SoundId est connu.

	Les événements sont déclenchés par le TEMPS écoulé dans une seule boucle,
	jamais par des task.delay dispersés : c'est déterministe, et testable
	hors Roblox (vfx_studio/luau/test_vfxstudio.luau).

	Utilisation (client) :
		local VFX = require(path.VFXStudio)
		local DATA = require(path.VFXRecettes)
		VFX.configurer(DATA.assets)
		local h = VFX.jouer(DATA.recettes.orbe_impact, CFrame.new(0, 0, 0))
		-- h.Annuler() pour tout nettoyer si la technique est interrompue
]]

local VFXStudio = {}

local ASSETS = { textures = {}, meshes = {}, sons = {}, variantes = {},
	repli_texture = "rbxasset://textures/particles/sparkles_main.dds" }

function VFXStudio.configurer(a)
	for k, v in pairs(a or {}) do
		ASSETS[k] = v
	end
end

-- ------------------------------------------------------------ hasard (= aperçu)
local function imul(a, b)
	local ah, al = bit32.rshift(a, 16), bit32.band(a, 0xffff)
	local bh, bl = bit32.rshift(b, 16), bit32.band(b, 0xffff)
	return bit32.band(al * bl + bit32.lshift(bit32.band(ah * bl + al * bh, 0xffff), 16), 0xffffffff)
end
function VFXStudio.mulberry(seed)
	local a = bit32.band(seed, 0xffffffff)
	return function()
		a = bit32.band(a + 0x6d2b79f5, 0xffffffff)
		local t = imul(bit32.bxor(a, bit32.rshift(a, 15)), bit32.bor(1, a))
		t = bit32.bxor(bit32.band(t + imul(bit32.bxor(t, bit32.rshift(t, 7)), bit32.bor(61, t)), 0xffffffff), t)
		return bit32.bxor(t, bit32.rshift(t, 14)) / 4294967296
	end
end

-- ------------------------------------------------------------ séquences
function VFXStudio.seq(s, t, e)
	if s == nil then
		return 0
	end
	if type(s) == "number" then
		return s
	end
	if t <= s[1][1] then
		return s[1][2] + (s[1][3] or 0) * (e or 0)
	end
	for i = 2, #s do
		if t <= s[i][1] then
			local a, b = s[i - 1], s[i]
			local u = (t - a[1]) / math.max(1e-6, b[1] - a[1])
			return a[2] + (b[2] - a[2]) * u + ((a[3] or 0) + ((b[3] or 0) - (a[3] or 0)) * u) * (e or 0)
		end
	end
	local l = s[#s]
	return l[2] + (l[3] or 0) * (e or 0)
end
local seq = VFXStudio.seq

local function vseq(s, t) -- séquence de vecteurs {{t, {x,y,z}}}
	local out = {}
	for k = 1, 3 do
		local sk = {}
		for i, p in ipairs(s) do
			sk[i] = { p[1], p[2][k] }
		end
		out[k] = seq(sk, t)
	end
	return out
end

local function numSeq(s)
	local kp = {}
	for i, p in ipairs(s) do
		kp[i] = NumberSequenceKeypoint.new(p[1], p[2], p[3] or 0)
	end
	return NumberSequence.new(kp)
end
local function colSeq(s)
	local kp = {}
	for i, p in ipairs(s) do
		kp[i] = ColorSequenceKeypoint.new(p[1], Color3.new(p[2][1], p[2][2], p[2][3]))
	end
	return ColorSequence.new(kp)
end
local function colAt(s, t)
	return vseq(s, t)
end
local function vec(a)
	return Vector3.new(a[1], a[2], a[3])
end
local function range(a)
	return NumberRange.new(a[1], a[2])
end

local function texture(nom, variante)
	if not nom then
		return nil
	end
	local id = ASSETS.textures[nom .. (variante and ("_d" .. variante) or "")] or ASSETS.textures[nom]
	return id or ASSETS.repli_texture
end

-- repère dont l'axe Y = d (axes monde)
-- repère dont l'axe Y = d : rotation MINIMALE depuis Y monde, comme
-- setFromUnitVectors dans l'aperçu (sinon le lacet des croissants diffère)
local function repereY(pos, d)
	local y = d.Unit
	local up = Vector3.new(0, 1, 0)
	local c = up:Dot(y)
	if c > 0.99999 then
		return CFrame.new(pos)
	elseif c < -0.99999 then
		return CFrame.new(pos) * CFrame.Angles(math.pi, 0, 0)
	end
	local axe = up:Cross(y).Unit
	return CFrame.new(pos) * CFrame.fromAxisAngle(axe, math.acos(c))
end

local function porteur(dossier, nom)
	local p = Instance.new("Part")
	p.Name = nom
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Transparency = 1
	p.Size = Vector3.new(0.2, 0.2, 0.2)
	p.Parent = dossier
	return p
end

-- décalage de caméra : même formule et même générateur que l'aperçu
-- (trauma² : amplitude * (1 - a/durée)^2, bruit à graine fixe + cosinus)
function VFXStudio.secousse(rec, t)
	local x, y, z = 0, 0, 0
	for _, s in ipairs(rec.secousses or {}) do
		local a = t - s.t0
		if a >= 0 and a <= s.duree then
			local r = VFXStudio.mulberry((s.graine or 9) * 1000 + math.floor(a * 60))
			local amp = s.amplitude * (1 - a / s.duree) ^ 2
			local d = s.direction or { 0, -1, 0 }
			local n = math.sqrt(d[1] * d[1] + d[2] * d[2] + d[3] * d[3])
			local k = amp * (r() * 2 - 1) * 0.6 + amp * 0.4 * math.cos(a * 70)
			x, y, z = x + d[1] / n * k, y + d[2] / n * k, z + d[3] / n * k
		end
	end
	return Vector3.new(x, y, z)
end

-- ============================================================ jouer
function VFXStudio.jouer(rec, repere, opts)
	opts = opts or {}
	repere = repere or CFrame.new(0, 0, 0)
	local dossier = Instance.new("Folder")
	dossier.Name = "VFX_" .. rec.nom
	dossier.Parent = opts.parent or workspace

	local function monde(a)
		return repere:PointToWorldSpace(vec(a))
	end
	local function dirMonde(a)
		return repere:VectorToWorldSpace(vec(a)).Unit
	end

	-- ancres
	local P = rec.projectile
	local function projectilePos(t)
		local a, b = monde(P.de), monde(P.a)
		local u = math.clamp((t - P.t0) / (P.t1 - P.t0), 0, 1)
		local e = P.acceleration and u * u or u
		local p = a:Lerp(b, e)
		return p + repere:VectorToWorldSpace(Vector3.new(0, (P.hauteur or 0) * 4 * e * (1 - e), 0))
	end
	local function resolve(anc, t)
		if anc == "projectile" then
			local p0, p1 = projectilePos(math.max(P.t0, t - 0.01)), projectilePos(math.min(P.t1, t + 0.01))
			local d = p1 - p0
			return projectilePos(t), (d.Magnitude > 1e-6 and d.Unit or Vector3.new(0, 1, 0))
		elseif anc == "impact" then
			return monde(P.a), repere:VectorToWorldSpace(Vector3.new(0, 1, 0)), (monde(P.a) - monde(P.de)).Unit
		end
		anc = anc or {}
		if anc.chemin then
			-- ancre qui SUIT un chemin {{t, x, y, z}, ...} (poing, victime projetée)
			local c = anc.chemin
			local i = 1
			while i < #c - 1 and c[i + 1][1] <= t do
				i += 1
			end
			local a, b = c[i], c[math.min(i + 1, #c)]
			local u = if b[1] > a[1] then math.clamp((t - a[1]) / (b[1] - a[1]), 0, 1) else 0
			local pa, pb = monde({ a[2], a[3], a[4] }), monde({ b[2], b[3], b[4] })
			local d = pb - pa
			return pa:Lerp(pb, u), (if d.Magnitude > 1e-6 then d.Unit else Vector3.new(0, 1, 0)), dirMonde(anc.coup or { 0, 0, -1 })
		end
		return monde(anc.pos or { 0, 0, 0 }), dirMonde(anc.dir or { 0, 1, 0 }), dirMonde(anc.coup or { 0, 0, -1 })
	end

	local evenements = {} -- {t, fn, fait}
	local miseAJour = {} -- fonctions(t) appelées à chaque image
	local emetteurs = {}
	local finMax = rec.duree
	local function ev(t, fn)
		table.insert(evenements, { t = t, fn = fn })
	end

	-- ---------------------------------------------------- particules
	local function particules(L)
		local pos, dir = resolve(L.ancre, L.t0)
		local p = porteur(dossier, "P_" .. (L.nom or "particules"))
		p.CFrame = repereY(pos, dir)
		local parent = p
		if L.forme and (L.forme.sphere or L.forme.anneau) then
			-- Sphere / Disc exigent un BasePart comme parent (doc officielle)
			local r = L.forme.sphere or L.forme.anneau
			p.Size = Vector3.new(2 * r, L.forme.anneau and 0.2 or 2 * r, 2 * r)
		else
			local att = Instance.new("Attachment")
			att.Parent = p
			parent = att
		end
		local pe = Instance.new("ParticleEmitter")
		pe.Name = L.nom or "particules"
		pe.Enabled = false
		pe.Rate = 0
		pe.Texture = texture(L.texture)
		pe.Lifetime = range(L.lifetime)
		pe.Speed = range(L.speed)
		pe.SpreadAngle = Vector2.new(L.spread[1], L.spread[2])
		pe.Drag = L.drag or 0
		pe.Acceleration = repere:VectorToWorldSpace(vec(L.accel))
		pe.Size = numSeq(L.size)
		pe.Transparency = numSeq(L.transparency)
		pe.Squash = numSeq(L.squash)
		pe.Color = colSeq(L.color)
		pe.LightEmission = L.light_emission or 1
		pe.LightInfluence = 0 -- explicite : Instance.new -> 0, Studio -> 1 (doc officielle)
		pe.Brightness = L.brightness or 1
		pe.Rotation = range(L.rotation)
		pe.RotSpeed = range(L.rotspeed)
		pe.ZOffset = L.zoffset or 0
		pe.Orientation = Enum.ParticleOrientation[L.orientation or "FacingCamera"]
		pe.EmissionDirection = Enum.NormalId.Top
		pe.LockedToPart = L.bloque_a_l_ancre == true
		if L.forme and L.forme.sphere then
			pe.Shape = Enum.ParticleEmitterShape.Sphere
			pe.ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface
			if L.speed[2] <= 0 then
				-- aspiration : l'aperçu tire une vitesse négative, Roblox émet
				-- depuis la surface vers l'intérieur (ShapeInOut Inward)
				pe.ShapeInOut = Enum.ParticleEmitterShapeInOut.Inward
				pe.Speed = NumberRange.new(-L.speed[2], -L.speed[1])
			end
		elseif L.forme and L.forme.anneau then
			pe.Shape = Enum.ParticleEmitterShape.Disc
			pe.ShapePartial = 1
		end
		if L.flipbook then
			local g = L.flipbook.grille
			pe.FlipbookLayout = g == 2 and Enum.ParticleFlipbookLayout.Grid2x2
				or g == 4 and Enum.ParticleFlipbookLayout.Grid4x4
				or Enum.ParticleFlipbookLayout.Grid8x8
			pe.FlipbookMode = Enum.ParticleFlipbookMode[L.flipbook.mode or "OneShot"]
			if L.flipbook.fps then
				pe.FlipbookFramerate = NumberRange.new(math.min(30, L.flipbook.fps))
			end
			pe.FlipbookStartRandom = L.flipbook.depart_aleatoire == true
		end
		pe.Parent = parent
		if L.gel ~= false then
			table.insert(emetteurs, pe) -- une couche peut refuser le gel (halo qui suit l'orbe)
		end
		if L.ancre == "projectile" or (type(L.ancre) == "table" and L.ancre.chemin) then
			-- l'émetteur SUIT son ancre ; les particules déjà émises gardent leur
			-- vitesse de naissance (comportement natif de Roblox)
			table.insert(miseAJour, function(t)
				local pp, dd = resolve(L.ancre, if L.ancre == "projectile" then math.min(t, P.t1) else t)
				p.CFrame = repereY(pp, dd)
			end)
		end
		if L.emit ~= nil then
			ev(L.t0, function()
				pe:Emit(L.emit)
			end)
		else
			ev(L.t0, function()
				pe.Rate = L.rate
				pe.Enabled = true
			end)
			ev(L.t0 + (L.duree_emission or 0), function()
				pe.Enabled = false
			end)
		end
		finMax = math.max(finMax, L.t0 + (L.duree_emission or 0) + L.lifetime[2])
	end

	-- ---------------------------------------------------------- mesh
	local function mesh(L)
		local p = porteur(dossier, "M_" .. (L.nom or L.mesh))
		p.Material = (L.light_emission or 1) >= 0.5 and Enum.Material.Neon or Enum.Material.SmoothPlastic
		local sm = Instance.new("SpecialMesh")
		local mid = ASSETS.meshes[L.mesh]
		if mid then
			sm.MeshType = Enum.MeshType.FileMesh
			sm.MeshId = mid
		else
			-- repli : sphère native (taille = Part.Size * Scale), en attendant l'envoi du mesh
			sm.MeshType = Enum.MeshType.Sphere
			p.Size = Vector3.new(2, 2, 2)
		end
		sm.Parent = p
		table.insert(miseAJour, function(t)
			local a = (t - L.t0) / L.duree
			if a < 0 or a > 1 then
				p.Transparency = 1
				return
			end
			local pos, dir, coup = resolve(L.ancre, t)
			local o = L.orientation or "sol"
			local up = o == "coup" and (coup or dir) or o == "direction" and dir or repere:VectorToWorldSpace(Vector3.new(0, 1, 0))
			local cf = repereY(pos + repere:VectorToWorldSpace(vec(L.decalage or { 0, 0, 0 })), up)
			if L.inclinaison then
				cf = cf * CFrame.Angles(math.rad(L.inclinaison[1]), math.rad(L.inclinaison[2]), math.rad(L.inclinaison[3]))
			end
			cf = cf * CFrame.Angles(0, math.rad((L.rotation_vitesse or 0) * (t - L.t0) + (L.rotation or 0)), 0)
			p.CFrame = cf
			local s = vseq(L.echelle, a)
			sm.Scale = Vector3.new(s[1], s[2], s[3])
			p.Transparency = math.clamp(seq(L.transparency, a), 0, 1)
			local c = colAt(L.color, a)
			local br = L.brightness or 1
			sm.VertexColor = Vector3.new(c[1] * br, c[2] * br, c[3] * br)
			if L.texture then
				-- défilement en U quantifié sur les `nv` variantes décalées de la
				-- texture (formes.py) ; l'aperçu quantifie pareil. Le défilement
				-- en V n'est pas reproduit (critique.py le signale).
				local nv = ASSETS.variantes[L.texture]
				local du = (L.defilement or { 0, 0 })[1]
				if nv and du ~= 0 then
					sm.TextureId = texture(L.texture, math.floor((du * (t - L.t0) % 1) * nv) % nv)
				else
					sm.TextureId = texture(L.texture)
				end
			end
		end)
		finMax = math.max(finMax, L.t0 + L.duree)
	end

	-- ------------------------------------------------- trail / beam
	local function trail(L)
		local p = porteur(dossier, "T_" .. (L.nom or "trail"))
		local lmax = 0
		for _, k in ipairs(L.largeur) do
			lmax = math.max(lmax, k[2])
		end
		local a0, a1 = Instance.new("Attachment"), Instance.new("Attachment")
		a0.Position = Vector3.new(-lmax / 2, 0, 0)
		a1.Position = Vector3.new(lmax / 2, 0, 0)
		a0.Parent, a1.Parent = p, p
		local tr = Instance.new("Trail")
		tr.Attachment0, tr.Attachment1 = a0, a1
		tr.FaceCamera = true
		tr.Lifetime = L.lifetime or 0.3
		tr.Texture = texture(L.texture)
		tr.TextureMode = Enum.TextureMode.Stretch
		tr.LightEmission = L.light_emission or 1
		tr.LightInfluence = 0
		tr.Brightness = L.brightness or 1
		local ws = {}
		for i, k in ipairs(L.largeur) do
			ws[i] = { k[1], k[2] / math.max(lmax, 1e-6), 0 }
		end
		tr.WidthScale = numSeq(ws)
		tr.Transparency = numSeq(L.transparency)
		tr.Color = colSeq(L.color)
		tr.Enabled = false
		tr.Parent = p
		ev(L.t0, function()
			tr.Enabled = true
		end)
		ev(L.t1, function()
			tr.Enabled = false
		end)
		table.insert(miseAJour, function(t)
			local pos, dir = resolve(L.ancre, math.min(t, L.t1_ancre or L.t1))
			p.CFrame = repereY(pos, dir)
		end)
		finMax = math.max(finMax, L.t1 + (L.lifetime or 0.3))
	end

	local function beam(L)
		local p = porteur(dossier, "B_" .. (L.nom or "beam"))
		local a0, a1 = Instance.new("Attachment"), Instance.new("Attachment")
		a0.WorldPosition, a1.WorldPosition = monde(L.de), monde(L.a)
		a0.Parent, a1.Parent = p, p
		local b = Instance.new("Beam")
		b.Attachment0, b.Attachment1 = a0, a1
		b.FaceCamera = true
		b.Segments = L.segments or 10
		b.Texture = texture(L.texture)
		b.TextureSpeed = L.vitesse_texture or 0
		b.TextureLength = L.repetition or 1
		b.TextureMode = Enum.TextureMode.Stretch
		b.LightEmission = L.light_emission or 1
		b.LightInfluence = 0
		b.Width0 = seq(L.largeur, 0)
		b.Width1 = seq(L.largeur, 1)
		b.Transparency = numSeq(L.transparency)
		b.Color = colSeq(L.color)
		b.Enabled = false
		b.Parent = p
		ev(L.t0, function()
			b.Enabled = true
		end)
		ev(L.t0 + L.duree, function()
			b.Enabled = false
		end)
		finMax = math.max(finMax, L.t0 + L.duree)
	end

	local function son(L)
		local id = ASSETS.sons[L.son]
		if not id then
			return -- pas d'identifiant : rien plutôt qu'un son inventé
		end
		-- créé DÈS le lancement (chargement), joué à t0 : pas de retard au
		-- premier Play
		local pos = resolve(L.ancre, L.t0)
		local p = porteur(dossier, "S_" .. L.son)
		p.CFrame = CFrame.new(pos)
		local s = Instance.new("Sound")
		s.Name = L.son
		s.SoundId = id
		s.Volume = L.volume or 1
		s.PlaybackSpeed = L.hauteur or 1
		s.Parent = p
		ev(L.t0, function()
			s:Play()
		end)
		-- le nettoyage attend la fin du son (durée écrite par compile_roblox)
		finMax = math.max(finMax, L.t0 + (L.duree or 2) / (L.hauteur or 1))
	end

	-- ------------------------------------------------- serpent (dragon)
	-- Corps = chaîne de N-1 Beams (FaceCamera) entre N Attachments posés sur
	-- la forme échantillonnée ; tête = carte (Part invisible + 2 Decals : la
	-- face ARRIÈRE porte la texture normale, la face AVANT la texture miroir,
	-- pour que le museau suive toujours le cou, de quelque côté qu'on la voie).
	local camera = opts.camera or workspace.CurrentCamera
	local function serpent(L)
		local N = #L.images[1][2]
		local p = porteur(dossier, "D_" .. (L.nom or "serpent"))
		p.CFrame = CFrame.new(0, 0, 0)
		local atts, beams = {}, {}
		for i = 1, N do
			local a = Instance.new("Attachment")
			a.Parent = p
			atts[i] = a
		end
		local largeur = function(sN)
			return seq(L.largeur, sN)
		end
		for i = 1, N - 1 do
			local b = Instance.new("Beam")
			b.Attachment0, b.Attachment1 = atts[i], atts[i + 1]
			b.FaceCamera = true
			b.Segments = 1
			b.Texture = texture(L.texture)
			b.TextureMode = Enum.TextureMode.Stretch
			b.TextureLength = 1
			b.TextureSpeed = L.vitesse_texture or 0
			b.LightEmission = L.light_emission or 0
			b.LightInfluence = 0
			b.Width0 = largeur((i - 1) / (N - 1))
			b.Width1 = largeur(i / (N - 1))
			local c = colAt(L.color, (i - 0.5) / (N - 1))
			b.Color = ColorSequence.new(Color3.new(c[1], c[2], c[3]))
			b.Transparency = NumberSequence.new(1)
			b.Parent = p
			beams[i] = { b = b, vis = 1 }
		end
		local tete, decals
		if L.tete then
			tete = porteur(dossier, "D_tete")
			tete.Size = Vector3.new(L.tete.taille[1], L.tete.taille[2], 0.05)
			local dos = Instance.new("Decal")
			dos.Face = Enum.NormalId.Back
			dos.Texture = texture(L.tete.texture)
			dos.Parent = tete
			local face = Instance.new("Decal")
			face.Face = Enum.NormalId.Front
			face.Texture = texture(L.tete.texture_miroir or L.tete.texture)
			face.Parent = tete
			decals = { dos, face }
		end
		local function forme(t)
			local im = L.images
			local i = 1
			while i < #im - 1 and im[i + 1][1] <= t do
				i += 1
			end
			local a, b = im[i], im[math.min(i + 1, #im)]
			local u = if b[1] > a[1] then math.clamp((t - a[1]) / (b[1] - a[1]), 0, 1) else 0
			local out = {}
			for k = 1, N do
				local pa, pb = a[2][k], b[2][k]
				out[k] = monde({ pa[1] + (pb[1] - pa[1]) * u, pa[2] + (pb[2] - pa[2]) * u, pa[3] + (pb[3] - pa[3]) * u })
			end
			return out
		end
		table.insert(miseAJour, function(t)
			local a = (t - L.t0) / L.duree
			local actif = a >= 0 and a <= 1
			local s0 = if L.tete_visible then seq(L.tete_visible, a) else 0
			local s1 = if L.queue_visible then seq(L.queue_visible, a) else 1
			local glob = 1 - math.clamp(seq(L.transparency or 0, a), 0, 1)
			local pts = actif and forme(t) or nil
			for i = 1, N - 1 do
				local sa, sb = (i - 1) / (N - 1), i / (N - 1)
				local vis = if actif and sa >= s0 - 1e-6 and sb <= s1 + 1e-6 then 1 - glob else 1
				if pts then
					atts[i].WorldPosition = pts[i]
					atts[i + 1].WorldPosition = pts[i + 1]
				end
				if vis ~= beams[i].vis then
					beams[i].b.Transparency = NumberSequence.new(vis)
					beams[i].vis = vis
				end
			end
			if tete then
				local visible = actif and s0 <= 1e-6 and s1 > 0.02 and glob > 0
				for _, d in ipairs(decals) do
					d.Transparency = if visible then 1 - glob else 1
				end
				if visible then
					-- carte face caméra, museau le long du cou projeté (= aperçu)
					local p0, p3 = pts[1], pts[math.min(4, N)]
					local Z = if camera then (camera.CFrame.Position - p0).Unit else Vector3.new(0, 0, 1)
					local cou = p0 - p3
					local X = cou - Z * cou:Dot(Z)
					if X.Magnitude < 0.25 * cou.Magnitude or X.Magnitude < 1e-4 then
						local droite = if camera then camera.CFrame.RightVector else Vector3.new(1, 0, 0)
						X = droite * (if X:Dot(droite) < 0 then -1 else 1)
					end
					X = X.Unit
					local Y = Z:Cross(X).Unit
					local haut = if camera then camera.CFrame.UpVector else Vector3.new(0, 1, 0)
					if Y:Dot(haut) < 0 then
						Y = -Y
					end
					local centre = p0 + X * (L.tete.taille[1] * (0.5 - (L.tete.cou or 0.12)))
					tete.CFrame = CFrame.fromMatrix(centre, X, Y)
				end
			end
		end)
		finMax = math.max(finMax, L.t0 + L.duree)
	end

	-- -------------------------------------------------------- éclairs
	-- Mêmes tirages que l'aperçu (mulberry32, même graine par couche, même
	-- ordre) : on re-calcule les points à chaque image, les Beams et
	-- Attachments sont créés une fois (jamais de création / destruction).
	local function eclairs(L, graine)
		local K, M = L.brisures or 5, L.nombre or 4
		local p = porteur(dossier, "E_" .. (L.nom or "eclairs"))
		p.CFrame = CFrame.new(0, 0, 0)
		local bolts = {}
		for b = 1, M do
			local atts, beams = {}, {}
			for i = 1, K + 1 do
				local a = Instance.new("Attachment")
				a.Parent = p
				atts[i] = a
			end
			for i = 1, K do
				local bm = Instance.new("Beam")
				bm.Attachment0, bm.Attachment1 = atts[i], atts[i + 1]
				bm.FaceCamera = true
				bm.Segments = 1
				bm.Texture = texture(L.texture or "eclair")
				bm.LightEmission = L.light_emission or 1
				bm.LightInfluence = 0
				bm.Transparency = NumberSequence.new(1)
				bm.Parent = p
				beams[i] = bm
			end
			bolts[b] = { atts = atts, beams = beams, vis = 1 }
		end
		table.insert(miseAJour, function(t)
			local a = (t - L.t0) / L.duree
			local actif = a >= 0 and a <= 1
			local q = math.floor((t - L.t0) / (L.periode or 0.05))
			local pos = actif and resolve(L.ancre, t) or nil
			local glob = 1 - math.clamp(seq(L.transparency or 0, a), 0, 1)
			local c = colAt(L.color, math.clamp(a, 0, 1))
			for b = 1, M do
				local B = bolts[b]
				local vis = 1
				if actif then
					local r = VFXStudio.mulberry(graine * 31 + q * 977 + (b - 1) * 131)
					if r() < (L.presence or 0.8) then
						vis = 1 - glob
					end
					local u1, th, rr = r() * 2 - 1, r() * math.pi * 2, (L.rayon or 1) * r() ^ (1 / 3)
					local st = pos + Vector3.new(math.sqrt(1 - u1 * u1) * math.cos(th), u1, math.sqrt(1 - u1 * u1) * math.sin(th)) * rr
					local v1, ph = r() * 2 - 1, r() * math.pi * 2
					local dir = Vector3.new(math.sqrt(1 - v1 * v1) * math.cos(ph), v1, math.sqrt(1 - v1 * v1) * math.sin(ph))
					local lg = L.longueur[1] + r() * (L.longueur[2] - L.longueur[1])
					local base = repereY(Vector3.new(0, 0, 0), dir)
					local bx, bz = base.RightVector, -base.LookVector
					for i = 0, K do
						local pt = st + dir * (lg * i / K)
						if i > 0 and i < K then
							pt = pt + bx * ((r() * 2 - 1) * lg * 0.22) + bz * ((r() * 2 - 1) * lg * 0.22)
						end
						B.atts[i + 1].WorldPosition = pt
					end
					local w = (L.largeur or 0.2) * (0.6 + 0.4 * r())
					for _, bm in ipairs(B.beams) do
						bm.Width0, bm.Width1 = w, w
						bm.Color = ColorSequence.new(Color3.new(c[1], c[2], c[3]))
					end
				end
				if vis ~= B.vis then
					for _, bm in ipairs(B.beams) do
						bm.Transparency = NumberSequence.new(vis)
					end
					B.vis = vis
				end
			end
		end)
		finMax = math.max(finMax, L.t0 + L.duree)
	end

	-- ------------------------------------------------------- couches
	if P then
		local v = table.clone(P.visuel)
		v.nom = v.nom or "projectile"
		mesh(v)
	end
	-- graine par couche : même suite que l'aperçu (moteur.js, VFX.Effet)
	local graine = rec.graine or 1
	for _, L in ipairs(rec.couches) do
		graine = (graine * 16807) % 2147483647
		if L.type == "serpent" then
			serpent(L)
		elseif L.type == "eclairs" then
			eclairs(L, graine)
		elseif L.type == "particules" then
			particules(L)
		elseif L.type == "mesh" then
			mesh(L)
		elseif L.type == "trail" then
			trail(L)
		elseif L.type == "beam" then
			beam(L)
		elseif L.type == "son" then
			son(L)
		end
	end
	for _, s in ipairs(rec.sons or {}) do
		son(s)
	end

	-- gel du hitstop : TimeScale 0 sur tous les émetteurs
	for _, g in ipairs(rec.gels or {}) do
		ev(g[1], function()
			for _, pe in ipairs(emetteurs) do
				pe.TimeScale = 0
			end
		end)
		ev(g[1] + g[2], function()
			for _, pe in ipairs(emetteurs) do
				pe.TimeScale = 1
			end
		end)
	end

	-- bloom, flash, secousse
	local bloom
	if rec.bloom and opts.bloom ~= false then
		bloom = Instance.new("BloomEffect")
		bloom.Name = "VFX_Bloom"
		bloom.Threshold = rec.bloom.seuil
		bloom.Size = 12 * (rec.bloom.taille or 2) -- [DÉDUIT] l'aperçu règle un rayon relatif, Roblox une taille en pixels
		bloom.Parent = opts.lighting or game:GetService("Lighting")
		table.insert(miseAJour, function(t)
			bloom.Intensity = seq(rec.bloom.intensite, math.clamp(t / rec.duree, 0, 1))
		end)
	end
	local flashFrame
	if rec.flashs and opts.ecran then
		local gui = Instance.new("ScreenGui")
		gui.Name = "VFX_Flash"
		gui.IgnoreGuiInset = true
		gui.Parent = opts.ecran
		flashFrame = Instance.new("Frame")
		flashFrame.Size = UDim2.fromScale(1, 1)
		flashFrame.BorderSizePixel = 0
		flashFrame.BackgroundTransparency = 1
		flashFrame.Parent = gui
		table.insert(miseAJour, function(t)
			local vis = 1
			for _, f in ipairs(rec.flashs) do
				local a = (t - f.t0) / f.duree
				if a >= 0 and a <= 1 then
					local h = f.couleur:gsub("#", "")
					flashFrame.BackgroundColor3 = Color3.fromRGB(tonumber(h:sub(1, 2), 16), tonumber(h:sub(3, 4), 16), tonumber(h:sub(5, 6), 16))
					vis = seq(f.transparency or { { 0, 0 }, { 1, 1 } }, a)
				end
			end
			flashFrame.BackgroundTransparency = vis
		end)
	end
	-- ------------------------------------------------ boucle unique
	table.sort(evenements, function(a, b)
		return a.t < b.t
	end)
	local fini = false
	local dernierDecalage = Vector3.new(0, 0, 0)
	local handle = { Duree = finMax, Dossier = dossier }
	local function etape(t)
		for _, e in ipairs(evenements) do
			if not e.fait and t >= e.t then
				e.fait = true
				e.fn()
			end
		end
		for _, f in ipairs(miseAJour) do
			f(t)
		end
		if opts.camera and rec.secousses then
			-- on retire le décalage de l'image précédente : la secousse ne
			-- s'accumule pas si le script caméra ne réécrit pas la CFrame
			local d = VFXStudio.secousse(rec, t)
			opts.camera.CFrame = opts.camera.CFrame + (d - dernierDecalage)
			dernierDecalage = d
		end
		if t >= finMax and not fini then
			handle.Annuler()
		end
	end
	handle._etape = etape
	local conn
	function handle.Annuler()
		if fini then
			return
		end
		fini = true
		if conn then
			conn:Disconnect()
		end
		if bloom then
			bloom:Destroy()
		end
		if flashFrame then
			flashFrame.Parent:Destroy()
		end
		dossier:Destroy()
	end
	if not opts.manuel then
		local RunService = game:GetService("RunService")
		local debut = os.clock()
		conn = RunService.Heartbeat:Connect(function()
			etape(os.clock() - debut)
		end)
	end
	return handle
end

return VFXStudio
