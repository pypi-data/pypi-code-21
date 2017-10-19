# coding=utf-8
import jinja2
import os
from flask import Flask, render_template, request, send_from_directory

from mali_commands.data_volume import with_repo

app = Flask(__name__)

template_folder = os.path.join(os.path.dirname(__file__), 'templates')

my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader([template_folder]),
])

app.jinja_loader = my_loader


@app.route('/images/<path:path>')
def create_images_handler(path):
    data_path = app.config['data_path']

    return send_from_directory(data_path, path)


@app.route("/")
def main():
    query = request.args.get('q')

    repo_root = app.config['repo_root']
    config_prefix = app.config['config_prefix']

    with with_repo(config_prefix, repo_root) as repo:
        return render_template('index.html', images=repo.metadata.query(query))
