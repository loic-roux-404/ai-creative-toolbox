import os
import tempfile
from shutil import rmtree

from dotenv import load_dotenv

from .file_to_gpt import FileToGpt


def test_file_to_gpt():
    load_dotenv()
    # Create a temporary directory to store files.
    temp_dir = tempfile.mkdtemp()

    # Create a test file.
    test_file = os.path.join(temp_dir, "test.md")
    with open(test_file, "w") as f:
        f.write("In which show Bart is one of the main characters ?")

    # Create a config object.
    config = {
        "files": [temp_dir],
        "save_dir": temp_dir,
        "title_template": "rendered",
        "messages": [
            {
                "role": "user",
                "content": test_file,
            }
        ],
    }

    # Create a FileToGpt object.
    file_to_gpt = FileToGpt(config)

    # Start the automation.
    file_to_gpt.start()

    print(os.listdir(temp_dir))

    # Check that the output file was created.
    output_file = os.path.join(temp_dir, "rendered.md")
    assert os.path.exists(output_file)

    # Check the contents of the output file.
    with open(output_file) as f:
        content = f.read()

    assert "The Simpsons." in content

    assert (
        """

---

"""
        == content[-7 : len(content)]
    )

    # Clean up.
    rmtree(temp_dir)
