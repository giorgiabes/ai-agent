import os


def get_files_info(working_directory, directory=None):
    try:
        # If directory is None, list working_directory itself
        directory = directory or "."

        # Get absolute paths
        working_abs = os.path.abspath(working_directory)
        target_abs = os.path.abspath(os.path.join(working_directory, directory))

        # Check if target directory is inside working_directory
        if not target_abs.startswith(working_abs):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # Check if target is a directory
        if not os.path.isdir(target_abs):
            return f'Error: "{directory}" is not a directory'

        # List contents
        entries = []
        for entry in os.listdir(target_abs):
            entry_path = os.path.join(target_abs, entry)
            is_dir = os.path.isdir(entry_path)
            try:
                size = os.path.getsize(entry_path)
            except Exception as e:
                size = f"Error getting size: {e}"
            entries.append(f"- {entry}: file_size={size} bytes, is_dir={is_dir}")

        return "\n".join(entries)

    except Exception as e:
        return f"Error: {e}"
