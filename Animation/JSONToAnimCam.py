#!/usr/bin/env python3

"""
camera_converter_core.py

Common camera parsing and transformation layer.

Flow:

JSON
 ↓
CameraTrack
 ↓
Coordinate Conversion
 ↓
Rotation Conversion
 ↓
Exporter (FBX / Alembic / USD)

No exporter-specific logic should exist here.
"""

from dataclasses import dataclass
from typing import List
import json


# ==========================================================
# Timecode
# ==========================================================

def tc_to_frame(tc: str, fps: int) -> int:
    """
    Convert HH:MM:SS:FF to absolute frame number.
    """

    h, m, s, f = map(int, tc.split(":"))
    return ((h * 3600 + m * 60 + s) * fps) + f


# ==========================================================
# Raw Sample
# ==========================================================

@dataclass
class CameraSample:

    timecode: str

    frame: int
    source_frame = int(
        data.get("frame", 0)
    )

    tx: float
    ty: float
    tz: float

    pan: float
    tilt: float
    roll: float

    zoom: float
    focus: float
    iris: float

    offset_ms: float


# ==========================================================
# Export-Ready Key
# ==========================================================

@dataclass
class CameraKey:

    frame: int

    tx: float
    ty: float
    tz: float

    rx: float
    ry: float
    rz: float

    focal_length: float
    focus_distance: float
    iris: float


# ==========================================================
# Camera Track
# ==========================================================

@dataclass
class CameraTrack:

    fps: int
    keys: List[CameraKey]


# ==========================================================
# Rotation Mapping
# ==========================================================

class RotationMapper:

    def __init__(
        self,
        pan_axis="ry",
        tilt_axis="rx",
        roll_axis="rz",
        invert_pan=False,
        invert_tilt=False,
        invert_roll=False
    ):

        self.pan_axis = pan_axis
        self.tilt_axis = tilt_axis
        self.roll_axis = roll_axis

        self.invert_pan = invert_pan
        self.invert_tilt = invert_tilt
        self.invert_roll = invert_roll

    def convert(self, pan, tilt, roll):

        rotations = {
            "rx": 0.0,
            "ry": 0.0,
            "rz": 0.0
        }

        rotations[self.pan_axis] = -pan if self.invert_pan else pan
        rotations[self.tilt_axis] = -tilt if self.invert_tilt else tilt
        rotations[self.roll_axis] = -roll if self.invert_roll else roll

        return (
            rotations["rx"],
            rotations["ry"],
            rotations["rz"]
        )


# ==========================================================
# Coordinate Mapping
# ==========================================================

class CoordinateMapper:

    """
    Example mappings:

    Maya Y-Up

        X -> X
        Y -> -Z
        Z -> Y

    Blender

        X -> X
        Y -> Y
        Z -> Z

    Custom mappings can be added later.
    """

    def __init__(self, mode="maya_yup"):

        self.mode = mode

    def convert(self, x, y, z):

        if self.mode == "maya_yup":

            return (
                x * 100.0,
                z * 100.0,
                -y * 100.0
            )

        elif self.mode == "raw":

            return (
                x * 100.0,
                y * 100.0,
                z * 100.0
            )

        raise ValueError(
            f"Unknown coordinate mapping: {self.mode}"
        )


# ==========================================================
# Parser
# ==========================================================

# ==========================================================
# Parser
# ==========================================================

class CameraParser:

    REQUIRED_FIELDS = (
        "tc",
        "x",
        "y",
        "z",
        "pan",
        "tilt",
        "roll"
    )

    @staticmethod
    def load_jsonl(path, fps):

        samples = []

        with open(path, "r", encoding="utf-8") as f:

            for line_number, line in enumerate(f, start=1):

                line = line.strip()

                if not line:
                    continue

                try:
                    data = json.loads(line)

                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid JSON on line {line_number}: {e}"
                    )

                missing = [
                    field
                    for field in CameraParser.REQUIRED_FIELDS
                    if field not in data
                ]

                if missing:
                    raise ValueError(
                        f"Line {line_number} missing fields: {missing}"
                    )

                tc = str(data["tc"])

                samples.append(

                    CameraSample(

                        timecode=tc,

                        frame=tc_to_frame(
                            tc,
                            fps
                        ),

                        tx=float(data["x"]),
                        ty=float(data["y"]),
                        tz=float(data["z"]),

                        pan=float(data["pan"]),
                        tilt=float(data["tilt"]),
                        roll=float(data["roll"]),

                        zoom=float(data.get("zoom", 0.0)),
                        focus=float(data.get("focus", 0.0)),
                        iris=float(data.get("iris", 0.0)),

                        offset_ms=float(
                            data.get("offset_ms", 0.0)
                        )
                    )
                )

        samples.sort(
            key=lambda sample: sample.frame
        )

        return samples


# ==========================================================
# Track Builder
# ==========================================================

class CameraTrackBuilder:

    @staticmethod
    def build(
        samples,
        coordinate_mapper,
        rotation_mapper
    ):

        keys = []

        for sample in samples:

            tx, ty, tz = coordinate_mapper.convert(
                sample.tx,
                sample.ty,
                sample.tz
            )

            rx, ry, rz = rotation_mapper.convert(
                sample.pan,
                sample.tilt,
                sample.roll
            )

            focal = sample.zoom

            if focal <= 0:
                focal = 35.0

            keys.append(

                CameraKey(

                    frame=sample.frame,

                    tx=tx,
                    ty=ty,
                    tz=tz,

                    rx=rx,
                    ry=ry,
                    rz=rz,

                    focal_length=focal,

                    focus_distance=sample.focus * 100.0,

                    iris=sample.iris
                )
            )

        fps = None

        if samples:
            fps = 25

        return CameraTrack(
            fps=fps,
            keys=keys
        )


# ==========================================================
# Exporter Base Class
# ==========================================================

class BaseExporter:

    EXTENSION = ""

    def export(
        self,
        track,
        output_path
    ):
        raise NotImplementedError