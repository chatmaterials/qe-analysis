#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(errors="ignore") if path.exists() else ""


def to_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value.replace("D", "e").replace("d", "e"))
    except ValueError:
        return None


def count_atoms_from_input(text: str) -> int | None:
    match = re.search(r"\bnat\s*=\s*(\d+)", text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def find_input(path: Path) -> Path | None:
    for name in ("scf.in", "relax.in", "nscf.in", "bands.in", "pw.in"):
        candidate = path / name
        if candidate.exists():
            return candidate
    candidates = sorted(path.glob("*.in"))
    return candidates[0] if candidates else None


def find_output(path: Path, input_file: Path | None) -> Path | None:
    if input_file:
        candidate = path / f"{input_file.stem}.out"
        if candidate.exists():
            return candidate
    candidates = sorted(path.glob("*.out"))
    return candidates[0] if candidates else None


def analyze_path(path: Path) -> dict[str, object]:
    input_file = find_input(path)
    output_file = find_output(path, input_file)
    input_text = read_text(input_file) if input_file else ""
    output_text = read_text(output_file) if output_file else ""
    energy_match = re.findall(r"!\s+total energy\s+=\s+([\-0-9.DdEe+]+)\s+Ry", output_text)
    final_energy = to_float(energy_match[-1]) if energy_match else None
    natoms = count_atoms_from_input(input_text)
    observations: list[str] = []
    completed = "JOB DONE." in output_text
    scf_converged = "convergence has been achieved" in output_text
    ionic_converged = "End of BFGS Geometry Optimization" in output_text or "bfgs converged" in output_text.lower()
    if completed:
        observations.append("QE run completed.")
    else:
        observations.append("QE run appears incomplete.")
    if "convergence NOT achieved" in output_text:
        observations.append("SCF convergence was not reached.")
    energy_per_atom = final_energy / natoms if final_energy is not None and natoms else None
    return {
        "path": str(path),
        "completed": completed,
        "scf_converged": scf_converged,
        "ionic_converged": ionic_converged,
        "natoms": natoms,
        "final_energy_Ry": final_energy,
        "energy_per_atom_Ry": energy_per_atom,
        "observations": observations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a QE result directory.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    record = analyze_path(Path(args.path).expanduser().resolve())
    if args.json:
        print(json.dumps(record, indent=2))
        return
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
