--!nonstrict
--[[
	Demo : rejoue le M1 en boucle sur les deux mannequins du dossier.
	Script en RunContext = Client : il tourne ou qu'il soit (ici, dans le
	dossier M1_Technique du Workspace), en Play dans Studio.
	Deplacer/tourner l'Attaquant suffit : la victime se replace devant lui.
]]

local folder = script.Parent
local M1 = require(folder:WaitForChild("M1Technique"))
local attacker = folder:WaitForChild("Attaquant")
local victim = folder:WaitForChild("Victime")
local animations = folder:WaitForChild("Animations")

task.wait(1)
while true do
	M1.placeVictim(attacker, victim)
	M1.play(attacker, victim, animations)
	task.wait(2.2)
end
