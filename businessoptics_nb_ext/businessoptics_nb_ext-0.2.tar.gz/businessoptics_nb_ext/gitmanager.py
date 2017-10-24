import io
import json
import os.path
import traceback
from collections import OrderedDict
from datetime import datetime

import nbformat
from notebook.services.contents.filemanager import FileContentsManager


class GitContentsManager(FileContentsManager):
    def get(self, path, content=True, type=None, format=None):
        try:
            if self._path_is_notebook(path) or type == 'notebook':
                src_path = self._get_subpaths(path, True)[1]
                if os.path.exists(src_path):
                    return self._load_flat_notebook(path, content)
        except:
            # This will make debugging in the future a lot easier
            traceback.print_exc()
            raise

        return super(GitContentsManager, self).get(path, content, type, format)

    def _load_flat_notebook(self, path, content):

        _, src_path, output_path = self._get_subpaths(path, True)

        packet = dict(
            name=os.path.basename(path),
            type='notebook',
            format='json' if content else None,
            last_modified=datetime.fromtimestamp(os.path.getmtime(src_path)),
            content=None,
            writable=True,
            path=path,
            mimetype=None,
            created=None
        )

        if not content:
            return packet

        header = []
        cells = []
        current_cell = None
        cell_lines = []
        in_header = True

        def deposit_cell():
            if current_cell:
                current_cell['source'] = "".join(cell_lines).strip('\n')
                cells.append(current_cell)
                cell_lines.clear()

        def create_cell(line):
            current_cell = {
                'cell_type': 'code',
                'metadata': {},

            }
            current_cell.update(json.loads(line.partition(" ")[2]))
            if current_cell['cell_type'] == 'code':
                current_cell.update({
                    'execution_count': None,
                    'outputs': []
                })
            return current_cell

        with open(src_path) as sf:
            for line in sf:
                if in_header:
                    if line[0] == '#' and not line.startswith("##--cell"):
                        header.append(line)
                    else:
                        in_header = False

                if not in_header:
                    if line.startswith("##--cell"):
                        deposit_cell()
                        current_cell = create_cell(line)
                    else:
                        cell_lines.append(line)

            deposit_cell()

        nb = json.loads("".join([line[1:] for line in header[1:]]))

        packet['content'] = nb

        # Load output if it exists
        if os.path.exists(output_path):
            with open(output_path) as of:
                output = json.load(of)

            for cell, output in zip(cells, output['cells']):
                if cell['cell_type'] == 'code':
                    cell.update(dict(
                        execution_count=output.get('execution_count'),
                        outputs=output.get('outputs', [])
                    ))

        nb['cells'] = cells

        return packet

    def _convert_to_source(self, nb):
        buf = []
        buf.append("# Git friendly notebook")
        headers = OrderedDict(
            (key, nb[key]) for key in ['nbformat', 'nbformat_minor', 'metadata']
        )

        header_stream = io.StringIO(json.dumps(headers, indent=2))
        for line in header_stream:
            buf.append('# ' + line.strip('\n'))

        cells = nb['cells']
        for cell in cells:
            source = cell['source']
            cell_metadata = {
                'cell_type': cell['cell_type']
            }
            buf.append('\n##--cell {}\n'.format(json.dumps(cell_metadata)))
            buf.append(source)

        return '\n'.join(buf)

    def _path_is_notebook(self, path):
        return path.endswith('.ipynb') or path.endswith('_flat.py')

    def _get_subpaths(self, os_path, strip):
        if strip:
            os_path = os_path.strip("/")

        folder, base = os.path.split(os_path)
        if base.endswith("_flat.py"):
            name = base[:-len("_flat.py")]
        else:
            name = base.partition('.')[0]

        source_path = os.path.join(folder, name + "_flat.py")
        ipynb_path = os.path.join(folder, name + ".ipynb")
        output_path = os.path.join(folder, "." + name + ".ipynboutput")

        return ipynb_path, source_path, output_path

    def _save_notebook(self, os_path, nb):
        """Save a notebook to an os_path."""
        ipynb_path, source_path, output_path = self._get_subpaths(os_path, False)

        with open(ipynb_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f, version=nbformat.NO_CONVERT)

        with open(source_path, 'w', encoding='utf-8') as f:
            src = self._convert_to_source(nb)
            f.write(src)

        with open(output_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f, version=nbformat.NO_CONVERT)

    def rename_file(self, old_path, new_path):
        """Rename a file."""

        # Treat everything else as usual
        if not self._path_is_notebook(old_path):
            super(GitContentsManager, self).rename_file(old_path, new_path)
            return

        # Call super class' rename function on each component
        old_paths = self._get_subpaths(old_path, False)
        new_paths = self._get_subpaths(new_path, False)
        pairs = zip(old_paths, new_paths)
        for old_component_path, new_component_path in pairs:
            old_component_os_path = self._get_os_path(old_component_path)
            if os.path.exists(old_component_os_path):
                super(GitContentsManager, self).rename_file(old_component_path, new_component_path)

    def delete_file(self, path):
        """Delete a file."""
        # Treat everything else as usual
        if not self._path_is_notebook(path):
            super(GitContentsManager, self).delete_file(path)
            return

        components = self._get_subpaths(path, False)

        # Try delete all the paths and store first exception
        exception = None
        for component in components:
            try:
                super(GitContentsManager, self).delete_file(component)
            except Exception as e:
                if not exception:
                    exception = e

        # Check deletion was a success
        if any(self.file_exists(component) for component in components) and exception:
            raise exception
