# PyPI Package Template

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![GitHub License](https://img.shields.io/github/license/SpaceShaman/pypi-workflow)
![Tests](https://img.shields.io/github/actions/workflow/status/SpaceShaman/pypi-workflow/release.yml?label=tests)
![Codecov](https://img.shields.io/codecov/c/github/SpaceShaman/pypi-workflow)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pypi-workflow)
[![PyPI - Version](https://img.shields.io/pypi/v/pypi-workflow)](https://pypi.org/project/pypi-workflow)

This repository contains a simple template for creating PyPI packages with automated publishing using GitHub Actions. It includes the following features:

- **Automated Publishing**:
  - New versions are published to Test PyPI when a new tag with a semantic version is pushed.
  - New releases trigger the build and publication of the package to the official PyPI.

- **Continuous Integration/Continuous Deployment (CI/CD)**:
  - Automated testing using `pytest`.
  - Coverage reports generated with `pytest-cov` and uploaded to Codecov.

- **Secrets Configuration**:
  - Requires `PYPI_TOKEN` and `TEST_PYPI_TOKEN` for publishing.
  - Requires `CODECOV_TOKEN` for generating the coverage badge.

This template streamlines the process of developing, testing, and publishing Python packages, ensuring a smooth and automated workflow.
