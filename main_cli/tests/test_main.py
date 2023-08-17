from main_cli.__main__ import main

__author__ = "loic-roux-404"
__copyright__ = "loic-roux-404"
__license__ = "MIT"


def test_main(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts against stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["configs/gmail-example.json"])
    captured = capsys.readouterr()
    assert captured.out is not None
