import os


def create_usercustomize_py(file_path: str) -> None:
    """
    Creates a usercustomize.py file with the content to enable coverage for subprocesses.
    References:
        - https://coverage.readthedocs.io/en/latest/subprocess.html
        - https://stackoverflow.com/questions/60736080/python-coverage-subprocess-coverage-process-startup-error

    Parameters:
    -----------
    file_path: str
        The path to the usercustomize.py file.

    Returns:
    --------
    None
    """
    content = """import coverage
import os
coverage.process_startup()
os.environ["COVERAGE_PROCESS_START"] = "/mnt/shared_storage/Github/voluseg/.coveragerc"
"""
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"usercustomize.py created successfully at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def remove_usercustomize_py(file_path: str) -> None:
    """
    Removes the usercustomize.py file created for enabling coverage for subprocesses.

    Parameters:
    -----------
    file_path: str
        The path to the usercustomize.py file.

    Returns:
    --------
    None
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"usercustomize.py removed successfully from {file_path}")
        else:
            print(f"No usercustomize.py found at {file_path}")
    except Exception as e:
        print(f"An error occurred while trying to remove the file: {e}")
