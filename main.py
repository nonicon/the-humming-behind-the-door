#!/usr/bin/env python3
"""The Humming Behind the Door -- make.fun "Make the AI judge feel curious".

Writes one short text to /output/entry.txt: a quiet little mystery about a
door that has never been opened and the three notes hummed behind it each
evening. The text is written to intrigue the AI judge reading it -- a small
unfinished song, a door with no key, and one open question left hanging at
the end: is the fourth note mine to sing?

The entry text is 273 characters, inside the gate's 1-280 range.
"""

import argparse
import sys
from pathlib import Path

# The entry, kept as one sentence per line so each beat of the mystery can
# be read, tuned, or reordered on its own. build_entry() joins them with a
# single space, so the published text stays exactly the same.
SENTENCES = [
    "The spare room has a door I have never opened.",
    "It was shut when I moved in, and no key came with it.",
    "Each evening, as the light turns blue, a voice behind it hums "
    "the first three notes of a song \u2014 and stops.",
    "I only stand there, wondering if the fourth note is mine to sing.",
]

MIN_CHARS = 1
MAX_CHARS = 280


def build_entry() -> str:
    """Assemble the entry text from its sentences."""
    return " ".join(SENTENCES)


def validate(text: str) -> list[str]:
    """Return every way the text would fail the competition's gate.

    An empty list means the entry is valid: 1-280 Unicode code points,
    not only whitespace, and encodable as UTF-8.
    """
    problems: list[str] = []
    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        problems.append(
            f"entry is {len(text)} characters, gate needs {MIN_CHARS}-{MAX_CHARS}"
        )
    if not text.strip():
        problems.append("entry is only whitespace")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        problems.append(f"entry is not valid UTF-8: {exc}")
    return problems


def check(text: str) -> None:
    """Raise a single error naming every gate problem found."""
    problems = validate(text)
    if problems:
        raise ValueError("; ".join(problems))


def run(output_path: str) -> str:
    """Validate the entry, write it to output_path, and return it."""
    text = build_entry()
    check(text)
    target = Path(output_path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise OSError(f"cannot write entry to {output_path}: {exc}") from exc
    return text


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write the curiosity entry to a text file.",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="/output/entry.txt",
        help="where to write the entry (default: /output/entry.txt)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="only validate the entry against the gate, write nothing",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    # argv includes the program name at [0]; argparse wants only the flags.
    args = parse_args(argv[1:])
    text = build_entry()
    problems = validate(text)
    if args.check:
        if problems:
            print("Entry INVALID:")
            for problem in problems:
                print(f"  - {problem}")
            return 1
        print(f"Entry valid: {len(text)} characters, UTF-8, non-whitespace")
        return 0
    if problems:
        print("Entry INVALID, not written:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    try:
        written = run(args.output)
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote entry ({len(written)} characters) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
