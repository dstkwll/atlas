# brokencli

A tiny CLI that left-pads a label. **It is currently broken.**

## Install (offline, clean environment)

    pip install --no-index --no-build-isolation .

## Run (the documented command)

    brokencli hello 8
    # or, without console-script resolution:
    python -m brokencli.cli hello 8

Expected: the label `hello` right-justified in a field of width 8 (`   hello`).

## Test

    python -m unittest discover -p 'test_*.py'

Both the run command and the test currently fail with
`ModuleNotFoundError: No module named 'tinyfmt'`.
