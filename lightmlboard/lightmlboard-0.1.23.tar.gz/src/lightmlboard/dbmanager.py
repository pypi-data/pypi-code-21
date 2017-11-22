"""
@file
@brief Manages a sqlite3 database to store the results.
"""
import datetime
import numpy
import pandas
from uuid import uuid4
from .dbengine import Database
from .options_helpers import read_options, read_users
from .competition import Competition


class DatabaseCompetition(Database):
    """
    Holds the data used for competitions. Tables:

    Competitions

    * cpt_id
    * cpt_name
    * metric
    * datafile
    * description
    * expected_values

    Teams

    * team_id
    * team_name

    Players

    * player_id
    * team_id
    * player_name
    * mail
    * login
    * pwd

    Submission

    * cpt_id
    * player_id
    * date
    * filename
    * metric_value
    """

    def __init__(self, dbfile):
        """
        @param      dbfile      filename or ``:memory:``
        """
        Database.__init__(self, dbfile)
        self._init()

    def _init(self):
        """
        Creates the tables if not present.
        """
        self.connect()
        tables = self.get_table_list()
        adds = dict(competitions=DatabaseCompetition._col_competitions,
                    teams=DatabaseCompetition._col_teams,
                    players=DatabaseCompetition._col_players,
                    submissions=DatabaseCompetition._col_submissions)
        for k, v in adds.items():
            if k not in tables:
                self.create_table(k, v())
        self.commit()
        self.close()

    def init_from_options(self, filename):
        """
        Initializes the database. It skips a table if
        it exists.

        @param      filename        filename
        """
        opt = read_options(filename)
        if opt is None:
            raise ValueError("No option in '{0}'.".format(filename))
        users = read_users(opt["allowed_users"])
        key = "tmpl_competitions" if "tmpl_competitions" in opt else "competitions"
        competitions = [(d if isinstance(d, Competition)
                         else Competition(**d)) for d in opt[key]]

        if not self.has_rows("teams"):
            teams = map(lambda x: x[1]['team'], users.items())
            tdf = pandas.DataFrame({"team_name": list(teams)})
            tdf.reset_index(drop=False, inplace=True)
            tdf.columns = ["team_id", "team_name"]
            tdf.to_sql("teams", self.Connection,
                       if_exists="append", index=False)

        if not self.has_rows("players"):
            players = list(map(lambda x: x[1], users.items()))
            pdf = pandas.DataFrame(players)
            pdf.reset_index(drop=False, inplace=True)
            tdf = self.to_df("teams")
            pdf["player_name"] = pdf["name"]
            pdf["player_id"] = pdf["index"]
            pdf = pdf.merge(tdf, left_on="team", right_on="team_name")
            pdf = pdf.drop(["name", "team_name", "index", "team"], axis=1)
            pdf.to_sql("players", self.Connection,
                       if_exists="append", index=False)

        if not self.has_rows("competitions"):
            pdf = pandas.DataFrame(Competition.to_records(competitions))
            if "cpt_id" in pdf.columns:
                pdf.reset_index(drop=True, inplace=True)
            else:
                pdf.reset_index(drop=False, inplace=True)
                # tdf = self.to_df("competitions")
                pdf["cpt_id"] = pdf["index"]
                pdf = pdf.drop("index", axis=1)
            pdf.to_sql("competitions", self.Connection,
                       if_exists="append", index=False)

        if not self.has_rows("submissions"):
            pdf = DatabaseCompetition._dummy_submissions()
            pdf.reset_index(drop=True, inplace=True)
            pdf.to_sql("submissions", self.Connection,
                       if_exists="append", index=False)

        df = self.to_df("players")
        logins = set(df['login'])
        if None in logins:
            raise ValueError("One login is wrong: {0}".format(logins))

    def get_competitions(self):
        """
        Returns the list of competitions as list of ``(cpt_id, cpt_name)``.
        """
        return self.execute("SELECT cpt_id, cpt_name FROM competitions")

    def to_df(self, table):
        """
        Returns the content of a table as a dataframe.
        """
        return pandas.read_sql("SELECT * FROM {0}".format(table), self.Connection)

    @property
    def Connection(self):
        """
        Returns the connexion.
        """
        self._check_connection()
        return self._connection

    @staticmethod
    def _col_competitions():
        return [('cpt_id', int), ('link', str), ('cpt_name', str), ('description', str),
                ('metric', str), ('datafile', str), ('expected_values', str)]

    @staticmethod
    def _col_teams():
        return [('team_id', int), ('team_name', str)]

    @staticmethod
    def _col_players():
        return [('player_id', int), ('team_id', int), ('metric', str), ('player_name', str),
                ('mail', str), ('login', str), ('pwd', str)]

    @staticmethod
    def _col_submissions():
        return [('sub_id', str), ('cpt_id', int), ('player_id', int), ('date', str),
                ('data', str), ('metric', str), ('metric_value', float)]

    @staticmethod
    def _dummy_submissions():
        return pandas.DataFrame([dict(sub_id=str(uuid4()), cpt_id=-1, player_id=-1, date=datetime.datetime.now(),
                                      data='', metric='rse', metric_value=numpy.nan)])

    def get_cpt_id(self):
        """
        Returns the list of competation id.
        """
        return list(_[0] for _ in self.execute("SELECT cpt_id FROM competitions"))

    def get_player_id(self):
        """
        Returns the list of competation id.
        """
        return list(_[0] for _ in self.execute("SELECT player_id FROM players"))

    def submit(self, cpt_id, player_id, data, date=datetime.datetime.now()):
        """
        Adds a submission to the database.

        @param      cpt_id          competition id
        @param      player_id       player who did the submission
        @param      data            data of the submission

        The function computes the metric associated to the submission.
        """
        if not isinstance(data, str):
            raise TypeError("data must be str not {0}".format(type(data)))
        cp = list(self.execute(
            "SELECT cpt_id, metric, expected_values FROM competitions WHERE cpt_id={0}".format(cpt_id)))
        if len(cp) == 0:
            raise ValueError("Unable to find cpt_id={0} in\n{1}".format(
                cpt_id, self.get_cpt_id()))
        pid = list(self.execute(
            "SELECT player_id FROM players WHERE player_id={0}".format(player_id)))
        if len(pid) == 0:
            raise ValueError("Unable to find player_id={0} in\n{1}".format(
                player_id, self.get_player_id()))
        metrics = [_[1:] for _ in cp]

        sub = []
        for met, exp in metrics:
            cp = Competition(cpt_id=0, link='', name='', description='',
                             metric=met, expected_values=exp)
            dres = cp.evaluate(data)
            res = dres[met]
            if not isinstance(res, float):
                res = float(res)
            rec = dict(sub_id=str(uuid4()), cpt_id=cpt_id, player_id=player_id,
                       data=data, metric=met, metric_value=res)
            sub.append(rec)

        df = pandas.DataFrame(sub)
        df.to_sql("submissions", self._connection,
                  if_exists="append", index=False)
        self.commit()

    def get_competition(self, cpt_id):
        """
        Retrieves a competition.

        @param      cpt_id  competition id
        @return             @see cl Competition
        """
        res = list(self.execute(
            "SELECT * FROM competitions WHERE cpt_id=={0}".format(cpt_id)))
        if len(res) == 0:
            raise KeyError("No competition for cpt_id=={0}".format(cpt_id))
        if len(res) != 1:
            raise KeyError(
                "Too many competitions for cpt_id=={0}".format(cpt_id))
        args = list(res[0])
        return Competition(*args)

    def get_results(self, cpt_id):
        """
        Retrieves the results of a competition.

        @param      cpt_id  competition id
        @return             a data frame
        """
        res = pandas.read_sql("""SELECT A.*, B.player_name AS player_name, C.team_name
                                 FROM submissions AS A
                                 INNER JOIN players AS B ON A.player_id == B.player_id
                                 INNER JOIN teams AS C ON B.team_id == C.team_id
                                 WHERE cpt_id == {0}
                                 """.format(cpt_id), self.Connection)
        return res
