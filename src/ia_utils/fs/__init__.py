def write_to_file(file_path, content):
    file = open(file_path, "a")
    file.write(content)
    file.close()


def open_file(file_path):
    file = open(file_path, "r")
    content = file.read()
    file.close()
    return content
