import os

MAX_CHARS = 10000


def get_file_content(working_directory, file_path):
    try:
        working_abs = os.path.abspath(working_directory)
        target_abs = os.path.abspath(os.path.join(working_directory, file_path))

        # Check if target path is inside working directory
        if not target_abs.startswith(working_abs):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Check if file exists and is a regular file
        if not os.path.isfile(target_abs):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target_abs, "r", encoding="utf-8") as f:
            content = f.read()

        if len(content) > MAX_CHARS:
            content = content[:MAX_CHARS]
            content += f'\n[...File "{file_path}" truncated at 10000 characters]'

        return content

    except Exception as e:
        return f"Error: {e}"
