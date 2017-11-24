import os
import logging
import shutil

from pathlib import Path
from pystache import render

from src.abstract_tree import Node
from src.config import ProjectConfig
from src.config.models.seed import Seed
from src.generation.services.seed_manager import Seed_Manager

template_file_suffix='.mustache'

class Generator:

    def __init__(self):
        self.seed_manager = Seed_Manager()
        self.logger = logging.getLogger(__name__)

    def remove_if_exist(self, path):
        # Remove the targeted folder if it exists
        if path.exists() and path.is_dir():
            self.logger.info("remove the existing dist folder ", path)
            try:
                print("remove", path)
                shutil.rmtree(path.absolute().__str__())
            except Exception:
                self.logger.critical("cannot remove the existing dist folder ")
                raise RuntimeError("cannot remove the existing dist folder ")

    def build(
            self,
            seed: Seed,
            gardener_config: ProjectConfig
    ):
        self.logger.info("Begin the build step")

        relative_tree_label = seed.name
        self.abstract_tree_root = Node(Path(seed.location))
        current_node = self.abstract_tree_root
        current_relative_node = current_node.add_relative(
            label=relative_tree_label,
            relative_path=Path(gardener_config.destination)
        )

        self.remove_if_exist(current_relative_node.path)

        to_walk = [self.abstract_tree_root]
        while to_walk:
            current_node = to_walk.pop()
            current_relative_node = current_node.get_relative(relative_tree_label)
            self.logger.info("creation of the folder ", current_relative_node.path)
            current_relative_node.path.mkdir()

            for f in current_node.path.iterdir():
                child = Node(path=f)
                file_name = render(child.path.name, {'gardener': gardener_config})
                compiled_path = Path(current_relative_node.path, file_name)
                child_relative = child.add_relative(relative_tree_label, compiled_path)
                current_node.add_child(child)

                if f.is_dir():
                    to_walk.append(child)
                elif f.is_file():
                    data = {
                        'gardener': gardener_config,
                        'seed': seed
                    }
                    self.copy_or_compile(child, child_relative, data)

        return self.abstract_tree_root

    def can_copy(self, path: Path):
        ignore = ['puzle-seed.yml']

        return path.name not in ignore

    def copy_or_compile(
            self,
            orig: Node,
            dest: Node,
            data: dict
    ):

        if self.can_copy(orig.path):
            suffix = orig.path.suffix
            with  orig.path.open('r') as orig_content:
                content = orig_content.read()
                if suffix == template_file_suffix:
                    self.logger.info("compile ", orig.path._str)
                    content = render(content, data)
                    file = Path(dest.path.with_suffix(''))
                else:
                    file = Path(dest.path)

                with file.open('w+') as dest_file:
                    self.logger.info("write ", file)
                    dest_file.write(content)
                    print(str(orig.path.absolute()) + " -> " + str(file.absolute()))

    def __call__(self, gardener_config: ProjectConfig, seed: Seed=None):
        # TODO: Find the targeted seed in local system and remote(to generate)
        # TODO: If the targeted seed does not exist on the local system, dl it
        self.logger.info("Begin the generation step")

        if seed:
            self.build(seed, gardener_config)
        else:
            self.logger.error("Cannot find the given seed")
