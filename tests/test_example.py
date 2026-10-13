"""The shipped example runs against the installed package and matches its recorded result."""

import json
import subprocess
import sys
from pathlib import Path


EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_example_runs_and_matches_sample_result():
    result = subprocess.run(
        [sys.executable, str(EXAMPLES / "check_sample.py")],
        capture_output=True, text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Result matches sample_result.json" in result.stdout


def test_sample_result_flags_only_the_ambiguous_instruction():
    sample = json.loads((EXAMPLES / "sample_result.json").read_text(encoding="utf-8"))

    assert sample["needs_confirmation"] == [{"category": "medications", "id": "med_2"}]
    assert sample["dropped_diet_advice"] == ["Eat five portions of fruit a day."]
    flagged = sample["recovery_state"]["medications"][1]
    assert flagged["dose"] == "[?1 or 2 tablets?]"
    assert sample["recovery_state"]["tasks"][1]["follow_on"]["duration_minutes"] == 20


def test_example_files_are_marked_synthetic():
    letter = (EXAMPLES / "synthetic_discharge_letter.txt").read_text(encoding="utf-8")
    sample = json.loads((EXAMPLES / "sample_result.json").read_text(encoding="utf-8"))

    assert "SYNTHETIC" in letter.splitlines()[0]
    assert sample["notice"] == "Synthetic data only. Not a medical device."
