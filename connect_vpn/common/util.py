import os


def create_file_anew(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)


def ensure_file_exists(file_path, default_content="", create_anew=create_file_anew):
    created_anew = False
    if not os.path.exists(file_path):
        create_anew(file_path, default_content)
        created_anew = True
    return created_anew


def ensure_directory_exists(path: str):
    created_anew = False
    if not os.path.exists(path):
        created_anew = True
        os.makedirs(path)
    return created_anew
