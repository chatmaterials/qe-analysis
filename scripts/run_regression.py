#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=True)


def run_json(*args: str):
    return json.loads(run(*args).stdout)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    single = run_json("scripts/analyze_qe_result.py", "fixtures/completed", "--json")
    ensure(single["completed"] is True, "completed fixture should be complete")
    ensure(abs(single["final_energy_Ry"] + 15.4321) < 1e-6, "single-run energy should parse")

    compare = run_json("scripts/compare_qe_results.py", "fixtures/compare/alpha", "fixtures/compare/beta", "--json")
    ensure(compare["results"][0]["path"].endswith("alpha"), "alpha should be lower in energy than beta")
    ensure(compare["results"][1]["relative_energy_mRy"] > 0, "beta should have positive relative energy")
    structure = run_json("scripts/structure_change_qe.py", "fixtures/compare/alpha/relax.in", "fixtures/compare/beta/relax.in", "--json")
    ensure(structure["natoms"] == 2, "structure comparison should keep the atom count")
    ensure(all(delta == 0 for delta in structure["lattice_length_delta"]), "current QE fixtures should have identical lattices")
    dos = run_json("scripts/analyze_qe_dos.py", "fixtures/completed", "--json")
    ensure(abs(dos["dos_at_fermi"] - 0.1) < 1e-6, "DOS analysis should parse DOS at the Fermi level")
    band = run_json("scripts/analyze_qe_band.py", "fixtures/completed", "--json")
    ensure(abs(band["band_gap_eV"] - 0.9) < 1e-6, "band analysis should parse the band gap")
    ensure(band["is_direct_gap"] is False, "fixture should produce an indirect band gap")
    proj = run_json("scripts/analyze_qe_projwfc.py", "fixtures/completed", "--json")
    ensure(proj["dominant_channel_at_fermi"] == "p", "projwfc analysis should identify the dominant channel near the Fermi level")
    ensure(proj["peak_channel"] == "d", "projwfc analysis should identify the strongest projected channel")
    temp_dir = Path(tempfile.mkdtemp(prefix="qe-analysis-report-"))
    try:
        report_path = Path(run("scripts/export_analysis_report.py", "fixtures/completed", "--output", str(temp_dir / "ANALYSIS_REPORT.md")).stdout.strip())
        report_text = report_path.read_text()
        ensure("# Analysis Report" in report_text, "analysis report should have an analysis-report heading")
        ensure("Final energy" in report_text, "analysis report should include the final energy")
        ensure("## DOS" in report_text and "## Band" in report_text and "## Projected Orbitals" in report_text, "analysis report should include DOS, band, and projected-orbital sections when files are present")
    finally:
        shutil.rmtree(temp_dir)

    print("qe-analysis regression passed")


if __name__ == "__main__":
    main()
