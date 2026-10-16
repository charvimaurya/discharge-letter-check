"""allergies: an optional schema list of word-for-word sentences, flagged when missing or unclear."""

import jsonschema
import pytest

from discharge_letter_check import Allergy, RecoveryState, Source, load_schema, validate_recovery_plan


ALLERGY = "Allergic to Examplicillin (synthetic)."


def _check(extracted):
    jsonschema.validate(instance=extracted, schema=load_schema())


def _allergy(text=ALLERGY, **extra):
    return {"text": text, "source": {"snippet": f"ALLERGIES: {ALLERGY}", "page": 1}, **extra}


def test_a_letter_with_one_allergy_passes():
    _check({"discharge_date": "2026-10-16", "allergies": [_allergy()]})


def test_an_allergy_with_empty_text_fails():
    with pytest.raises(jsonschema.ValidationError) as error:
        _check({"allergies": [_allergy(text="")]})

    assert error.value.validator == "minLength"
    assert list(error.value.path) == ["allergies", 0, "text"]


def test_data_with_no_allergies_section_still_passes():
    _check({"discharge_date": "2026-10-16", "medications": [], "diet_advice": []})

    assert RecoveryState("patient", "document").allergies == []


def test_an_allergy_with_an_extra_field_fails():
    with pytest.raises(jsonschema.ValidationError) as error:
        _check({"allergies": [_allergy(severity="severe")]})

    assert error.value.validator == "additionalProperties"


def test_an_unclear_allergy_is_flagged_and_kept_as_written():
    unclear = Allergy("allergy_1", "Allergic to [?Examplicillin?]")
    clear = Allergy("allergy_2", ALLERGY, source=Source("d", ALLERGY, page=1))
    validate_recovery_plan(RecoveryState("patient", "document", allergies=[unclear, clear]))

    assert unclear.needs_confirmation is True
    assert unclear.text == "Allergic to [?Examplicillin?]"
    assert clear.needs_confirmation is False


@pytest.mark.parametrize("missing", ["", None])
def test_an_allergy_with_no_text_is_flagged(missing):
    allergy = Allergy("allergy_1", missing)
    validate_recovery_plan(RecoveryState("patient", "document", allergies=[allergy]))

    assert allergy.needs_confirmation is True
    assert allergy.text == missing
