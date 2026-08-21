"""Phase 2.2 (MANDAT SUITE v2) : passe Normal reutilisable, extraite de
experiments/tool_evals/bake_normal_cendre.py (T.1.2, deja verifiee par
deux methodes independantes - hemisphere synthetique + sphere de
reference - convention Y+ = haut de l'image, aucun flip necessaire pour
Godot CanvasTexture.normal_texture + Light2D). Ce module ne fait QUE la
passe Normal ; la passe beauty reste celle deja geree par chaque script
appelant (rig_final_crawler.py/rig_final_brute.py/capture_pose.py) - pas
de duplication de la logique de camera/eclairage.
"""

import bpy


def render_normal_pass(scene, out_path: str) -> None:
    """Rend une passe Normal espace camera (remappee [-1,1]->[0,1]) sur
    la camera/scene DEJA en place (appeler juste apres le rendu beauty
    correspondant, avant de changer de pose/camera). Restaure use_nodes
    a False en sortie pour ne pas affecter un rendu beauty suivant."""
    view_layer = scene.view_layers[0]
    view_layer.use_pass_normal = True
    scene.use_nodes = True
    tree = scene.node_tree
    for n in list(tree.nodes):
        tree.nodes.remove(n)
    rl = tree.nodes.new("CompositorNodeRLayers")
    mul = tree.nodes.new("CompositorNodeMixRGB")
    mul.blend_type = "MULTIPLY"
    mul.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
    add = tree.nodes.new("CompositorNodeMixRGB")
    add.blend_type = "ADD"
    add.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
    alpha = tree.nodes.new("CompositorNodeSetAlpha")
    comp = tree.nodes.new("CompositorNodeComposite")
    tree.links.new(rl.outputs["Normal"], mul.inputs[1])
    tree.links.new(mul.outputs["Image"], add.inputs[1])
    tree.links.new(add.outputs["Image"], alpha.inputs["Image"])
    tree.links.new(rl.outputs["Alpha"], alpha.inputs["Alpha"])
    tree.links.new(alpha.outputs["Image"], comp.inputs["Image"])

    prev_view_transform = scene.view_settings.view_transform
    scene.view_settings.view_transform = "Standard"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_management = "OVERRIDE"
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    scene.view_settings.view_transform = prev_view_transform
    scene.use_nodes = False
