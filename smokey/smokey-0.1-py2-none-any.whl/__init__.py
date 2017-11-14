from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

print("Loading Smokey")

from IPython.display import JSON, HTML, display

display(JSON({'a': {'b': 3}}))
display(JSON({'a': {'b': 3}}, expanded=True))


from vdom import h1, div, p, pre, b, span

import IPython
import ipykernel

def version(name, version):
    return div(
        b(name, style=dict(display="table-cell", paddingRight="1rem")),
        span(version, style=dict(display="table-cell")),

        style=dict(display="table-row")
    )

display(
    div(
        h1('Watermark', style=dict(color="#e7e7e7", backgroundColor="#101010", padding="10px")),
        version("smokey version", __version__),
        version("ipython version", IPython.__version__),
        version("ipykernel version", ipykernel.__version__)
    )
)

display(HTML("<h1>IT IS LOADED AND WE ARE DONE</h1>"))
