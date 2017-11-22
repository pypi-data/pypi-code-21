import sys
import os
import glob

import jinja2


def build_adventure(directory: str) -> None:
    """Generate a static site to `output` from the adventure source
    found in the path `source`.

    """

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(directory),
    )
    source_path_pattern = os.path.join(directory, '*', 'trap.sub.html')
    source_file_path = None
    for source_file_path in glob.iglob(source_path_pattern):
        print(source_file_path)
        page_template = jinja_env.get_template(source_file_path)
        page_contents = page_template.render()
        source_file_directory = os.path.dirname(source_file_path)
        output_file_path = os.path.join(source_file_directory, 'index.html')
        with open(output_file_path, 'w') as f:
            f.write(page_contents)
            print(output_file_path)

    if not source_file_path:
        print(
            "No source files found! Must match pattern: %s"
            % source_path_pattern
        )
        sys.exit(1)
