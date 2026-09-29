import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from export_settings import AlembicSettings, FBXSettings, USDASettings

FORMATS = {"USD": ".usda", "FBX": ".fbx", "Alembic": ".abc"}
ROTATION_ORDERS = ("XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX")


def get_export_settings(input_file):
    """Open the export-options window as its own visible Tk root."""
    root = tk.Tk()
    root.title("Camera Export Options")
    root.resizable(False, False)

    result = {}
    source_name = os.path.splitext(os.path.basename(input_file))[0]
    source_folder = os.path.dirname(input_file)

    outer = ttk.Frame(root, padding=14)
    outer.grid(sticky="nsew")

    general = ttk.LabelFrame(outer, text="Export", padding=10)
    general.grid(row=0, column=0, sticky="ew")
    general.columnconfigure(1, weight=1)

    format_frame = ttk.LabelFrame(outer, text="Format Settings", padding=10)
    format_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

    def label(text, row):
        ttk.Label(general, text=text).grid(
            row=row, column=0, sticky="w", padx=(0, 12), pady=4
        )

    # Use direct widget insertion rather than Tk variables for the core defaults.
    label("File Name", 0)
    file_name_entry = ttk.Entry(general, width=38)
    file_name_entry.grid(row=0, column=1, sticky="ew", pady=4)
    file_name_entry.insert(0, source_name)

    label("File Type", 1)
    file_type_box = ttk.Combobox(
        general, values=tuple(FORMATS), state="readonly", width=35
    )
    file_type_box.grid(row=1, column=1, sticky="ew", pady=4)
    file_type_box.current(0)

    label("Start Frame", 2)
    start_frame_spin = ttk.Spinbox(general, from_=0, to=999999, width=14)
    start_frame_spin.grid(row=2, column=1, sticky="w", pady=4)
    start_frame_spin.insert(0, "1001")

    label("FPS", 3)
    fps_spin = ttk.Spinbox(general, from_=1, to=240, width=14)
    fps_spin.grid(row=3, column=1, sticky="w", pady=4)
    fps_spin.insert(0, "25")

    label("Rotation Order", 4)
    rotation_box = ttk.Combobox(
        general, values=ROTATION_ORDERS, state="readonly", width=12
    )
    rotation_box.grid(row=4, column=1, sticky="w", pady=4)
    rotation_box.current(0)

    label("Output Folder", 5)
    folder_frame = ttk.Frame(general)
    folder_frame.grid(row=5, column=1, sticky="ew", pady=4)
    output_folder_entry = ttk.Entry(folder_frame, width=29)
    output_folder_entry.pack(side="left", fill="x", expand=True)
    output_folder_entry.insert(0, source_folder)

    def browse_folder():
        folder = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=output_folder_entry.get() or source_folder,
            parent=root,
        )
        if folder:
            output_folder_entry.delete(0, tk.END)
            output_folder_entry.insert(0, folder)

    ttk.Button(folder_frame, text="Browse...", command=browse_folder).pack(
        side="left", padx=(6, 0)
    )

    # Format-specific variables can safely belong to this root.
    fbx_version = tk.StringVar(root, value="FBX 2020")
    fbx_encoding = tk.StringVar(root, value="Binary")
    fbx_bake = tk.BooleanVar(root, value=True)
    abc_archive = tk.StringVar(root, value="Ogawa")
    abc_step = tk.DoubleVar(root, value=1.0)
    abc_world = tk.BooleanVar(root, value=True)

    def add_format_row(row, text, widget):
        ttk.Label(format_frame, text=text).grid(
            row=row, column=0, sticky="w", padx=(0, 12), pady=4
        )
        widget.grid(row=row, column=1, sticky="ew", pady=4)

    def show_format_settings(_event=None):
        for child in format_frame.winfo_children():
            child.destroy()

        selected = file_type_box.get()
        if selected == "FBX":
            version_box = ttk.Combobox(
                format_frame,
                textvariable=fbx_version,
                values=("FBX 2020", "FBX 2019", "FBX 2018", "FBX 2016/2017"),
                state="readonly",
            )
            add_format_row(0, "FBX Version", version_box)
            encoding_box = ttk.Combobox(
                format_frame,
                textvariable=fbx_encoding,
                values=("Binary", "ASCII"),
                state="readonly",
            )
            add_format_row(1, "Encoding", encoding_box)
            ttk.Checkbutton(
                format_frame, text="Bake Animation", variable=fbx_bake
            ).grid(row=2, column=0, columnspan=2, sticky="w", pady=4)
        elif selected == "Alembic":
            archive_box = ttk.Combobox(
                format_frame,
                textvariable=abc_archive,
                values=("Ogawa",),
                state="readonly",
            )
            add_format_row(0, "Archive Type", archive_box)
            step_spin = ttk.Spinbox(
                format_frame,
                textvariable=abc_step,
                from_=0.01,
                to=100,
                increment=0.1,
            )
            add_format_row(1, "Frame Step", step_spin)
            ttk.Checkbutton(
                format_frame,
                text="World-space Transforms",
                variable=abc_world,
            ).grid(row=2, column=0, columnspan=2, sticky="w", pady=4)
        else:
            ttk.Label(
                format_frame,
                text="USD ASCII, Y-up, centimetre scene units",
            ).grid(row=0, column=0, sticky="w")

    file_type_box.bind("<<ComboboxSelected>>", show_format_settings)
    show_format_settings()

    def submit():
        name = file_name_entry.get().strip()
        folder = output_folder_entry.get().strip()
        try:
            start_frame = int(start_frame_spin.get())
            fps = int(fps_spin.get())
        except ValueError:
            messagebox.showerror(
                "Invalid Settings", "Start Frame and FPS must be whole numbers.", parent=root
            )
            return

        if not name or not folder:
            messagebox.showerror(
                "Invalid Settings",
                "File Name and Output Folder are required.",
                parent=root,
            )
            return
        if start_frame < 0 or fps < 1:
            messagebox.showerror(
                "Invalid Settings",
                "Start Frame must be 0 or greater and FPS must be at least 1.",
                parent=root,
            )
            return

        extension = FORMATS[file_type_box.get()]
        common = dict(
            output_path=os.path.join(folder, os.path.splitext(name)[0] + extension),
            file_type=extension,
            start_frame=start_frame,
            fps=fps,
            rotation_order=rotation_box.get(),
        )

        if extension == ".fbx":
            result["settings"] = FBXSettings(
                **common,
                ascii=fbx_encoding.get() == "ASCII",
                fbx_version=fbx_version.get(),
                bake_animation=fbx_bake.get(),
            )
        elif extension == ".abc":
            result["settings"] = AlembicSettings(
                **common,
                archive_type=abc_archive.get(),
                frame_step=float(abc_step.get()),
                world_space=abc_world.get(),
            )
        else:
            result["settings"] = USDASettings(**common)
        root.destroy()

    buttons = ttk.Frame(outer)
    buttons.grid(row=2, column=0, sticky="e", pady=(12, 0))
    ttk.Button(buttons, text="Cancel", command=root.destroy).pack(side="right")
    ttk.Button(buttons, text="Export", command=submit).pack(
        side="right", padx=(0, 6)
    )

    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.bind("<Return>", lambda _event: submit())
    root.bind("<Escape>", lambda _event: root.destroy())
    root.after(100, root.lift)
    file_name_entry.focus_set()
    root.mainloop()
    return result.get("settings")
