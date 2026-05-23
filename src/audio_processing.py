import librosa
import soundfile as sf
import tempfile

def preprocess_audio(input_file):
    audio, sr = librosa.load(
        input_file,
        sr=22050,
        mono=True
    )

    audio = librosa.util.normalize(audio)
    audio, _ = librosa.effects.trim(audio, top_db=25)

    temp = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    sf.write(temp.name, audio, sr)

    return temp.name