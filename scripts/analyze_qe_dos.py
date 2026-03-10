#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze_path(path: Path) -> dict[str, object]:
    dos_path = path / "dos.dat" if path.is_dir() else path
    rows = []
    for line in dos_path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        energy = float(parts[0])
        dos = float(parts[1])
        intdos = float(parts[2]) if len(parts) > 2 else None
        rows.append((energy, dos, intdos))
    if not rows:
        raise SystemExit("No DOS rows found")
    efermi = 0.0
    nearest = min(rows, key=lambda item: abs(item[0] - efermi))
    peak = max(rows, key=lambda item: item[1])
    observations = []
    if abs(nearest[1]) < 1e-6:
        observations.append("Sampled DOS at the Fermi level is effectively zero.")
    else:
        observations.append("Finite sampled DOS is present at the Fermi level.")
    return {
        "path": str(path),
        "dos_at_fermi": nearest[1],
        "peak_dos": peak[1],
        "peak_energy_eV": peak[0],
        "observations": observations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a QE DOS file or result directory.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze_path(Path(args.path).expanduser().resolve())
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
