"""Unrelated documents are rejected before any instruction is checked."""

import pytest

from discharge_letter_check import (
    WRONG_DOCUMENT_MESSAGE, WrongDocumentError, validate_discharge_document,
)


@pytest.mark.parametrize('text', [
    '', 'Invoice from hospital. Total due £240.',
    'CV: I worked at a hospital and administered medications.',
    'Appointment letter. Attend the orthopaedic clinic on Monday.',
    'My essay about the discharge of electrical energy.',
    'DISCHARGE LETTER',
])
def test_wrong_document_rejected(text):
    with pytest.raises(WrongDocumentError, match='Wrong document'):
        validate_discharge_document(text)


def test_none_is_rejected_like_an_empty_document():
    with pytest.raises(WrongDocumentError):
        validate_discharge_document(None)


@pytest.mark.parametrize('text', [
    'Hospital discharge letter. MEDICINES: Take paracetamol as directed.',
    'Discharge summary. Diagnosis: knee replacement. Follow-up in six weeks.',
    'You were discharged home today. Keep your wound dressing clean.',
    'DATE OF DISCHARGE: 16 October. Recovery exercises three times daily.',
])
def test_discharge_documents_accepted(text):
    assert validate_discharge_document(text) is None


def test_error_is_a_value_error_carrying_the_message():
    error = WrongDocumentError()
    assert isinstance(error, ValueError)
    assert str(error) == WRONG_DOCUMENT_MESSAGE
