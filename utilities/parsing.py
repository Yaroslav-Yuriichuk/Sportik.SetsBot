def parse_exercise(text: str) -> tuple[str, int] | None:
    parts = [part for part in text.strip().split() if part]

    if len(parts) < 2:
        return None

    repetitions_text = parts[-1]

    if not repetitions_text.isdigit():
        return None

    exercise_name = " ".join(parts[:-1]).strip()

    if not exercise_name:
        return None

    return exercise_name, int(repetitions_text)
