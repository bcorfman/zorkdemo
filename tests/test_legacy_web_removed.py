from pathlib import Path

import tomllib


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_legacy_dependency_is_removed():
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject["project"]["dependencies"]
    removed_dependency_prefix = "hu" + "g"

    assert all(not dependency.startswith(removed_dependency_prefix) for dependency in dependencies)


def test_pytest_testpaths_no_longer_include_web_tests():
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    testpaths = pyproject["tool"]["pytest"]["ini_options"]["testpaths"]

    assert testpaths == ["tests", "backend/tests"]


def test_setuptools_packages_do_not_include_web():
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    include = pyproject["tool"]["setuptools"]["packages"]["find"]["include"]

    assert include == ["adventure*", "backend*"]


def test_legacy_web_directory_is_removed():
    assert not (PROJECT_ROOT / "web").exists()
