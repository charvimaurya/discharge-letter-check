#!/usr/bin/env python3
"""Check instructions extracted from the synthetic example letter and print what needs confirming.

Synthetic data only. Not a medical device.

Run:    python examples/check_sample.py
Update: python examples/check_sample.py --write   (rewrites sample_result.json)
"""

import json
import sys
from dataclasses import asdict
from pathlib import Path

from discharge_letter_check import (
    Appointment,
    DietAdvice,
    FollowOn,
    Medication,
    RecoveryState,
    Source,
    Task,
    WarningSign,
    WrongDocumentError,
    validate_discharge_document,
    validate_recovery_plan,
)


EXAMPLES = Path(__file__).resolve().parent
LETTER_PATH = EXAMPLES / "synthetic_discharge_letter.txt"
RESULT_PATH = EXAMPLES / "sample_result.json"

DOCUMENT_ID = "synthetic-letter-001"
CATEGORIES = [
    "medications", "tasks", "appointments", "restrictions",
    "monitoring", "warning_signs", "diet_advice",
]


def _source(snippet: str) -> Source:
    return Source(DOCUMENT_ID, snippet, page=1)


def build_extracted_state() -> RecoveryState:
    """What an extraction step might return for the letter. This package does not extract.

    The extraction step marks wording it could not read with certainty as [?...?].
    One diet line here is not in the letter at all, to show that it gets dropped.
    """

    clear_dose = "Examplamol 500 mg tablets: take 2 tablets 4 times a day for 14 days."
    unclear_dose = (
        "Samplexin 30 mg tablets: take 1 or 2 tablets (handwritten amendment, unclear) "
        "only if needed for pain."
    )
    exercises = "Do your knee exercises 3 times a day."
    ice = "Ice pack on the knee for 20 minutes after each set of exercises."
    water = "Drink 6 to 8 glasses of water or other fluids a day."
    invented = "Eat five portions of fruit a day."
    wound_check = "Wound check with the practice nurse on 23 October 2026."
    warning = "If your wound becomes red, hot or swollen, contact your care team."

    return RecoveryState(
        patient_id="synthetic-patient-001",
        document_id=DOCUMENT_ID,
        discharge_date="2026-10-16",
        medications=[
            Medication(
                "med_1", "Examplamol", strength="500 mg", form="tablets", dose="2 tablets",
                times_per_day=4, duration_text="for 14 days", source=_source(clear_dose),
            ),
            Medication(
                "med_2", "Samplexin", strength="30 mg", form="tablets",
                dose="[?1 or 2 tablets?]", as_needed=True, as_needed_reason="for pain",
                source=_source(unclear_dose),
            ),
        ],
        tasks=[
            Task("task_1", exercises, kind="exercise", times_per_day=3, source=_source(exercises)),
            Task(
                "task_2", ice, kind="care", source=_source(ice),
                follow_on=FollowOn("task_1", duration_minutes=20, source=_source(ice)),
            ),
        ],
        appointments=[
            Appointment(
                "appt_1", "Wound check with the practice nurse", date="2026-10-23",
                source=_source(wound_check),
            ),
        ],
        warning_signs=[
            WarningSign(
                "warning_1", "If your wound becomes red, hot or swollen",
                "contact your care team", source=_source(warning),
            ),
        ],
        diet_advice=[
            DietAdvice("diet_1", water, source=_source(water)),
            DietAdvice("diet_2", invented, source=_source(invented)),
        ],
    )


def check_sample() -> dict:
    letter = LETTER_PATH.read_text(encoding="utf-8")

    try:
        validate_discharge_document(letter)
    except WrongDocumentError as error:
        return {"document_accepted": False, "error": str(error)}

    state = build_extracted_state()
    diet_before = [advice.text for advice in state.diet_advice]

    validate_recovery_plan(state, document_text=letter)

    diet_after = [advice.text for advice in state.diet_advice]

    return {
        "notice": "Synthetic data only. Not a medical device.",
        "document_accepted": True,
        "ingestion_status": state.ingestion_status,
        "needs_confirmation": [
            {"category": category, "id": item.id}
            for category in CATEGORIES
            for item in getattr(state, category)
            if item.needs_confirmation
        ],
        "dropped_diet_advice": [text for text in diet_before if text not in diet_after],
        "recovery_state": asdict(state),
    }


def main() -> int:
    result = check_sample()

    if "--write" in sys.argv[1:]:
        RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {RESULT_PATH.name}")
        return 0

    print(result["notice"])
    print(f"Letter accepted as a discharge document: {result['document_accepted']}")
    print(f"Status after checking: {result['ingestion_status']}")

    print("Needs confirmation by a person:")
    for flagged in result["needs_confirmation"]:
        item = next(
            item for item in result["recovery_state"][flagged["category"]]
            if item["id"] == flagged["id"]
        )
        print(f"  - {flagged['category']} {flagged['id']}: {json.dumps(item, sort_keys=True)}")

    print("Dropped because the wording is not in the letter:")
    for text in result["dropped_diet_advice"]:
        print(f"  - {text}")

    expected = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    if result != expected:
        print(f"MISMATCH: the result differs from {RESULT_PATH.name}", file=sys.stderr)
        return 1

    print(f"Result matches {RESULT_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
