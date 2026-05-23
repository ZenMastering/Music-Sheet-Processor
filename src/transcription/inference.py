import librosa
from basic_pitch.inference import predict


def predict_notes(audio_path):
    _, _, note_events = predict(audio_path)
    normalized_notes = []
    for note in note_events:
        if len(note) >= 3:
            start, end, pitch = note[:3]
            normalized_notes.append((start, end, pitch))
    return normalized_notes


def estimate_tempo(audio_path, sr=22050):
    audio, sr = librosa.load(audio_path, sr=sr, mono=True)
    tempo, beat_frames = librosa.beat.beat_track(y=audio, sr=sr)
    return float(tempo), librosa.frames_to_time(beat_frames, sr=sr)
