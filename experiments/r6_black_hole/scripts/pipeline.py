"""
Point d'entree UNIQUE pour obtenir les echantillons du personnage :
pistes (choreography.character_tracks) -> courbes Bezier Blender
(anim_engine.apply_tracks) -> ressorts -> contraintes (pieds plantes,
regard) -> cinematique directe. Lecteur, calibrate, audit et export
passent tous par ici : ce qui est mesure est exactement ce qui est rendu
et exporte.
"""
import anim_engine as ae
import choreography as ch

_LAST_LOG = {}


def build_samples(sample_hz=60):
    tracks, offset_log = ch.character_tracks()
    objs = ae.build_rig()
    ae.apply_tracks(objs, tracks)
    constraint_log = {}

    def post(local_samples):
        constraint_log.update(ch.post_local(local_samples))

    samples = ae.sample(objs, duration_s=ch.TOTAL_DURATION, sample_hz=sample_hz,
                        secondary_motion=ch.SECONDARY_MOTION, post_local=post)
    _LAST_LOG.clear()
    _LAST_LOG.update({"overlap_adjustments": offset_log, "constraints": constraint_log})
    return samples, ch.TOTAL_DURATION


def last_log():
    return dict(_LAST_LOG)
