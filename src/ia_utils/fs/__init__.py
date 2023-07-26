import tempfile

import requests


def write_to_file(file_path, content):
    file = open(file_path, "a")
    file.write(content)
    file.close()


def open_file(file_path):
    file = open(file_path, "r")
    content = file.read()
    file.close()
    return content


# TODO refecto to an io utils lib
def url_to_image(url) -> tempfile._TemporaryFileWrapper | None:
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
