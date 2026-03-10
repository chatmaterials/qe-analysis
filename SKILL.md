---
name: "qe-analysis"
description: "Use when the task is to analyze completed or partially completed Quantum ESPRESSO results, including extracting total energies, convergence status, force summaries, comparing multiple QE runs, and summarizing pw.x output directories."
---

# QE Analysis

Use this skill for post-run Quantum ESPRESSO result analysis rather than workflow setup.

## When to use

- analyze a completed or incomplete QE run
- compare energies across multiple QE directories
- summarize SCF or ionic convergence from `pw.x` output
- write a compact report from existing QE results

## Use the bundled helpers

- `scripts/analyze_qe_result.py`
  Summarize a single QE result directory.
- `scripts/compare_qe_results.py`
  Compare multiple QE result directories by energy and status.
- `scripts/structure_change_qe.py`
  Compare two QE structures and summarize lattice or coordinate changes.
- `scripts/analyze_qe_dos.py`
  Extract DOS-oriented summary data from QE DOS output.
- `scripts/analyze_qe_band.py`
  Extract band-gap-oriented summary data from QE band output.
- `scripts/analyze_qe_projwfc.py`
  Extract projected-orbital summary data from QE projwfc-like output.
- `scripts/export_analysis_report.py`
  Export a markdown analysis report from a QE result directory.

## Guardrails

- Do not treat incomplete scratch-dependent child runs as finalized results.
- Distinguish raw extraction from interpretation.
- If runs are not comparable, say so explicitly.
