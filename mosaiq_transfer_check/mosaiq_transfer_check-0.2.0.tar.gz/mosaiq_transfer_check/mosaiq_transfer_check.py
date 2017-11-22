import os
from notebook.notebookapp import NotebookApp

NOTEBOOK_DIRECTORY = os.path.join(
    os.path.dirname(__file__))

def main():
    NotebookApp.launch_instance(notebook_dir=NOTEBOOK_DIRECTORY)

if __name__ == "__main__":
    main()