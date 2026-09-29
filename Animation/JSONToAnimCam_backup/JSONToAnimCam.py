#!/usr/bin/env python3
import json
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, messagebox
from typing import List

from export_dialog import get_export_settings
from exporters import AlembicExporter, FBXExporter, USDAExporter

@dataclass
class CameraSample:
    timecode: str; frame: int
    x: float; y: float; z: float
    pan: float; tilt: float; roll: float
    zoom: float; focus: float; iris: float

@dataclass
class CameraKey:
    frame: int; tx: float; ty: float; tz: float
    rx: float; ry: float; rz: float
    focal_length: float; focus_distance: float; iris: float

@dataclass
class CameraTrack:
    fps: int; keys: List[CameraKey]
    start_timecode: str; end_timecode: str

def select_input_file():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select Camera Tracking File",
        filetypes=[("JSONL", "*.jsonl"), ("All Files", "*.*")],
        parent=root,
    )
    root.destroy()
    return path

def timecode_frame(value, fps):
    h, m, s, f = map(int, value.split(":"))
    if not (0 <= m < 60 and 0 <= s < 60 and 0 <= f < fps):
        raise ValueError(f"Invalid timecode: {value}")
    return ((h * 3600 + m * 60 + s) * fps) + f

def load_jsonl(path, fps):
    required = ("tc", "x", "y", "z", "pan", "tilt", "roll")
    samples = []
    with open(path, encoding="utf-8-sig") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                missing = [key for key in required if key not in data]
                if missing:
                    raise ValueError(f"missing fields {missing}")
                tc = str(data["tc"])
                samples.append(CameraSample(
                    tc, timecode_frame(tc, fps),
                    float(data["x"]), float(data["y"]), float(data["z"]),
                    float(data["pan"]), float(data["tilt"]), float(data["roll"]),
                    float(data.get("zoom", 0)), float(data.get("focus", 0)),
                    float(data.get("iris", 0)),
                ))
            except Exception as error:
                raise ValueError(f"Invalid tracking data on line {number}: {error}") from error
    if not samples:
        raise ValueError("The selected file contains no samples.")
    samples.sort(key=lambda item: item.frame)
    first = samples[0].frame
    for item in samples:
        item.frame -= first
    return samples

def build_track(samples, settings):
    keys = [CameraKey(
        sample.frame + settings.start_frame,
        sample.x * 100, sample.z * 100, -sample.y * 100,
        sample.tilt, sample.pan, sample.roll,
        sample.zoom if sample.zoom > 0 else 35,
        sample.focus * 100, sample.iris,
    ) for sample in samples]
    return CameraTrack(settings.fps, keys, samples[0].timecode, samples[-1].timecode)

def show_error(message):
    root = tk.Tk(); root.withdraw()
    messagebox.showerror("Export Failed", message, parent=root)
    root.destroy()

def show_success(message):
    root = tk.Tk(); root.withdraw()
    messagebox.showinfo("Export Complete", message, parent=root)
    root.destroy()

def main():
    try:
        source = select_input_file()
        if not source:
            return
        settings = get_export_settings(source)
        if settings is None:
            return
        track = build_track(load_jsonl(source, settings.fps), settings)
        exporter = {
            ".usda": USDAExporter,
            ".fbx": FBXExporter,
            ".abc": AlembicExporter,
        }[settings.file_type]()
        exporter.export(track, settings)
        show_success(f"Exported {len(track.keys)} keys to:\n{settings.output_path}")
    except Exception as error:
        show_error(str(error))

if __name__ == "__main__":
    main()
