from fractions import Fraction


def quantize_musical(time, beat_duration, max_denominator=16):
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
