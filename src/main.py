import customtkinter as ctk
from tkinter import filedialog
import os
import platform
import subprocess

from transcription.preprocessing import preprocess_audio_file
from transcription.inference import predict_notes, estimate_tempo
from midi_generation.midi_writer import write_midi

# -----------------------------
# APP CONFIG
# -----------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Music Sheet Processor")
app.geometry("700x500")

sr_global = None
selected_file = None
processed_audio = None
processed_file = None

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO_DIR = os.path.join(ROOT_DIR, "audio")
MIDI_DIR = os.path.join(ROOT_DIR, "midi")
SHEET_MUSIC_DIR = os.path.join(ROOT_DIR, "sheet_music")


# -----------------------------
# FUNCTIONS
# -----------------------------

def upload_audio():
    global selected_file

    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Audio Files", "*.wav *.mp3")
        ]
    )

    if file_path:
        selected_file = file_path
        file_label.configure(text=f"Loaded:\n{os.path.basename(file_path)}")
        status_label.configure(text="Ready to transcribe")

def preprocess_audio():
    global selected_file, processed_file

    if not selected_file:
        status_label.configure(text="No audio file selected")
        return

    try:
        processed_file = preprocess_audio_file(selected_file, AUDIO_DIR)
        status_label.configure(text="Preprocessed ✔")

    except Exception as e:
        status_label.configure(text=f"Error:\n{str(e)}")

def transcribe_audio():
    global processed_file

    if not processed_file:
        status_label.configure(text="You need to process the file first")
        return

    try:
        status_label.configure(text="Transcribing...")

        note_events = predict_notes(processed_file)
        tempo, _ = estimate_tempo(processed_file)
        beat_duration = 60.0 / tempo

        output_name = f"{os.path.splitext(os.path.basename(selected_file))[0]}_quantized.mid"
        output_path = write_midi(
            note_events,
            beat_duration,
            output_name,
            output_dir=MIDI_DIR,
            max_denominator=16,
            min_duration=beat_duration / 16,
            duration_threshold=0.05,
        )

        status_label.configure(text=f"Transcription complete!\nSaved as {output_path}")
        open_file(output_path)
        # # official name and directory designation
        # output_name = filedialog.asksaveasfilename(
        #     defaultextension=".mid",
        #     filetypes=[("MIDI Files", "*.mid")],
        #     initialfile="output.mid"
        # )

        # if not output_name:
        #     return

        # midi.write(output_name)
        # status_label.configure(
        #     text=f"Transcription complete!\nSaved as {output_name}"
        # )
        # open_file(output_name)
    except Exception as e:
        status_label.configure(text=f"Error:\n{str(e)}")

# -----------------------------
# Helper Functions
# -----------------------------

# Supports multiple platforms
def open_file(path):
    system = platform.system()

    if system == "Windows":
        os.startfile(path)
    elif system == "Darwin":
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])

# -----------------------------
# UI
# -----------------------------

title_label = ctk.CTkLabel(
    app,
    text="Music Sheet Processor",
    font=("Arial", 28, "bold")
)
title_label.pack(pady=30)

upload_button = ctk.CTkButton(
    app,
    text="Upload Audio",
    command=upload_audio,
    width=220,
    height=50,
    font=("Arial", 18)
)
upload_button.pack(pady=20)

file_label = ctk.CTkLabel(
    app,
    text="No file selected",
    font=("Arial", 16)
)
file_label.pack(pady=10)

preprocess_button = ctk.CTkButton(
    app,
    text="Preprocess Audio",
    command=preprocess_audio,
    width=220,
    height=50,
    font=("Arial", 18)
)
preprocess_button.pack(pady=10)

transcribe_button = ctk.CTkButton(
    app,
    text="Start Transcription",
    command=transcribe_audio,
    width=220,
    height=50,
    font=("Arial", 18)
)
transcribe_button.pack(pady=20)

status_label = ctk.CTkLabel(
    app,
    text="Waiting for input",
    font=("Arial", 16)
)
status_label.pack(pady=30)

# -----------------------------
# RUN APP
# -----------------------------

app.mainloop()
