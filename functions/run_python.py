import os
import subprocess


def run_python_file(working_directory, file_path, args=None):
    try:
        working_abs = os.path.abspath(working_directory)
        target_abs = os.path.abspath(os.path.join(working_directory, file_path))

        # Validate working directory scope
        if not target_abs.startswith(working_abs):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.exists(target_abs):
            return f'Error: File "{file_path}" not found.'

        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        # Build command with optional arguments
        cmd = ["python3", target_abs]
        if args:
            if isinstance(args, str):
                cmd.append(args)
            elif isinstance(args, list):
                cmd.extend(args)

        # Run subprocess
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=working_abs,
            timeout=30,
        )

        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")

        if not output:
            return "No output produced."

        return "\n".join(output)

    except Exception as e:
        return f"Error: executing Python file: {e}"
