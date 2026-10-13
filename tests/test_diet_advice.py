"""diet_advice: kept only when found word for word in the letter, and flagged when unclear."""

from discharge_letter_check import DietAdvice, RecoveryState, Source, validate_recovery_plan


LETTER = """DAILY ACTIVITIES
Rest with your leg raised between activities.
DIET
- Eat plenty of fibre, such as fruit, vegetables and wholegrain bread, to help prevent constipation from your
pain medicine.
- Drink 6 to 8 glasses of water or other fluids a day.
- Do not drink alcohol while you are taking codeine.
WOUND CARE
"""

FIBRE = ("Eat plenty of fibre, such as fruit, vegetables and wholegrain bread, "
         "to help prevent constipation from your pain medicine.")
WATER = "Drink 6 to 8 glasses of water or other fluids a day."
ALCOHOL = "Do not drink alcohol while you are taking codeine."


def _state(*items, letter=LETTER):
    state = RecoveryState("p", "d", discharge_date="2026-10-16", diet_advice=[
        DietAdvice(f"diet_{number}", text, kind, source=Source("d", text, page=1))
        for number, (text, kind) in enumerate(items, start=1)
    ])
    return validate_recovery_plan(state, document_text=letter)


def test_three_letter_lines_are_kept_with_their_kind():
    state = _state((FIBRE, "advice"), (WATER, "advice"), (ALCOHOL, "avoid"))

    assert [(a.text, a.kind) for a in state.diet_advice] == [
        (FIBRE, "advice"), (WATER, "advice"), (ALCOHOL, "avoid"),
    ]
    assert not any(a.needs_confirmation for a in state.diet_advice)
    assert state.diet_advice[2].source.snippet == ALCOHOL


def test_a_reworded_or_invented_line_is_dropped():
    state = _state(
        ("Avoid alcohol while on codeine.", "avoid"),   # reworded
        ("Eat five portions of fruit a day.", "advice"),  # not in the letter
        (WATER, "advice"),
    )

    assert [a.text for a in state.diet_advice] == [WATER]


def test_a_line_broken_across_pdf_lines_still_matches():
    assert [a.text for a in _state((FIBRE, "advice")).diet_advice] == [FIBRE]


def test_unclear_wording_needs_confirmation():
    unclear = "Drink [?] glasses of water a day."
    state = _state((unclear, "advice"), letter=f"DIET\n{unclear}\n")

    assert state.diet_advice[0].needs_confirmation is True


def test_without_the_letter_text_nothing_is_dropped():
    invented = "Eat five portions of fruit a day."
    state = _state((invented, "advice"), letter=None)

    assert [a.text for a in state.diet_advice] == [invented]
    assert state.diet_advice[0].needs_confirmation is False


def test_no_diet_section_means_no_diet_advice():
    state = RecoveryState("p", "d", discharge_date="2026-10-16")

    assert validate_recovery_plan(state, document_text="MEDICINES\n").diet_advice == []
