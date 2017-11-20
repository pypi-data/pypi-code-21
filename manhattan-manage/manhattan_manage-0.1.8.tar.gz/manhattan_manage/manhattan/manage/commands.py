from flask import current_app
from flask_script import Command, Option
from mongoframes import Frame

__all__ = ['add_command']


class BuildIndexes(Command):
    """
    Find and (re)build indexes defined against models.
    """

    def run(self):
        for frame in self.find_frames():
            print('Building indexes for', frame.__name__)

            # Drop any existing indexes
            frame.get_collection().drop_indexes()

            # Build indexes
            frame.get_collection().create_indexes(frame._indexes)

        print('Indexes built')

    def find_frames(self):
        """
        Find all classes that should be considered for index building.

        The current approach is to find tip classes (those at the end of the
        inheritance chain) with the `_indexes` attribute.
        """

        index_classes = []
        sub_classes = Frame.__subclasses__()
        while len(sub_classes) > 0:
            sub_class = sub_classes.pop()
            if len(sub_class.__subclasses__()):
                sub_classes += sub_class.__subclasses__()
            else:
                if hasattr(sub_class, '_indexes'):
                    index_classes.append(sub_class)

        return index_classes


def add_commands(manager):
    """Add commands within the module to the specified command manager"""
    manager.add_command('build-indexes', BuildIndexes)
