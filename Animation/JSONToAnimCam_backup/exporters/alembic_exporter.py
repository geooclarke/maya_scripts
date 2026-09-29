from .base_exporter import BaseExporter


class AlembicExporter(BaseExporter):
    """Export an animated transform and camera through PyAlembic."""

    ROTATE_TYPES = {
        "X": "kRotateXOperation",
        "Y": "kRotateYOperation",
        "Z": "kRotateZOperation",
    }

    @staticmethod
    def _imports():
        try:
            from alembic3d import Abc, AbcCoreAbstract, AbcGeom
            from imath import V3d
        except ImportError as error:
            raise RuntimeError(
                "Alembic export needs the bundled alembic3d and Imath bindings."
            ) from error
        return Abc, AbcCoreAbstract, AbcGeom, V3d

    def export(self, track, settings):
        if not track.keys:
            raise ValueError("Cannot export an empty camera track.")
        if settings.archive_type != "Ogawa":
            raise ValueError(
                "This standalone exporter currently supports Ogawa archives only."
            )
        if settings.frame_step <= 0:
            raise ValueError("Alembic frame step must be greater than zero.")

        Abc, AbcCoreAbstract, AbcGeom, V3d = self._imports()

        seconds_per_sample = float(settings.frame_step) / float(track.fps)
        start_seconds = float(track.keys[0].frame) / float(track.fps)
        time_sampling = AbcCoreAbstract.TimeSampling(
            seconds_per_sample, start_seconds
        )

        archive = Abc.OArchive(settings.output_path)
        time_sampling_index = archive.addTimeSampling(time_sampling)

        camera_xform = AbcGeom.OXform(
            archive.getTop(), "TrackedCamera_Xform", time_sampling_index
        )
        camera = AbcGeom.OCamera(
            camera_xform, "TrackedCamera", time_sampling_index
        )
        xform_schema = camera_xform.getSchema()
        camera_schema = camera.getSchema()

        operation_type = AbcGeom.XformOperationType
        translation_op = AbcGeom.XformOp(operation_type.kTranslateOperation)
        rotation_ops = {
            axis: AbcGeom.XformOp(
                getattr(operation_type, self.ROTATE_TYPES[axis])
            )
            for axis in "XYZ"
        }

        for key in track.keys:
            xform_sample = AbcGeom.XformSample()
            xform_sample.addOp(
                translation_op, V3d(key.tx, key.ty, key.tz)
            )
            rotations = {"X": key.rx, "Y": key.ry, "Z": key.rz}
            for axis in settings.rotation_order:
                xform_sample.addOp(rotation_ops[axis], rotations[axis])
            xform_schema.set(xform_sample)

            camera_sample = AbcGeom.CameraSample()
            camera_sample.setFocalLength(key.focal_length)
            camera_sample.setFocusDistance(key.focus_distance)
            camera_sample.setHorizontalAperture(3.6)
            camera_sample.setVerticalAperture(2.025)
            camera_schema.set(camera_sample)

        # Releasing archive-owned objects finalises the file in PyAlembic.
        del camera_schema, xform_schema, camera, camera_xform, archive
