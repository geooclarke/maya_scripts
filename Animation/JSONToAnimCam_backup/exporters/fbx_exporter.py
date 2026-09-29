from .base_exporter import BaseExporter
class FBXExporter(BaseExporter):
    def export(self, track, settings):
        raise RuntimeError("FBX writing is not implemented yet. Choose USD.")
