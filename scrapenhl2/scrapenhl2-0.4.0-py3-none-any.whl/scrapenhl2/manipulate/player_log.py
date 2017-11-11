"""
This module contains methods related to generating the 5v5 player log.
"""


def get_5v5_player_game_cfca(season, team):
    """
    Gets CFON, CAON, CFOFF, and CAOFF by game for given team in given season.
    :param season: int, the season
    :param team: int, team id
    :return: df with game, player, CFON, CAON, CFOFF, and CAOFF
    """
    team = team_info.team_as_id(team)
    # TODO create generate methods. Get methods check if file exists and if not, create anew (or overwrite)
    pbp = filter_for_corsi(teams.get_team_pbp(season, team))
    pbp.loc[:, 'TeamEvent'] = pbp.Team.apply(lambda x: 'CF' if x == team else 'CA')

    teamtotals = pbp[['Game', 'TeamEvent']] \
        .assign(Count=1) \
        .groupby(['Game', 'TeamEvent']).count().reset_index() \
        .pivot_table(index='Game', columns='TeamEvent', values='Count').reset_index() \
        .rename(columns={'CF': 'TeamCF', 'CA': 'TeamCA'})

    toi = teams.get_team_toi(season, team)
    toi = toi[['Game', 'Time', 'Team1', 'Team2', 'Team3', 'Team4', 'Team5']].drop_duplicates()
    indivtotals = pbp.merge(toi, how='left', on=['Game', 'Time'])
    indivtotals = indivtotals[['Game', 'TeamEvent', 'Team1', 'Team2', 'Team3', 'Team4', 'Team5']] \
        .melt(id_vars=['Game', 'TeamEvent'], value_vars=['Team1', 'Team2', 'Team3', 'Team4', 'Team5'],
              var_name='Temp', value_name='PlayerID') \
        .drop('Temp', axis=1) \
        .assign(Count=1) \
        .groupby(['Game', 'TeamEvent', 'PlayerID']).count().reset_index() \
        .pivot_table(index=['Game', 'PlayerID'], columns='TeamEvent', values='Count').reset_index() \
        .rename(columns={'CF': 'CFON', 'CA': 'CAON'})

    df = indivtotals.merge(teamtotals, how='inner', on='Game')
    for col in ['CFON', 'CAON', 'TeamCF', 'TeamCA']:
        if col not in df.columns:
            df.loc[:, col] = 0
        df.loc[:, col] = df[col].fillna(0)
    df.loc['CFOFF'] = df.TeamCF - df.CFON
    df.loc['CAOFF'] = df.TeamCA - df.CAON
    return df



def get_5v5_player_game_boxcars(season, team):
    df = teams.get_team_pbp(season, team)
    fives = filter_for_five_on_five(df)
    fives = filter_for_team(fives, team)

    # iCF
    icf = count_by_keys(filter_for_corsi(fives), 'Game', 'Actor') \
        .rename(columns={'Actor': 'PlayerID', 'Count': 'iCF'})

    # iFF
    iff = count_by_keys(filter_for_fenwick(fives), 'Game', 'Actor') \
        .rename(columns={'Actor': 'PlayerID', 'Count': 'iFF'})

    # iSOG
    isog = count_by_keys(filter_for_sog(fives), 'Game', 'Actor') \
        .rename(columns={'Actor': 'PlayerID', 'Count': 'iSOG'})

    # iG
    goals = filter_for_goals(fives)
    ig = count_by_keys(goals, 'Game', 'Actor') \
        .rename(columns={'Actor': 'PlayerID', 'Count': 'iG'})

    # iA1--use Recipient column
    primaries = count_by_keys(goals, 'Game', 'Recipient') \
        .rename(columns={'Recipient': 'PlayerID', 'Count': 'iA1'})

    # iA1
    secondaries = goals[['Game', 'Note']]
    # Extract using regex: ...assists: [stuff] (num), [stuff] (num)
    # The first "stuff" is A1, second is A2. Nums are number of assists to date in season
    secondaries.loc[:, 'Player'] = secondaries.Note.str.extract('assists: .*\(\d+\),\s(.*)\s\(\d+\)')
    secondaries = count_by_keys(secondaries, 'Game', 'Player') \
        .rename(columns={'Count': 'iA2'})
    # I also need to change these to player IDs. Use iCF for help.
    # Assume single team won't have 2 players with same name in same season
    playerlst = icf[['PlayerID']] \
        .merge(players.get_player_ids_file().rename(columns={'ID': 'PlayerID'}),
               how='left', on='PlayerID')
    secondaries.loc[:, 'PlayerID'] = players.playerlst_as_id(secondaries.Player, True, playerlst)
    secondaries = secondaries[['Game', 'PlayerID', 'iA2']]

    boxcars = ig.merge(primaries, how='outer', on=['Game', 'PlayerID']) \
        .merge(secondaries, how='outer', on=['Game', 'PlayerID']) \
        .merge(isog, how='outer', on=['Game', 'PlayerID']) \
        .merge(iff, how='outer', on=['Game', 'PlayerID']) \
        .merge(icf, how='outer', on=['Game', 'PlayerID'])

    for col in boxcars.columns:
        boxcars.loc[:, col] = boxcars[col].fillna(0)

    return boxcars


