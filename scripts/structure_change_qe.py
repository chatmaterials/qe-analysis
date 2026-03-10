#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_structure(text: str) -> dict[str, object]:
    lines = text.splitlines()
    nat = 0
    lattice: list[list[float]] = []
    coords: list[list[float]] = []
    for line in lines:
        if "nat =" in line:
            try:
                nat = int(line.split("nat =", 1)[1].split(",")[0].strip())
            except ValueError:
                nat = 0
    for i, line in enumerate(lines):
        if line.strip().upper().startswith("CELL_PARAMETERS"):
            lattice = [[float(x) for x in lines[i + j + 1].split()[:3]] for j in range(3)]
        if line.strip().upper().startswith("ATOMIC_POSITIONS"):
            coords = [[float(x) for x in lines[i + j + 1].split()[1:4]] for j in range(nat)]
            break
    return {"natoms": nat, "lattice": lattice, "coords": coords}


def vector_length(vec: list[float]) -> float:
    return sum(value * value for value in vec) ** 0.5


def analyze(initial: Path, final: Path) -> dict[str, object]:
    a = parse_structure(initial.read_text())
    b = parse_structure(final.read_text())
    lengths_a = [vector_length(vec) for vec in a["lattice"]]
    lengths_b = [vector_length(vec) for vec in b["lattice"]]
    delta = [after - before for before, after in zip(lengths_a, lengths_b)]
    max_coord_shift = max(
        (
            sum((after[i] - before[i]) ** 2 for i in range(3)) ** 0.5
            for before, after in zip(a["coords"], b["coords"])
        ),
        default=0.0,
    )
    return {
        "initial": str(initial),
        "final": str(final),
        "natoms": a["natoms"],
        "lattice_lengths_initial": lengths_a,
        "lattice_lengths_final": lengths_b,
        "lattice_length_delta": delta,
        "max_coordinate_shift": max_coord_shift,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two QE input structures.")
    parser.add_argument("initial")
    parser.add_argument("final")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.initial).expanduser().resolve(), Path(args.final).expanduser().resolve())
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
