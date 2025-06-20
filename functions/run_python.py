import os
import subprocess

def run_python_file(working_directory, file_path):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_target_path = os.path.abspath(os.path.join(working_directory, file_path))

        if not abs_target_path.startswith(abs_working_dir):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.exists(abs_target_path):
            return f'Error: File "{file_path}" not found.'

        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        result = subprocess.run(
            ["python", abs_target_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=abs_working_dir
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        exit_code = result.returncode

        response_parts = []
        if stdout:
            response_parts.append(f"STDOUT:\n{stdout}")
        if stderr:
            response_parts.append(f"STDERR:\n{stderr}")
        if exit_code != 0:
            response_parts.append(f"Process exited with code {exit_code}")
        if not response_parts:
            return "No output produced."

        return "\n\n".join(response_parts)

    except Exception as e:
        return f"Error: executing Python file: {e}"
