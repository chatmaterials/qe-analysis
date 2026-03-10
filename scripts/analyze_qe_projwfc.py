#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


CHANNELS = ["s", "p", "d"]


def analyze_path(path: Path) -> dict[str, object]:
    proj = path / "projwfc.dat" if path.is_dir() else path
    rows = []
    for line in proj.read_text().splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        energy = float(parts[0])
        values = {channel: float(parts[index + 1]) for index, channel in enumerate(CHANNELS)}
        rows.append((energy, values))
    if not rows:
        raise SystemExit("No projwfc rows found")
    nearest = min(rows, key=lambda item: abs(item[0]))
    dominant_channel = max(nearest[1].items(), key=lambda item: item[1])[0]
    peak_channel = None
    peak_value = None
    peak_energy = None
    for channel in CHANNELS:
        best = max(rows, key=lambda item: item[1][channel])
        if peak_value is None or best[1][channel] > peak_value:
            peak_channel = channel
            peak_value = best[1][channel]
            peak_energy = best[0]
    return {
        "path": str(path),
        "dominant_channel_at_fermi": dominant_channel,
        "channel_values_at_fermi": nearest[1],
        "peak_channel": peak_channel,
        "peak_value": peak_value,
        "peak_energy_eV": peak_energy,
        "observations": ["Projected orbital weights were summarized from the sampled projwfc data."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a simple QE projwfc-like data file or result directory.")
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
