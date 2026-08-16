#!/usr/bin/env python3
"""Check that the rolling architecture monolith matches its canonical sources."""

from pathlib import Path
import sys


SEPARATOR = b"\n---\n\n"


def canonical_documents(architecture_dir):
    return sorted(
        (path for path in architecture_dir.glob("[0-9][0-9]-*.md") if path.is_file()),
        key=lambda path: path.name,
    )


def expected_monolith(documents):
    return SEPARATOR.join(path.read_bytes() for path in documents)


def first_difference(expected, actual):
    for offset, (expected_byte, actual_byte) in enumerate(zip(expected, actual)):
        if expected_byte != actual_byte:
            return offset
    return min(len(expected), len(actual))


def validate_repository(repository_root):
    architecture_dir = Path(repository_root) / "architecture"
    monolith_path = architecture_dir / "rolling-monolith.md"

    try:
        documents = canonical_documents(architecture_dir)
        if not documents:
            return 2, f"error: no canonical architecture documents found in {architecture_dir}"
        if not monolith_path.is_file():
            return 2, f"error: rolling monolith is missing: {monolith_path}"

        expected = expected_monolith(documents)
        actual = monolith_path.read_bytes()
    except OSError as error:
        return 2, f"error: could not validate architecture: {error}"

    if expected == actual:
        return 0, f"architecture monolith is consistent ({len(documents)} documents)"

    offset = first_difference(expected, actual)
    line = expected[:offset].count(b"\n") + 1
    return (
        1,
        "architecture monolith drift detected: "
        f"first difference at byte {offset} (expected line {line}); "
        f"expected {len(expected)} bytes, found {len(actual)} bytes",
    )


def main():
    repository_root = Path(__file__).resolve().parents[1]
    status, message = validate_repository(repository_root)
    print(message, file=sys.stdout if status == 0 else sys.stderr)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
