import io
import nbformat
from jinja2 import DictLoader, Template, FileSystemLoader
from nbconvert import HTMLExporter
from pystache import render

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
  """

HTML_FOOTER = """
  </style>
</head>
{%- endblock header -%} {% block in_prompt %}
<div class="prompt input_prompt"> </div>
{% endblock in_prompt %}

{% block output_prompt %}
{% endblock output_prompt %}

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
</body>
{%- endblock body %} {% block footer %} {{ super() }}

</html>
{% endblock footer %}
    """


def run_to_html(processed_file, css='', with_template=True):
  html_template = HTML_HEADER + css + HTML_FOOTER
  dl = DictLoader({'full.tpl': html_template})
  html_exporter = HTMLExporter(
      extra_loaders=[dl]) if with_template else HTMLExporter()
  with io.open(processed_file, 'r') as f:
    nb = nbformat.reads(f.read(), as_version=4)
  # (body, resources)
  return html_exporter.from_notebook_node(nb)
