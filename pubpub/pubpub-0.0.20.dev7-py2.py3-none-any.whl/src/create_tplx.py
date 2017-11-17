import logging
from jinja2 import Template
# % filter_data_type returns the first available format in the data priority
# ((* block execute_result scoped *))
#     ((*- for type in output.data | filter_data_type -*))
#         {{notebook_output}}
#     ((*- endfor -*))
# ((* endblock execute_result *))

TPLX_OUTLINE = r"""
((=
{{title}} template
=))

((*- extends 'article.tplx' -*))

((* block docclass *))
\documentclass[12pt]{book}
{{docclass}}
((* endblock *))

((* block commands *))
\setcounter{secnumdepth}{0} % Turns off numbering for sections
((( super() )))
((* endblock commands *))

((* block author *))
\author{ {{', '.join(authors)}} }
((* endblock author *))

((* block title *))
\title{ {{title}} }
((* endblock title *))

((* block predoc *))
((( super() )))
((* endblock predoc *))

((* block abstract *))
{% if abstract -%}
{{abstract}}
{% else -%}
\tableofcontents
{% endif -%}
((* endblock abstract *))

((* block packages *))
((( super() )))
\usepackage{titlesec}
\usepackage{titletoc}
((* endblock *))

% remove In[]
((* block input scoped *))
   ((( custom_add_prompt(cell.source | wrap_text(80) | highlight_code(strip_verbatim=True), cell, '', 'incolor') )))
((* endblock input *))

% Display stream ouput with coloring
((* block stream *))
    \begin{Verbatim}[commandchars=\\\{\},fontsize=\footnotesize]
((( output.text | truncate(300, False, '\n...') | wrap_text(80) | escape_latex | ansi2latex )))
    \end{Verbatim}
((* endblock stream *))

% Remove Out[]
((* block execute_result scoped *))
    ((*- for type in output.data | filter_data_type -*))
        ((*- if type in ['text/plain']*))

\begin{Verbatim}[commandchars=\\\{\},fontsize=\footnotesize]
((( output.data['text/plain'] | truncate(300, False, '\n...') | wrap_text(80) | escape_latex )))
\end{Verbatim}

        ((* else -*))
            ((* block data_priority scoped *))
            ((( super() )))
            ((* endblock *))
        ((*- endif -*))
    ((*- endfor -*))
((* endblock execute_result *))

%==============================================================================
% Define macro custom_add_prompt() (derived from add_prompt() macro in style_ipython.tplx)
%==============================================================================

((* macro custom_add_prompt(text, cell, prompt, prompt_color) -*))
    ((*- if cell.execution_count is defined -*))
    ((*- set execution_count = "" ~ (cell.execution_count | replace(None, " ")) -*))
    ((*- else -*))
    ((*- set execution_count = " " -*))
    ((*- endif -*))
    ((*- set indention =  " " * (execution_count | length + 7) -*))
\begin{Verbatim}[commandchars=\\\{\}]
((( text | add_prompts(first='{\color{' ~ prompt_color ~ '}' ~ prompt ~ '}', cont='  ') )))
\end{Verbatim}
((*- endmacro *))
"""


def create_tplx(tplx_dicts=(), outpath=None):
  """ build a latex jinja template from multiple dictionaries,
    specifying fragments of the template to insert a specific points

    if a tplx_dict contains the key "overwrite",
    then its value should be a list of keys,
    such that these key values overwrite any entries before

    Parameters
    ----------
    tplx_dicts: list of dicts
    outpath: str
        if not None, output template to file

    """
  outline = TPLX_OUTLINE
  tplx_sections = {
      'meta_docstring': '',
      'document_docclass': None,
      'document_packages': '',
      'document_definitions': '',
      'document_margins': '',
      'document_commands': '',
      'document_header_end': '',
      'document_title': '',
      'document_abstract': None,
      'document_predoc': '',
      'document_bibliography': '',
      'document_postdoc': '',
      'notebook_input': '',
      'notebook_input_code': '',
      'notebook_input_raw': '',
      'notebook_input_markdown': '',
      'notebook_input_unknown': '',
      'notebook_output': None,
      'notebook_output_text': '',
      'notebook_output_error': '',
      'notebook_output_traceback': '',
      'notebook_output_stream': '',
      'notebook_output_latex': '',
      'notebook_output_markdown': '',
      'notebook_output_png': '',
      'notebook_output_jpg': '',
      'notebook_output_svg': '',
      'notebook_output_pdf': '',
      'jinja_macros': ''
  }

  # for i, tplx_dict in enumerate(tplx_dicts):
  #   if 'overwrite' in list(tplx_dict.keys()):
  #     overwrite = tplx_dict['overwrite']
  #   else:
  #     overwrite = []
  #   logging.debug('overwrite keys: {}'.format(overwrite))
  #   for key, val in tplx_dict.items():
  #     if key == 'overwrite':
  #       pass
  #     elif key not in tplx_sections:
  #       raise ValueError(
  #           '{0} from tplx_dict {1} not in outline tplx section'.format(
  #               key, i))
  #     elif key in overwrite:
  #       tplx_sections[key] = val
  #     else:
  #       tplx_sections[key] = tplx_sections[key] + '\n' + val

  dicts = tplx_sections.copy()
  dicts.update(**tplx_dicts)

  template = Template(outline)
  outline = template.render(**dicts)

  if outpath is not None:
    with open(outpath, 'w') as f:
      f.write(outline)
    return
  return outline