def get_5v5_player_game_toicomp(season, team):
    """
    Calculates data for QoT and QoC at a player-game level for given team in given season.
    :param season: int, the season
    :param team: int, team id
    :return: df with game, player,
    """

    toidf = teams.get_team_toi(season, team).drop_duplicates()
    toidf.loc[:, 'TeamStrength'] = toidf.TeamStrength.astype(str)
    toidf.loc[:, 'OppStrength'] = toidf.OppStrength.astype(str)
    # Filter to 5v5
    toidf = toidf[(toidf.TeamStrength == '5') & (toidf.OppStrength == '5')] \
        .drop({'FocusTeam', 'TeamG', 'OppG', 'Team6', 'Opp6', 'TeamScore', 'OppScore',
               'Team', 'Opp', 'Time', 'TeamStrength', 'OppStrength', 'Home', 'Road'},
              axis=1, errors='ignore')

    if len(toidf) > 0:
        df_for_qoc = toidf
        df_for_qot = toidf.assign(Opp1=toidf.Team1, Opp2=toidf.Team2,
                                  Opp3=toidf.Team3, Opp4=toidf.Team4, Opp5=toidf.Team5)

        qc1 = _long_on_player_and_opp(df_for_qoc)
        qc2 = _merge_toi60_position_calculate_comp(qc1, season, 'Comp')

        qt1 = _long_on_player_and_opp(df_for_qot)
        qt2 = _merge_toi60_position_calculate_comp(qt1, season, 'Team')

        qct = qc2.merge(qt2, how='inner', on=['Game', 'TeamPlayerID'])
        qct.loc[:, 'Team'] = team
        qct = qct.rename(columns={'TeamPlayerID': 'PlayerID'})
        return qct
    else:
        return None


def _long_on_player_and_opp(df):
    """
    A helper method for get_5v5_player_game_toicomp. Goes from standard format (which has one row per second) to
    long format (one row per player1-player2 pair)
    :param df: dataframe with game and players
    :return: dataframe, melted
    """

    # Melt opponents down. Group by Game, TeamPlayers, and Opponent, and take counts
    # Then melt by team players. Group by game, team player, and opp player, and sum counts
    df2 = pd.melt(df, id_vars=['Game', 'Team1', 'Team2', 'Team3', 'Team4', 'Team5'],
                  value_vars=['Opp1', 'Opp2', 'Opp3', 'Opp4', 'Opp5'],
                  var_name='OppNum', value_name='OppPlayerID').drop('OppNum', axis=1).assign(Secs=1)
    df2 = df2.groupby(['Game', 'OppPlayerID', 'Team1',
                       'Team2', 'Team3', 'Team4', 'Team5']).sum().reset_index()
    df2 = pd.melt(df2, id_vars=['Game', 'OppPlayerID', 'Secs'],
                  value_vars=['Team1', 'Team2', 'Team3', 'Team4', 'Team5'],
                  var_name='TeamNum', value_name='TeamPlayerID').drop('TeamNum', axis=1)
    # Filter out self for team cases
    df2 = df2.query("TeamPlayerID != OppPlayerID")
    df2 = df2.groupby(['Game', 'TeamPlayerID', 'OppPlayerID']).sum().reset_index()
    return df2


