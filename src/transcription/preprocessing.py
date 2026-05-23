import os
import librosa
import soundfile as sf


def preprocess_audio_file(source_path, output_dir, sr=22050, top_db=25, normalize=True):
    os.makedirs(output_dir, exist_ok=True)

    audio, sr = librosa.load(source_path, sr=sr, mono=True)

    if normalize:
        audio = librosa.util.normalize(audio)

    audio, _ = librosa.effects.trim(audio, top_db=top_db)

    basename = os.path.splitext(os.path.basename(source_path))[0]
    output_path = os.path.join(output_dir, f"{basename}_normalized.wav")
    sf.write(output_path, audio, sr)
    return output_path
