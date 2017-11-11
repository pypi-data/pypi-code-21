def _jupyter_nbextension_paths():  # pragma: no cover
    return [
      {
        'section': "notebook",
        'src': "static",
        'dest': "jupyter-homework",
        'require': 'jupyter-homework/notebook'
      },{
        'section': "tree",
        'src': "static",
        'dest': "jupyter-homework",
        'require': 'jupyter-homework/tree'
      },{
        'section': "common",
        'src': "static",
        'dest': "jupyter-homework",
        'require': 'jupyter-homework/common'
      }
    ]
