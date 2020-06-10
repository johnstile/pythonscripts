#!/usr/bin/env python
"""
Create a simple test function with just four lines of code
To run1: pytest
To run2: python -m pytest
To run3: pytest -x  # stop after first failure
To run4: pytest --maxfail=2  # stop after two failures
To run5: pytest -ra  # get a summery at the end
To run6: pytest --pdb   # Dropping to PDB (Python Debugger) on failures
To run6: pytest --junitxml=junit.xml  # Create result file read by Jenkins 
"""

import pytest


class TestClass:
    """For test discovery: Name Class prefix: Test"""
    def test_one(self):
        x = "this"
        assert "h" in x

    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")

def func(x):
    return x + 1

@pytest.mark.test_id(1)
def test_answer():
    assert func(3) == 4

"""
https://docs.pytest.org/en/latest/builtin.html
Builtin fixtures/function arguments
to request arbitrary resources
https://docs.pytest.org/en/stable/tmpdir.html#tmpdir-handling
pytest --fixtures
"""
@pytest.mark.test_id(2)
def test_needsfiles(tmpdir):
    print(tmpdir)
    assert 0

def f():
    raise SystemExit(1)

@pytest.mark.test_id(3)
def test_mytest():
    with pytest.raises(SystemExit):
        f()

@pytest.mark.test_id(4)
@pytest.fixture
def error_fixture():
    assert 0

@pytest.mark.test_id(5)
def test_ok():
    print("ok")

@pytest.mark.test_id(6)
def test_fail():
    assert 0

@pytest.mark.test_id(7)
def test_error(error_fixture):
    pass

@pytest.mark.test_id(8)
def test_skip():
    pytest.skip("skipping this test")

@pytest.mark.test_id(9)
def test_xfail():
    pytest.xfail("xfailing this test")

@pytest.mark.test_id(10)
@pytest.mark.xfail(reason="always xfail")
def test_xpass():
    pass
