import io, os, nbformat
from jinja2 import DictLoader, Template, FileSystemLoader
from nbconvert import HTMLExporter
from pystache import render

from .base import Template
from scss import Compiler
from ..resources import data_dir


class HtmlTemplate(Template):
  def process(self, force=False):
    complete_filename = self.bundle.complete_html_filename()

    if True or not force and not os.path.exists(complete_filename):

      processing_files = self.bundle.prepare()
      output_content = []

      (body, resources) = run_to_html(self.bundle.merged_notebook)
      # self.update_styles()

      with io.open(complete_filename, "w") as f:
        f.write(body)

    return complete_filename


def compiled_scss():
  p = Compiler()
  scss_file = os.path.join(data_dir(), 'style.scss')
  with open(scss_file, 'r') as f:
    compiled = p.compile_string(f.read())
    return compiled


def compiled_javascript():
  deps = [
      os.path.join(data_dir(), 'dom-to-images.js'),
      os.path.join(data_dir(), 'user.js')
  ]
  scripts = []
  for d in deps:
    with open(d, 'r') as f:
      scripts.append('<script type="text/javascript">' + f.read() +
                     '</script>')

  return '\n'.join(scripts)


HTML_HEADER = u"""
{%- extends 'basic.tpl' -%} {% from 'mathjax.tpl' import mathjax %} {%- block header -%}
<!DOCTYPE html>
<html>

<head>
  {%- block html_head -%}
  <meta charset="utf-8" />
  <title>{{resources['metadata']['name']}}</title>

  {%- if "widgets" in nb.metadata -%}
  <script src="https://unpkg.com/jupyter-js-widgets@2.0.*/dist/embed.js"></script> {%- endif-%}

  <script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.1.10/require.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
  {% for css in resources.inlining.css -%}
  <style type="text/css">
  {{ css }}
  </style>
  {% endfor %}
  </style>

  <!-- Loading mathjax macro -->
  {{ mathjax() }} {%- endblock html_head -%}
  <style type="text/css">
    .snapshot_container { width: 100%; }
  </style>
  <style type="text/css">
  """

HTML_BASE = """
  </style>
</head>
{%- endblock header -%} {% block in_prompt %}
<div class="prompt input_prompt"> </div>
{% endblock in_prompt %}

{% block output_prompt %}
{% endblock output_prompt %}

{% block execute_result -%}
{%- set extra_class="output_execute_result snapshot" -%}
{% block data_priority scoped %}

{%- if cell.execution_count is defined -%}
<div id="snapshot-{{ cell.execution_count }}" class="snapshot_container">
{% endif -%}

{{ super() }}

{%- if cell.execution_count is defined -%}
</div>
{% endif -%}


{% endblock %}
{%- set extra_class="" -%}
{%- endblock execute_result %}

{% block output %}
{% block output_area_prompt %}
<div class="prompt output_prompt"></div>
{% endblock output_area_prompt %}
  {{ super() }}
{% endblock output %}

{% block body %}

<body>
  <div id="notebook">
    <div class="container" id="notebook-container">
      {{ super() }}
    </div>
  </div>
"""

HTML_FOOTER = """
</body>
{%- endblock body %} {% block footer %} {{ super() }}

</html>
{% endblock footer %}
    """


def run_to_html(processed_file, with_template=True):
  html_template = HTML_HEADER + compiled_scss(
  ) + HTML_BASE + compiled_javascript() + HTML_FOOTER
  dl = DictLoader({'full.tpl': html_template})
  html_exporter = HTMLExporter(
      extra_loaders=[dl]) if with_template else HTMLExporter()
  with io.open(processed_file, 'r') as f:
    nb = nbformat.reads(f.read(), as_version=4)
  # (body, resources)
  return html_exporter.from_notebook_node(nb)
