#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from analyze_qe_result import analyze_path
from analyze_qe_band import analyze_path as analyze_band
from analyze_qe_dos import analyze_path as analyze_dos
from analyze_qe_projwfc import analyze_path as analyze_projwfc


def render_markdown(record: dict[str, object]) -> str:
    lines = [
        "# Analysis Report",
        "",
        f"Source: `{record['path']}`",
        "",
        f"- Completed: `{str(record['completed']).lower()}`",
        f"- SCF converged: `{str(record['scf_converged']).lower()}`",
        f"- Ionic converged: `{str(record['ionic_converged']).lower()}`",
    ]
    if record.get("final_energy_Ry") is not None:
        lines.append(f"- Final energy (Ry): `{record['final_energy_Ry']:.8f}`")
    if record.get("energy_per_atom_Ry") is not None:
        lines.append(f"- Energy per atom (Ry): `{record['energy_per_atom_Ry']:.8f}`")
    lines.extend(["", "## Observations"])
    lines.extend(f"- {item}" for item in record["observations"])
    source = Path(str(record["path"]))
    if (source / "dos.dat").exists():
        dos = analyze_dos(source)
        lines.extend(
            [
                "",
                "## DOS",
                f"- DOS at Fermi: `{dos['dos_at_fermi']:.4f}`",
                f"- Peak DOS: `{dos['peak_dos']:.4f}` at `{dos['peak_energy_eV']:.4f}` eV",
            ]
        )
    if (source / "bands.dat").exists():
        band = analyze_band(source)
        lines.extend(
            [
                "",
                "## Band",
                f"- Band gap (eV): `{band['band_gap_eV']:.4f}`",
                f"- Direct gap: `{str(band['is_direct_gap']).lower()}`",
                f"- VBM (eV): `{band['vbm_eV']:.4f}`",
                f"- CBM (eV): `{band['cbm_eV']:.4f}`",
            ]
        )
    if (source / "projwfc.dat").exists():
        proj = analyze_projwfc(source)
        lines.extend(
            [
                "",
                "## Projected Orbitals",
                f"- Dominant channel at Fermi: `{proj['dominant_channel_at_fermi']}`",
                f"- Peak channel: `{proj['peak_channel']}` at `{proj['peak_energy_eV']:.4f}` eV",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def default_output(source: Path) -> Path:
    if source.is_file():
        return source.parent / f"{source.stem}.ANALYSIS_REPORT.md"
    return source / "ANALYSIS_REPORT.md"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a markdown analysis report for a QE result directory.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--output")
    args = parser.parse_args()
    source = Path(args.path).expanduser().resolve()
    record = analyze_path(source)
    output = Path(args.output).expanduser().resolve() if args.output else default_output(source)
    output.write_text(render_markdown(record))
    print(output)


if __name__ == "__main__":
    main()
