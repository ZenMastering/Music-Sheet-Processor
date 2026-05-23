import customtkinter as ctk
from tkinter import filedialog
from basic_pitch.inference import predict
import librosa
import os
import pretty_midi
import platform
import subprocess
from fractions import Fraction

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
        import soundfile as sf

        audio, sr = librosa.load(selected_file, sr=22050, mono=True)
        audio = librosa.util.normalize(audio)
        audio, _ = librosa.effects.trim(audio, top_db=25)

        temp_file = "temp_clean.wav"
        sf.write(temp_file, audio, sr)

        processed_file = temp_file

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

        model_output, midi_data, note_events = predict(processed_file)

        # tempo alignment algorithm
        audio_for_tempo, sr_for_tempo = librosa.load(
            processed_file,
            sr=22050,
            mono=True
        )

        tempo, beat_frames = librosa.beat.beat_track(
            y=audio_for_tempo,
            sr=sr_for_tempo
        )
        tempo = float(tempo)
        
        beat_times = librosa.frames_to_time(
            beat_frames,
            sr=sr_for_tempo
        )

        beat_duration = 60.0 / tempo

        filtered_notes = [
            n for n in note_events
            if n[1] - n[0] > 0.05  # duration > 50ms
        ]
        
        midi = pretty_midi.PrettyMIDI()

        instrument = pretty_midi.Instrument(program=0)

        for note in filtered_notes:
            pitch = int(note[2])    # MIDI pitch
            start, end = quantize_note_event(
                float(note[0]),
                float(note[1]),
                beat_duration,
                max_denominator=16,
                min_duration=beat_duration / 16
            )

            if end <= start:
                end = start + beat_duration / 16
            instrument.notes.append(
                pretty_midi.Note(
                    velocity=100,
                    pitch=pitch,
                    start=start,
                    end=end
                )
            )
        
        midi.instruments.append(instrument)

        # dev version of file designation
        output_name = "output.mid"
        midi.write(output_name)
        status_label.configure(
            text=f"Transcription complete!\nSaved as {output_name}"
        )
        
        open_file(output_name)
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

def quantize_time(time, grid_size):
    return round(time / grid_size) * grid_size


def quantize_musical(time, beat_duration, max_denominator=16):
    """Snap time to a musical fraction of the beat."""
    ratio = Fraction(time / beat_duration).limit_denominator(max_denominator)
    return float(ratio) * beat_duration


def quantize_note_event(start, end, beat_duration, max_denominator=16, min_duration=None):
    if min_duration is None:
        min_duration = beat_duration / max_denominator

    q_start = quantize_musical(start, beat_duration, max_denominator)
    q_end = quantize_musical(end, beat_duration, max_denominator)

    if q_end <= q_start:
        q_end = q_start + min_duration

    if q_end - q_start < min_duration:
        q_end = q_start + min_duration

    return q_start, q_end


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
