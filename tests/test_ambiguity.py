"""Ambiguous or missing information is flagged for confirmation, never guessed or rewritten."""

from dataclasses import asdict

import pytest

from discharge_letter_check import (
    Appointment, DietAdvice, Medication, Monitoring, RecoveryState, Restriction, Task,
    WarningSign, contains_uncertainty, validate_recovery_plan,
)


@pytest.mark.parametrize("value,expected", [
    ("[?2?] tablets", True),
    ("Take [?", True),
    ("[unreadable]", True),
    ("[UNREADABLE] times a day", True),
    ("[Unreadable]", True),
    ("2 tablets", False),
    ("Is this right?", False),
    ("unreadable", False),
    ("", False),
    (None, False),
])
def test_contains_uncertainty(value, expected):
    assert contains_uncertainty(value) is expected


REQUIRED = [
    ("medications", Medication("med", "Example"), "name"),
    ("tasks", Task("task", "Example"), "description"),
    ("appointments", Appointment("appt", "Example"), "title"),
    ("restrictions", Restriction("restriction", "Example"), "text"),
    ("monitoring", Monitoring("monitor", "Example"), "what"),
    ("warning_signs", WarningSign("warning", "Example", "Stated action"), "text"),
    ("warning_signs", WarningSign("warning", "Example", "Stated action"), "action"),
]


@pytest.mark.parametrize("category,item,field", REQUIRED)
@pytest.mark.parametrize("missing", ["", None])
def test_missing_required_text_is_flagged_and_left_missing(category, item, field, missing):
    item = type(item)(**asdict(item))
    setattr(item, field, missing)
    validate_recovery_plan(RecoveryState("patient", "document", **{category: [item]}))

    assert item.needs_confirmation is True
    assert getattr(item, field) == missing


@pytest.mark.parametrize("category,item", [
    ("medications", Medication("med", "Example")),
    ("tasks", Task("task", "Example")),
    ("appointments", Appointment("appt", "Example")),
    ("restrictions", Restriction("restriction", "Example")),
    ("monitoring", Monitoring("monitor", "Example")),
    ("warning_signs", WarningSign("warning", "Example", "Stated action")),
])
def test_absent_optional_details_are_not_flagged_or_filled_in(category, item):
    before = asdict(item)
    validate_recovery_plan(RecoveryState("patient", "document", **{category: [item]}))

    assert item.needs_confirmation is False
    assert asdict(item) == before


def test_missing_dose_is_preserved_without_inventing_it():
    medication = Medication("med", "Amoxicillin", times_per_day=3, duration_text="7 days")
    validate_recovery_plan(RecoveryState("patient", "document", medications=[medication]))

    assert medication.dose is None
    assert medication.needs_confirmation is False


def test_only_the_ambiguous_item_is_flagged():
    clear = Medication("med_1", "Examplamol", dose="2 tablets")
    ambiguous = Medication("med_2", "Samplexin", dose="[?1 or 2 tablets?]")
    task = Task("task_1", "Call [?111?] if symptoms worsen")
    state = RecoveryState("patient", "document", medications=[clear, ambiguous], tasks=[task])
    validate_recovery_plan(state)

    assert clear.needs_confirmation is False
    assert ambiguous.needs_confirmation is True
    assert ambiguous.dose == "[?1 or 2 tablets?]"
    assert task.needs_confirmation is True


def test_two_dates_for_one_appointment_are_both_kept_for_review():
    appointment = Appointment("appt", "Wound check", date="2026-10-21", conflicting_dates=["2026-10-23"])
    validate_recovery_plan(RecoveryState("patient", "document", appointments=[appointment]))

    assert appointment.needs_confirmation is True
    assert (appointment.date, appointment.conflicting_dates) == ("2026-10-21", ["2026-10-23"])


def test_uncertain_diet_line_is_flagged():
    advice = DietAdvice("diet", "Drink [unreadable] glasses of water a day.")
    validate_recovery_plan(RecoveryState("patient", "document", diet_advice=[advice]))

    assert advice.needs_confirmation is True


def test_ready_status_does_not_mean_nothing_was_flagged():
    medication = Medication("med", "[unreadable]")
    state = validate_recovery_plan(RecoveryState("patient", "document", medications=[medication]))

    assert state.ingestion_status == "ready"
    assert medication.needs_confirmation is True
