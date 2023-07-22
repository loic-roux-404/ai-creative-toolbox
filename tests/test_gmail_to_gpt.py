# import pytest

from ia_utils.main import main

__author__ = "loic-roux-404"
__copyright__ = "loic-roux-404"
__license__ = "MIT"


def test_fib():
    """API Tests"""
    pass
    # assert gmail_to_gpt(1) == 1
    # assert gmail_to_gpt(2) == 1
    # assert gmail_to_gpt(7) == 13
    # with pytest.raises(AssertionError):
    #     gmail_to_gpt(-10)


def test_main(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts against stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["config.json"])
    captured = capsys.readouterr()
    assert captured.out is not None
