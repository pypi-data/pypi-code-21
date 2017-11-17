# -*- coding: utf-8 -*-

import os
import click
from slugify import slugify
from jinja2 import Template
from sqlalchemy import create_engine
import logging

logger = logging.getLogger('__name__')

TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.15/css/dataTables.bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/buttons/1.3.1/css/buttons.dataTables.min.css">
    <script type="text/javascript" language="javascript" src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script type="text/javascript" language="javascript" src="https://cdn.datatables.net/1.10.15/js/jquery.dataTables.min.js"></script>
    <script type="text/javascript" language="javascript" src="https://cdn.datatables.net/1.10.15/js/dataTables.bootstrap.min.js"></script>
    <script type="text/javascript" language="javascript" src="https://cdn.datatables.net/buttons/1.3.1/js/dataTables.buttons.min.js"></script>
    <script type="text/javascript" language="javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js"></script>
    <script type="text/javascript" language="javascript" src="https://cdn.datatables.net/buttons/1.3.1/js/buttons.html5.min.js"></script>
    <title>{{title}}</title>
  </head>
  <body>

    <div class="container">
      <div class="row">
        <div class="col-md-12">
            <table id="{{_id}}" class="{{table_class}}">
              <!-- table header -->
              <thead>
                <tr>
                   {% for key in header %}
                   <th> {{ key }} </th>
                   {% endfor %}
                </tr>
              </thead>

              <!-- table rows -->
              <tbody>
              {% for dict_item in data %}
                <tr>
                   {% for key in header %}
                   <td> {{ dict_item[key] }} </td>
                   {% endfor %}
                </tr>
                {% endfor %}
              </tbody>
            </table>
        </div>
      </div>
    </div>
    <script>
        $(document).ready(function() {
            $('#{{_id}}').DataTable( {
                dom: 'Bfrtip',
                buttons: [
                    'excelHtml5',
                    'csvHtml5',
                    'pdfHtml5'
                ]
            } );
        } );
    </script>
</body>
</html>
"""


def to_dict(engine):
    '''
    Convert database table to a Pythonic structure

    Parameters
    ----------
    engine:sqlalchemy.engine.Engine

    Returns
    -------
    dict
        keys are table name 'slugified'
        values are a list of dict
    '''
    result = {}
    cnx = engine.connect()
    for table in engine.table_names():
        slug = slugify(table, to_lower=True, separator='_')
        result[slug] = [dict(row)
                        for row in cnx.execute(f'select * from {table}')]
    return result


def to_html(rows, title, _id='data', _class='table'):
    '''
    records rows to html

    Parameters
    ----------
    rows:records.rows
    _title:str
    _id:str
    _class:str

    Returns
    -------
    str
        html as text
    '''
    # FIXME:header as a variable ?
    try:
        header = list(rows[0].keys())
    except IndexError as e:
        logger.error(e)
        raise ValueError(f'{title} seems to be empty (no rows)')
    template = Template(TEMPLATE)
    return template.render({'data': rows,
                          'title': title,
                          '_id': _id,
                          'table_class': _class,
                          'header': header})


@click.command()
@click.argument('db_path', type=click.Path(exists=True))
@click.argument('folder', type=click.Path(exists=True))
def cli(db_path, folder):
    """
    Convert sqlite db to html : one file per table
    """
    engine = create_engine(f'sqlite:///{db_path}')
    for table, rows in to_dict(engine).items():
        with open(os.path.join(folder, f'{table}.html'), 'w') as fd:
            fd.write(to_html(rows, table))


if __name__ == "__main__":
    cli()
