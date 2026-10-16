# Contributing

Thank you for helping. This library is small on purpose, so changes should keep it easy to read and test.

## Set up

Python 3.11 or newer. From a clone of the repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
```

## Run the tests

```bash
pytest -q
python examples/check_sample.py
```

Every change needs a test. GitHub runs the tests on Python 3.11, 3.12 and 3.13 for every push and pull request.

## Two rules

1. **All sample data must be synthetic.** Never add a real letter, a real name, a real date of birth or a real NHS number, even with parts removed. Mark new sample letters as synthetic, like the one in `examples/`.
2. **The checker must never call a model or the network.** It only checks data it is given, using the Python standard library. Do not add runtime dependencies or code that sends anything over the network.

## Reporting a problem

Open an issue at https://github.com/charvimaurya/discharge-letter-check/issues. Do not paste real patient information into an issue.
