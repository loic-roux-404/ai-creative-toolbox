import tempfile
from itertools import chain
from os import listdir, path
from typing import Optional

import requests


def write_to_file(file_path: str, content: str):
    file = open(path.expanduser(file_path), "a")
    file.write(content)
    file.close()


def open_file(file_path: str):
    file = open(path.expanduser(file_path), "r")
    content = file.read()
    file.close()
    return content


def file_exists(file_path: str):
    return path.exists(path.expanduser(file_path))


def files_in_dir(dir_path: str) -> list[str]:
    full_dir_path = path.expanduser(dir_path)
    if not path.isdir(full_dir_path):
        return [full_dir_path]

    return [
        path.expanduser(f"{dir_path}/{relative_file}")
        for relative_file in listdir(path.expanduser(full_dir_path))
    ]


def all_files_in_dirs(files: list[str]):
    return list(chain.from_iterable([files_in_dir(file) for file in files]))


def url_to_file(url: str) -> Optional[tempfile._TemporaryFileWrapper]:
    # Send a HTTP request to the URL of the image, stream = True ensures
    # that the request won't download the image file immediately
    response = requests.get(url, stream=True)

    # Check if the request threw an error
    if response.status_code != 200:
        response.raise_for_status()
        return None

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmpf:
        tmpf.write(response.content)

    return tmpf


def url_to_text(html_url: str):
    response = requests.get(html_url)
    return response.text
