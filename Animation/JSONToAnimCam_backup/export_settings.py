from dataclasses import dataclass


@dataclass
class CommonExportSettings:
    output_path: str
    file_type: str
    start_frame: int = 1001
    fps: int = 25
    rotation_order: str = "XYZ"


@dataclass
class FBXSettings(CommonExportSettings):
    ascii: bool = False
    fbx_version: str = "FBX 2020"
    bake_animation: bool = True


@dataclass
class AlembicSettings(CommonExportSettings):
    archive_type: str = "Ogawa"
    frame_step: float = 1.0
    world_space: bool = True


@dataclass
class USDASettings(CommonExportSettings):
    up_axis: str = "Y"
    metres_per_unit: float = 0.01
