import tempfile
from os import path

import requests


def write_to_file(file_path, content):
    file = open(path.expanduser(file_path), "a")
    file.write(content)
    file.close()


def open_file(file_path):
    file = open(path.expanduser(file_path), "r")
    content = file.read()
    file.close()
    return content


def url_to_file(url) -> tempfile._TemporaryFileWrapper | None:
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


def url_to_text(html_url):
    response = requests.get(html_url)
    return response.text
