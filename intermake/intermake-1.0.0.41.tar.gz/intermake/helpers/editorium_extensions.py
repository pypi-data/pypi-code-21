"""
Creates and registers additional GUI editors.
"""

# (defer through function so we don't have to load Qt)
def __editors() -> type:
    from intermake.hosts.frontends.gui_qt.editorium_extensions import Editor_Visualisable
    return Editor_Visualisable


import editorium
editorium.register( __editors )