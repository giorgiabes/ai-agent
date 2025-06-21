import os


def write_file(working_directory, file_path, content):
    try:
        working_abs = os.path.abspath(working_directory)
        target_abs = os.path.abspath(os.path.join(working_directory, file_path))

        # Check if target path is inside working directory
        if not target_abs.startswith(working_abs):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        # Ensure parent directories exist
        parent_dir = os.path.dirname(target_abs)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        # Write content to file (overwrite if exists)
        with open(target_abs, "w", encoding="utf-8") as f:
            f.write(content)

        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )

    except Exception as e:
        return f"Error: {e}"
