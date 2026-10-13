"""The extraction JSON schema ships inside the installed package and is loaded from there."""

import json
import subprocess
import sys
from importlib import resources
from importlib.metadata import files

import pytest

from discharge_letter_check import SCHEMA_FILENAME, load_schema, schema_text


CATEGORIES = [
    "medications", "tasks", "appointments", "restrictions",
    "monitoring", "warning_signs", "diet_advice",
]


def test_schema_is_a_package_resource():
    resource = resources.files("discharge_letter_check").joinpath("schemas", SCHEMA_FILENAME)

    assert resource.is_file()
    assert json.loads(resource.read_text(encoding="utf-8")) == load_schema()


def test_schema_loads_from_the_installed_package_outside_the_repository(tmp_path):
    # -I ignores the current directory and PYTHONPATH, so only the installation is used.
    code = (
        "import discharge_letter_check as package\n"
        "schema = package.load_schema()\n"
        "print(schema['title'], len(schema['properties']))\n"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", code],
        cwd=tmp_path, capture_output=True, text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["ExtractedDischarge", "8"]


def test_installed_distribution_can_find_the_schema():
    recorded = [str(path) for path in files("discharge-letter-check") or []]

    # A wheel install records the schema; an editable install records a finder for src/.
    assert any(path.endswith(SCHEMA_FILENAME) for path in recorded) or any(
        "__editable__" in path for path in recorded
    )


def test_load_schema_returns_a_fresh_copy():
    first = load_schema()
    first["properties"].clear()

    assert load_schema()["properties"]
    assert json.loads(schema_text()) == load_schema()


def test_schema_top_level_shape():
    schema = load_schema()

    assert schema["title"] == "ExtractedDischarge"
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == {"discharge_date", *CATEGORIES}


@pytest.mark.parametrize("category", CATEGORIES)
def test_schema_requires_source_on_every_item(category):
    schema = load_schema()["properties"][category]["items"]
    assert "source" in schema["required"]
    source = schema["properties"]["source"]
    assert "snippet" in source["required"]
    assert source["properties"]["snippet"]["type"] == "string"
    # Canonical schema permits an unknown page; known pages are retained above.
    assert {"type": "integer"} in source["properties"]["page"]["anyOf"]
    assert {"type": "null"} in source["properties"]["page"]["anyOf"]


def test_schema_has_diet_advice_with_avoid_and_advice():
    diet = load_schema()["properties"]["diet_advice"]["items"]

    assert diet["properties"]["kind"]["enum"] == ["avoid", "advice"]
    assert set(diet["required"]) == {"text", "kind", "source"}


def test_schema_allows_unstated_details_to_be_null():
    medication = load_schema()["properties"]["medications"]["items"]

    assert medication["required"] == ["name", "source"]
    for optional in ["strength", "dose", "duration_text"]:
        assert {"type": "null"} in medication["properties"][optional]["anyOf"]
