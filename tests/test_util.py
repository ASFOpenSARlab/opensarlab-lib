from pathlib import Path
import pytest

import opensarlab_lib.util as util

def test_path_exists():
    assert util.path_exists('../opensarlab_lib')
    assert not util.path_exists('not/a/real/path')

def test_input_path(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "Some input")
    i = util.input_path("What is your name?")
    assert i == "Some input"

def test_new_directory():
    my_dir = 'DUMMY_DIR'
    util.new_directory(my_dir)
    my_dir = Path(my_dir)
    assert my_dir.is_dir()
    my_dir.unlink()



