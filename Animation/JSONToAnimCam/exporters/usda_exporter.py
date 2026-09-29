from .base_exporter import BaseExporter
class USDAExporter(BaseExporter):
    @staticmethod
    def _samples(track, fn):
        return ",\n".join(f"        {key.frame}: {fn(key)}" for key in track.keys)
    def export(self, track, settings):
        op = f"rotate{settings.rotation_order}"
        t = self._samples(track, lambda k: f"({k.tx:.9g}, {k.ty:.9g}, {k.tz:.9g})")
        r = self._samples(track, lambda k: f"({k.rx:.9g}, {k.ry:.9g}, {k.rz:.9g})")
        fl = self._samples(track, lambda k: f"{k.focal_length:.9g}")
        fd = self._samples(track, lambda k: f"{k.focus_distance:.9g}")
        text = f'''#usda 1.0
(
    startTimeCode = {track.keys[0].frame}
    endTimeCode = {track.keys[-1].frame}
    framesPerSecond = {track.fps}
    timeCodesPerSecond = {track.fps}
    metersPerUnit = {settings.metres_per_unit}
    upAxis = "{settings.up_axis}"
)
def Camera "TrackedCamera"
{{
    double3 xformOp:translate.timeSamples = {{
{t}
    }}
    float3 xformOp:{op}.timeSamples = {{
{r}
    }}
    uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:{op}"]
    float focalLength.timeSamples = {{
{fl}
    }}
    float focusDistance.timeSamples = {{
{fd}
    }}
}}
'''
        with open(settings.output_path, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
