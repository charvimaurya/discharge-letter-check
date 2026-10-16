"""Flag missing or uncertain items in instructions extracted from hospital discharge letters.

Synthetic data only. Not a medical device.
"""

from discharge_letter_check.document_validation import (
    WRONG_DOCUMENT_MESSAGE,
    WrongDocumentError,
    validate_discharge_document,
)
from discharge_letter_check.models import (
    Allergy,
    Appointment,
    DietAdvice,
    FollowOn,
    Medication,
    Monitoring,
    RecoveryState,
    Restriction,
    Source,
    Task,
    WarningSign,
)
from discharge_letter_check.schema import SCHEMA_FILENAME, load_schema, schema_text
from discharge_letter_check.validator import (
    contains_uncertainty,
    validate_allergies,
    validate_appointments,
    validate_diet_advice,
    validate_follow_ons,
    validate_medications,
    validate_monitoring,
    validate_recovery_plan,
    validate_restrictions,
    validate_tasks,
    validate_warning_signs,
)

__version__ = "0.2.0"

# Version of the bundled extraction schema.
SCHEMA_VERSION = "0.2.0"

__all__ = [
    "Allergy",
    "Appointment",
    "DietAdvice",
    "FollowOn",
    "Medication",
    "Monitoring",
    "RecoveryState",
    "Restriction",
    "SCHEMA_FILENAME",
    "SCHEMA_VERSION",
    "Source",
    "Task",
    "WRONG_DOCUMENT_MESSAGE",
    "WarningSign",
    "WrongDocumentError",
    "__version__",
    "contains_uncertainty",
    "load_schema",
    "schema_text",
    "validate_allergies",
    "validate_appointments",
    "validate_diet_advice",
    "validate_discharge_document",
    "validate_follow_ons",
    "validate_medications",
    "validate_monitoring",
    "validate_recovery_plan",
    "validate_restrictions",
    "validate_tasks",
    "validate_warning_signs",
]
