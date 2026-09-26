--!nonstrict
--[[
	Demo : rejoue le Poing du Dragon en boucle sur les deux mannequins du
	dossier. Script en RunContext = Client : il tourne dans le Workspace, en
	Play dans Studio. La camera cinematique ne s'active que si le
	personnage du joueur est l'attaquant (CONFIG.CAMERA) : pour la voir dans
	la demo, passer DEMO_CAMERA a true (la camera du joueur est alors pilotee
	pendant la technique).
]]

local folder = script.Parent
local DragonFist = require(folder:WaitForChild("DragonFist"))
local data = require(folder:WaitForChild("DragonFistData"))
local attacker = folder:WaitForChild("Attaquant")
local victim = folder:WaitForChild("Victime")
local animations = folder:WaitForChild("Animations")

local DEMO_CAMERA = true

local aRoot = attacker:WaitForChild("HumanoidRootPart")
local home = aRoot.CFrame
task.wait(2)
while true do
	aRoot.CFrame = home
	if DEMO_CAMERA then
		-- la demo filme les mannequins : on force la camera cinematique
		local camera = workspace.CurrentCamera
		local oldType = camera.CameraType
		camera.CameraType = Enum.CameraType.Scriptable
		local track = DragonFist.play(attacker, victim, animations, data, true)
		track.Stopped:Wait()
		camera.CameraType = oldType
	else
		local track = DragonFist.play(attacker, victim, animations, data)
		track.Stopped:Wait()
	end
	task.wait(3)
end