def _merge_toi60_position_calculate_comp(df, season, suffix='Comp'):
    """
    Merges dataframe with toi60 and positions to calculate QoC or QoT by player and game.
    Used in get_5v5_player_game_toicomp
    :param df: dataframe with players and times faced
    :param suffix: use 'Comp' for QoC and 'Team' for QoT
    :return: a dataframe with QoC and QoT by player and game
    """

    toi60df = get_player_toion_toioff_file(season)
    posdf = get_player_positions()

    # Attach toi60 and positions, and calculate sums
    qoc = df.merge(toi60df, how='left', left_on='OppPlayerID', right_on='PlayerID') \
        .merge(posdf, how='left', left_on='OppPlayerID', right_on='ID') \
        .drop({'PlayerID', 'TOION', 'TOIOFF', 'TOI%', 'ID'}, axis=1)
    qoc.loc[:, 'Pos2'] = qoc.Pos.apply(
        lambda x: 'D' + suffix if x == 'D' else 'F' + suffix)  # There shouldn't be any goalies
    qoc.loc[:, 'TOI60Sum'] = qoc.Secs * qoc.TOI60
    qoc = qoc.drop('Pos', axis=1)
    qoc = qoc.drop({'OppPlayerID', 'TOI60'}, axis=1) \
        .groupby(['Game', 'TeamPlayerID', 'Pos2']).sum().reset_index()
    qoc.loc[:, suffix] = qoc.TOI60Sum / qoc.Secs
    qoc = qoc[['Game', 'TeamPlayerID', 'Pos2', suffix]] \
        .pivot_table(index=['Game', 'TeamPlayerID'], columns='Pos2', values=suffix).reset_index()
    return qoc


def get_5v5_player_game_shift_startend(season, team):
    return pd.DataFrame({'PlayerID': [0], 'Game': [0]})


def generate_5v5_player_log(season):
    """
    Takes the play by play and adds player 5v5 info to the master player log file, noting TOI, CF, etc.
    This takes awhile because it has to calculate TOICOMP.
    :param season: int, the season
    :return: nothing
    """
    print('Generating player log for {0:d}'.format(season))

    to_concat = []

    # Recreate TOI60 file.
    _ = get_player_toion_toioff_file(season, force_create=True)

    for team in schedules.get_teams_in_season(season):
        try:
            goals = get_5v5_player_game_boxcars(season, team)  # G, A1, A2, SOG, iCF
            cfca = get_5v5_player_game_cfca(season, team)  # CFON, CAON, CFOFF, CAOFF, and same for goals
            toi = get_5v5_player_game_toi(season, team)  # TOION and TOIOFF
            toicomp = get_5v5_player_game_toicomp(season, team)  # FQoC, F QoT, D QoC, D QoT, and respective Ns
            shifts = get_5v5_player_game_shift_startend(season, team)  # OZ, NZ, DZ, OTF-O, OTF-D, OTF-N

            temp = toi \
                .merge(cfca, how='left', on=['PlayerID', 'Game']) \
                .merge(toicomp.drop('Team', axis=1), how='left', on=['PlayerID', 'Game']) \
                .merge(goals, how='left', on=['PlayerID', 'Game'])
            # .merge(shifts, how='left', on=['PlayerID', 'Game'])

            to_concat.append(temp)
        except Exception as e:
            print('Issue with generating game-by-game for', season, team)
            print(e)

    df = pd.concat(to_concat)
    for col in df.columns:
        df.loc[:, col] = pd.to_numeric(df[col])
    df = df[df.Game >= 20001]  # no preseason
    df = df[df.Game <= 30417]  # no ASG, WC, Olympics, etc
    for col in df:
        if df[col].isnull().sum() > 0:
            print('In player log, {0:s} has null values; filling with zeroes'.format(col))
            df.loc[:, col] = df[col].fillna(0)
    return df


def get_toicomp_file(season, force_create=False):
    """
    If you want to rewrite the TOI60 file, too, then run get_player_toion_toioff_file with force_create=True before
    running this method.

    :param season: int, the season
    :param force_create: bool, should this be read from file if possible, or created from scratch

    :return:
    """

    fname = get_toicomp_filename(season)
    if os.path.exists(fname) and not force_create:
        return pd.read_csv(fname)
    else:
        df = generate_toicomp(season)
        save_toicomp_file(df, season)
        return get_toicomp_file(season)


def get_toicomp_filename(season):
    """

    :param season: int, the season

    :return:
    """
    return os.path.join(organization.get_other_data_folder(), '{0:d}_toicomp.csv'.format(season))


def save_toicomp_file(df, season):
    """

    :param df:
    :param season: int, the season

    :return:
    """
    df.to_csv(get_toicomp_filename(season), index=False)


