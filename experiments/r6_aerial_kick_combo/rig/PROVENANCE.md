# Rig R6 — provenance

`RigR6.rbxmx` : rig R6 Roblox complet (Head, Torso, Left/Right Arm,
Left/Right Leg, HumanoidRootPart + les 6 Motor6D), récupéré depuis GitHub.

- Source : https://github.com/Epix-Incorporated/Adonis
  chemin `MainModule/Server/Dependencies/Assets/RigR6.rbxmx`
- Licence : MIT (Copyright (c) 2016-2026 Sceleratis, Epix Incorporated,
  and the Adonis Community) — voir LICENSE.md du dépôt source.
- Récupéré le 2026-09-01 via `raw.githubusercontent.com` (80 998 octets).

## Pourquoi celui-ci

Les résultats de recherche GitHub renvoyaient surtout des
`RCCService*/content/models/Thumbnails/Mannequins/R6.rbxmx` : ce sont des
dumps de contenu client/serveur Roblox redistribués (dépôts de private
servers), donc du contenu propriétaire sans licence de redistribution.
Écartés au profit d'une source clairement licenciée MIT, d'un projet
open-source connu et maintenu.

## Particularité à connaître

Toutes les parts du modèle portent la rotation `Ry(180°)`
(`[[-1,0,0],[0,1,0],[0,0,-1]]`) : le modèle est sauvegardé **retourné**,
ce qui explique que "Right Arm" y soit à X = -1.5 et "Left Arm" à X = +1.5.
C'est sans effet sur ce qu'on en extrait : les `C0`/`C1` des Motor6D sont
exprimés dans le repère LOCAL de chaque part, donc invariants par rotation
globale du modèle. On ne lit jamais les `CFrame` monde des parts comme
référence de repos — uniquement les tailles et les C0/C1.
