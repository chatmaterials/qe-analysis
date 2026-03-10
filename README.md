# qe-analysis

Standalone skill for post-run Quantum ESPRESSO result analysis and multi-run comparison.

## Install

```bash
npx skills add chatmaterials/qe-analysis -g -y
```

## Local Validation

```bash
python3 -m py_compile scripts/*.py
npx skills add . --list
python3 scripts/analyze_qe_result.py fixtures/completed --json
python3 scripts/compare_qe_results.py fixtures/compare/alpha fixtures/compare/beta --json
python3 scripts/structure_change_qe.py fixtures/compare/alpha/relax.in fixtures/compare/beta/relax.in --json
python3 scripts/analyze_qe_dos.py fixtures/completed --json
python3 scripts/analyze_qe_band.py fixtures/completed --json
python3 scripts/analyze_qe_projwfc.py fixtures/completed --json
python3 scripts/export_analysis_report.py fixtures/completed
python3 scripts/run_regression.py
```