def generate_toicomp(season):
    """
    Generates toicomp at a player-game level

    :param season: int, the season

    :return: df,
    """

    team_by_team = []
    allteams = team_info.get_teams_in_season(season)
    for i, team in enumerate(allteams):
        if os.path.exists(teams.get_team_toi_filename(season, team)):
            print('Generating TOICOMP for {0:d} {1:s} ({2:d}/{3:d})'.format(
                season, team_info.team_as_str(team), i + 1, len(allteams)))

            qct = get_5v5_player_game_toicomp(season, team)
            if qct is not None:
                team_by_team.append(qct)

    df = pd.concat(team_by_team)
    return df


def get_5v5_player_log(season, force_create=False):
    """

    :param season: int, the season
    :param force_create: bool, create from scratch even if it exists?

    :return:
    """
    fname = get_5v5_player_log_filename(season)
    if os.path.exists(fname) and not force_create:
        return feather.read_dataframe(fname)
    else:
        df = generate_5v5_player_log(season)
        save_5v5_player_log(df, season)
        return get_5v5_player_log(season)


def get_5v5_player_log_filename(season):
    """

    :param season: int, the season

    :return:
    """
    return os.path.join(organization.get_other_data_folder(), '{0:d}_player_5v5_log.feather'.format(season))


def save_5v5_player_log(df, season):
    """

    :param season: int, the season

    :return: nothing
    """
    return feather.write_dataframe(df, get_5v5_player_log_filename(season))



def get_5v5_player_game_toi(season, team):
    """
    Gets TOION and TOIOFF by game and player for given team in given season.

    :param season: int, the season
    :param team: int, team id

    :return: df with game, player, TOION, and TOIOFF
    """
    fives = teams.get_team_toi(season, team) \
        .query('TeamStrength == "5" & OppStrength == "5"') \
        .filter(items=['Game', 'Time', 'Team1', 'Team2', 'Team3', 'Team4', 'Team5'])

    # Get TOI by game. This is to get TOIOFF
    time_by_game = fives[['Game', 'Time']].groupby('Game').count().reset_index().rename(columns={'Time': 'TeamTOI'})

    # Now get a long dataframe of individual TOI
    fives2 = fives[['Game', 'Time', 'Team1', 'Team2', 'Team3', 'Team4', 'Team5']]
    fives_long = pd.melt(fives2, id_vars=['Time', 'Game'], value_vars=['Team1', 'Team2', 'Team3', 'Team4', 'Team5'],
                         var_name='Team', value_name='Player') \
        .drop('Team', axis=1)

    # Now, by player. First at a game level to get TOIOFF
    toi_by_player = fives_long.groupby(['Player', 'Game']).count() \
        .reset_index() \
        .rename(columns={'Time': 'TOION'}) \
        .merge(time_by_game, how='left', on='Game')
    toi_by_player.loc[:, 'TOION'] = toi_by_player.TOION / 3600
    toi_by_player.loc[:, 'TOIOFF'] = toi_by_player.TeamTOI / 3600 - toi_by_player.TOION

    return toi_by_player.rename(columns={'Player': 'PlayerID'})


def get_5v5_player_season_toi(season, team):
    """
    Gets TOION and TOIOFF by player for given team in given season.

    :param season: int, the season
    :param team: int, team id

    :return: df with game, player, TOION, and TOIOFF
    """
    toi_by_player = get_5v5_player_game_toi(season, team)
    toi_indiv = toi_by_player[['PlayerID', 'TOION', 'TOIOFF']].groupby('PlayerID').sum().reset_index()
    return toi_indiv


def generate_player_toion_toioff(season):
    """
    Generates TOION and TOIOFF at 5v5 for each player in this season.

    :param season: int, the season

    :return: df with columns Player, TOION, TOIOFF, and TOI60.
    """

    team_by_team = []
    allteams = schedules.get_teams_in_season(season)
    for i, team in enumerate(allteams):
        if os.path.exists(teams.get_team_toi_filename(season, team)):
            print('Generating TOI60 for {0:d} {1:s} ({2:d}/{3:d})'.format(
                season, team_info.team_as_str(team), i + 1, len(allteams)))
            toi_indiv = get_5v5_player_season_toi(season, team)
            team_by_team.append(toi_indiv)

    toi60 = pd.concat(team_by_team)
    toi60 = toi60.groupby('PlayerID').sum().reset_index()
    toi60.loc[:, 'TOI%'] = toi60.TOION / (toi60.TOION + toi60.TOIOFF)
    toi60.loc[:, 'TOI60'] = toi60['TOI%'] * 60

    return toi60
