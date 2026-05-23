import os
import pretty_midi

from .quantizer import quantize_note_event


def write_midi(note_events, beat_duration, output_name, output_dir, program=0, velocity=100, max_denominator=16, min_duration=None, duration_threshold=0.05):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_name)
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=program)

    for note in note_events:
        start, end, pitch = note[:3]
        if end - start < duration_threshold:
            continue

        q_start, q_end = quantize_note_event(
            start,
            end,
            beat_duration,
            max_denominator=max_denominator,
            min_duration=min_duration,
        )

        if q_end <= q_start:
            q_end = q_start + (min_duration or beat_duration / max_denominator)

        instrument.notes.append(
            pretty_midi.Note(
                velocity=velocity,
                pitch=int(pitch),
                start=q_start,
                end=q_end,
            )
        )

    midi.instruments.append(instrument)
    midi.write(output_path)
    return output_path
