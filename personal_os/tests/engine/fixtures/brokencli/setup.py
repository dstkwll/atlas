from setuptools import setup, find_packages

# Legacy setup.py (no pyproject/PEP517) on purpose: this toolchain (py3.9 +
# setuptools 58, no `wheel`) installs a legacy source tree OFFLINE via
# `pip install --no-index --no-build-isolation .` without needing to build a
# wheel. The engine's HARD validator relies on exactly this offline path.
setup(
    name="brokencli",
    version="0.1.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["brokencli=brokencli.cli:main"]},
)
