--!nonstrict
--[[
	Demo : rejoue « Un seul coup » en boucle sur les deux mannequins du
	dossier. Script en RunContext = Client : il tourne dans le Workspace, en
	Play dans Studio. DEMO_CAMERA = true : la caméra cinématique filme les
	mannequins (la caméra du joueur est pilotée pendant la technique).
]]

local folder = script.Parent
local UnSeulCoup = require(folder:WaitForChild("UnSeulCoup"))
local data = require(folder:WaitForChild("UnSeulCoupData"))
local attacker = folder:WaitForChild("Attaquant")
local victim = folder:WaitForChild("Victime")
local animations = folder:WaitForChild("Animations")

local DEMO_CAMERA = true

local aRoot = attacker:WaitForChild("HumanoidRootPart")
local home = aRoot.CFrame
task.wait(2)
while true do
	aRoot.CFrame = home
	local camera = workspace.CurrentCamera
	local oldType = camera.CameraType
	if DEMO_CAMERA then
		camera.CameraType = Enum.CameraType.Scriptable
	end
	local track = UnSeulCoup.play(attacker, victim, animations, data, DEMO_CAMERA)
	track.Stopped:Wait()
	camera.CameraType = oldType
	task.wait(UnSeulCoup.CONFIG.CLEANUP_TIME + 1)
end
