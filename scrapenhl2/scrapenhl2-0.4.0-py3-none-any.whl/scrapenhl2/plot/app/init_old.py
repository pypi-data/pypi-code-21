"""
This file imports other views and shows the homepage

/ lists links to homepages for games, help, players, stats, and teams.
"""

import webbrowser
from io import BytesIO

from flask import Flask, render_template, make_response, redirect
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import scrapenhl2.plot.app.player_views as player_views
import scrapenhl2.plot.app.stat_views as stat_views
import scrapenhl2.plot.app.game_views as game_views
import scrapenhl2.plot.app.help_views as help_views
import scrapenhl2.plot.app.team_views as team_views


import scrapenhl2.scrape.scrape_game as sg
import scrapenhl2.scrape.scrape_setup as ss
import scrapenhl2.plot.visualize_game as vg
import scrapenhl2.plot.visualize_player as vp
import scrapenhl2.manipulate.manipulate as manip

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


@app.route('/update/')
def update_data():
    # TODO add streaming output
    try:
        sg.autoupdate()
        return render_template('updatepage.html', msg='Done updating data')
    except Exception as e:
        return render_template('updatepage.html', msg=str(e) + str(e.args))


@app.route('/games/<int:season>/<int:game>/refresh/')
def refresh_game(season, game):
    sg.scrape_game_pbp(season, game, True)
    sg.parse_game_pbp(season, game, True)
    try:
        sg.scrape_game_toi(season, game, True)
        sg.scrape_game_pbp(season, game, True)
    except Exception as e:
        sg.scrape_game_toi_from_html(season, game, True)
        sg.parse_game_toi_from_html(season, game, True)

    return redirect("/games/{0:d}/".format(season), code=302)


@app.route('/players/<int:season>/refresh/')
def refresh_players(season):
    df = manip.generate_5v5_player_log(season)
    manip.save_5v5_player_log(df, season)
    return redirect("/players/")


@app.route('/games/<int:season>/')
@app.route('/games/<int:season>/<team>/')
def get_game_list(season, team=None):
    sch = ss.get_season_schedule(season)

    if team is not None:
        tid = ss.team_as_id(team)
        sch = sch[(sch.Home == tid) | (sch.Road == tid)]

    sch.loc[:, 'Home'] = sch.Home.apply(lambda x: ss.team_as_str(x))
    sch.loc[:, 'Road'] = sch.Road.apply(lambda x: ss.team_as_str(x))
    sch = sch[['Date', 'Game', 'Home', 'Road', 'HomeScore', 'RoadScore', 'Status', 'Result']] \
        .rename(columns={'Result': 'HomeResult'})
    sch.loc[:, 'H2H'] = sch.Game.apply(lambda x: '/games/{0:d}/h2h/{1:d}/'.format(season, x))
    sch.loc[:, 'Timeline'] = sch.Game.apply(lambda x: '/games/{0:d}/tl/{1:d}/'.format(season, x))

    return render_template('games.html', season=season, schedule=sch)


@app.route('/players/')
@app.route('/players/<pfilter>')
def get_player_list(pfilter=None):
    pinfo = ss.get_player_ids_file()

    if pfilter is None:
        pinfo = pinfo.sort_values(by=['Name', 'DOB'])
    else:
        pinfo = ss.add_sim_scores(pinfo, pfilter)
        pinfo = pinfo.sort_values(by=['SimScore', 'DOB'], ascending=False)
        pinfo = pinfo.iloc[:50, :]  # limit size

    pinfo.loc[:, 'Link'] = pinfo.ID.apply(lambda x: '/player/{0:d}'.format(int(x)))
    pinfo = pinfo[['DOB', 'Hand', 'Name', 'Pos', 'Height', 'Weight', 'Link']]
    return render_template('players.html', pinfo=pinfo)


@app.route('/player/<int:pid>/')
def get_player_links(pid):
    pname = ss.player_as_str(pid)
    examplelink = '/player/{0:d}/rollingcf/2016-2018/'.format(int(pid))
    return render_template('individual.html', pname=pname, examplelink=examplelink)


@app.route('/games/<int:season>/<charttype>/<int:game>/')
def team_graph(season, game, charttype):
    # TODO get these working in templates!
    if charttype == 'h2h':
        fig = vg.game_h2h(season, game, "fig")
    elif charttype == 'tl':
        fig = vg.game_timeline(season, game, "fig")
        pass
    else:
        return render_template("chart.html", message="Invalid chart type; use h2h or tl")
    canvas = FigureCanvas(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'

    return response


@app.route('/player/<int:pid>/<charttype>/<int:s1>-<int:s2>/')
def indiv_graph(pid, s1, s2, charttype):
    if charttype == 'rollingcf':
        fig = vp.rolling_player_cf(pid, startseason=s1, endseason=s2-1, save_file="fig")
    else:
        return render_template("chart.html", message="Invalid chart type")
    canvas = FigureCanvas(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'

    return response


@app.route('/games/<int:season>/<int:game>/')
def game_graphs(season, game):
    return 'todo'


def runapp(debug=False):
    webbrowser.open('http://127.0.0.1:5000/', new=2)
    app.run()


if __name__ == '__main__':
    # sg.parse_season_pbp(2017, True)
    # sg.parse_season_toi(2017, True)
    manip.get_player_5v5_log(2017, True)
    runapp(debug=True)
