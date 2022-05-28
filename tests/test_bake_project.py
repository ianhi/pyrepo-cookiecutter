import datetime
import os
import shlex
import subprocess
from contextlib import contextmanager
import pytest

from cookiecutter.utils import rmtree


@contextmanager
def inside_dir(dirpath):
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def bake_in_temp_dir(cookies, *args, **kwargs):
    """
    Delete the temporal directory that is created when executing the tests
    :param cookies: pytest_cookies.Cookies,
        cookie to be baked and its temporal files will be removed
    """
    result = cookies.bake(*args, **kwargs)
    assert result.exit_code == 0
    assert result.exception is None
    try:
        yield result
    finally:
        rmtree(str(result.project_path))


@pytest.fixture
def basic_build(cookies):
    with bake_in_temp_dir(cookies) as result:
        yield result


def run_inside_dir(command, dirpath):
    """
    Run a command from inside a given directory, returning the exit status
    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.check_call(shlex.split(command))


def check_output_inside_dir(command, dirpath):
    "Run a command from inside a given directory, returning the command output"
    with inside_dir(dirpath):
        return subprocess.check_output(shlex.split(command))


def test_year_compute_in_license_file(basic_build):
    now = datetime.datetime.now()
    assert str(now.year) in (basic_build.project_path / "LICENSE").read_text()


def test_bake_with_defaults(basic_build):
    pth = basic_build.project_path
    assert pth.is_dir()
    assert basic_build.exit_code == 0
    assert basic_build.exception is None

    found_toplevel_files = [f.name for f in pth.glob("*")]
    assert "pyproject.toml" in found_toplevel_files
    assert "src" in found_toplevel_files
    assert (pth / "src" / "pyrepo").exists()
    assert "tox.ini" in found_toplevel_files
    assert "tests" in found_toplevel_files


def test_bake_and_run_tests(basic_build):
    assert basic_build.project_path.is_dir()
    assert run_inside_dir("pytest", str(basic_build.project_path)) == 0


def test_bake_with_apostrophe_and_run_tests(cookies):
    """Ensure that a `full_name` with apostrophes does not break pyproject.toml"""
    with bake_in_temp_dir(cookies, extra_context={"full_name": "O'connor"}) as result:
        assert result.project_path.is_dir()
        assert run_inside_dir("pytest", str(result.project_path)) == 0


def test_bake_and_build(basic_build):
    pth = str(basic_build.project_path)
    run_inside_dir("git init -q", pth)
    run_inside_dir("git add .", pth)
    run_inside_dir('git commit -q --author="Name <>" -m "initial"', pth)
    assert run_inside_dir("python -m build", pth) == 0
    assert len(list((basic_build.project_path / "dist").iterdir())) == 2


def test_bake_and_check_manifest(basic_build):
    run_inside_dir("check-manifest", str(basic_build.project_path))
