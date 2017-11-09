# elabtui
# Text User Interface for elabftw
# https://www.elabftw.net
# https://github.com/elabftw/elabtui

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
from pathlib import Path
import os.path
import sys
import elabapy
import yaml

class ExperimentModel(object):
    def __init__(self):
        self.current_id = None

    def add(self, experiment):
        exp = manager.create_experiment()
        id = exp["id"]
        manager.post_experiment(id, experiment)

    def get_summary(self):
        exps = manager.get_all_experiments();
        ids = []
        titles = []
        for exp in exps:
            ids.append(exp["id"])
            titles.append(exp["title"])
        return list(zip(titles, ids))

    def get_experiment(self, exp_id):
        return manager.get_experiment(exp_id);

    def get_current_experiment(self):
        return self.get_experiment(self.current_id)

    def update_current_experiment(self, details):
        if self.current_id is None:
            self.add(details)
        else:
            manager.post_experiment(self.current_id, details)

    def delete_experiment(self, experiment_id):
        return True

class ListView(Frame):
    def __init__(self, screen, model):
        super(ListView, self).__init__(screen,
                                       screen.height,
                                       screen.width,
                                       on_load=self._reload_list,
                                       hover_focus=True,
                                       title="Experiments List")
        # Save off the model that accesses the experiments database.
        self._model = model

        # Create the form for displaying the list of experiments.
        self._list_view = ListBox(
            Widget.FILL_FRAME,
            model.get_summary(),
            name="experiments",
            on_change=self._on_pick)
        self._edit_button = Button("Edit", self._edit)
        self._delete_button = Button("Delete", self._delete)
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._list_view)
        layout.add_widget(Divider())
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("New", self._add), 0)
        layout2.add_widget(self._edit_button, 1)
        layout2.add_widget(self._delete_button, 2)
        layout2.add_widget(Button("Quit", self._quit), 3)
        self.fix()
        self._on_pick()

    def _on_pick(self):
        self._edit_button.disabled = self._list_view.value is None
        self._delete_button.disabled = self._list_view.value is None

    def _reload_list(self, new_value=None):
        self._list_view.options = self._model.get_summary()
        self._list_view.value = new_value

    def _add(self):
        self._model.current_id = None
        raise NextScene("Edit Experiment")

    def _edit(self):
        self.save()
        self._model.current_id = self.data["experiments"]
        raise NextScene("Edit Experiment")

    def _delete(self):
        self.save()
        self._model.delete_experiment(self.data["experiments"])
        self._reload_list()

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")


class ExperimentView(Frame):
    def __init__(self, screen, model):
        super(ExperimentView, self).__init__(screen,
                                          screen.height * 2 // 3,
                                          screen.width * 2 // 3,
                                          hover_focus=True,
                                          title="Experiment Details",
                                          reduce_cpu=True)
        # Save off the model that accesses the experiments database.
        self._model = model

        # Create the form for displaying the list of experiments.
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("Title:", "title"))
        layout.add_widget(Text("Date:", "date"))
        layout.add_widget(TextBox(
            Widget.FILL_FRAME, "Content", "body", as_string=True))
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 3)
        self.fix()

    def reset(self):
        # Do standard reset to clear out form, then populate with new data.
        super(ExperimentView, self).reset()
        self.data = self._model.get_current_experiment()

    def _ok(self):
        self.save()
        self._model.update_current_experiment(self.data)
        raise NextScene("Main")

    @staticmethod
    def _cancel():
        raise NextScene("Main")


def demo(screen, scene):
    scenes = [
        Scene([ListView(screen, experiments)], -1, name="Main"),
        Scene([ExperimentView(screen, experiments)], -1, name="Edit Experiment")
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene)

experiments = ExperimentModel()
# read config
config = yaml.safe_load(open(os.path.join(Path.home(), ".config/elabtui/config.yml")))
# init manager from elabapy
manager = elabapy.Manager(token=config["token"], endpoint=config["endpoint"], dev=True)

def main():

    last_scene = None

    while True:
        try:
            Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene
