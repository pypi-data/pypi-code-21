from pubapi_library.playerdata.games import DailyGames, MonthlyArchives
from pytest import fixture

from pubapi_library.playerdata.profile import Player


class TestProfile:
    @fixture
    def player_profile_keys(self):
        return ['@id', 'username', 'player_id', 'name', 'avatar', 'location',
                'country', 'joined', 'last_online', 'followers', 'status']

    def test_player_details(self, player_profile_keys):
        player_profile_instance = Player('walidmujahid')
        response = player_profile_instance.player_details()

        assert isinstance(response, dict)
        assert response['username'] == 'walidmujahid', "The username should" \
                                                       " be in the response"
        assert set(player_profile_keys).issubset(response.keys()), "All keys " \
                                                                   "should " \
                                                                   "be in " \
                                                                   "the " \
                                                                   "response."

    def test_player_id(self):
        player_profile_instance = Player('walidmujahid')
        id_ = player_profile_instance.id()

        assert id_ == "https://api.chess.com/pub/player/walidmujahid"

    def test_player_username(self):
        player_profile_instance = Player('walidmujahid')
        username = player_profile_instance.username()

        assert username == 'walidmujahid'

    def test_key_player_id(self):
        player_profile_instance = Player('walidmujahid')
        player_id = player_profile_instance.player_id()

        assert player_id == 5444274

    def test_player_name(self):
        player_profile_instance = Player('walidmujahid')
        name = player_profile_instance.name()

        assert name == "Walid Mujahid – وليد مجاهد – (CoT OTB)"

    def test_player_avatar(self):
        player_profile_instance = Player('walidmujahid')
        avatar = player_profile_instance.avatar()

        assert avatar == "https://images.chesscomfiles.com/uploads/v1/user/" \
                         "5444274.50d977ec.200x200o.eb5cddcca27e.jpeg"

    def test_player_location(self):
        player_profile_instance = Player('walidmujahid')
        location = player_profile_instance.location()

        assert location == "Fort Myers, Florida"

    def test_player_country(self):
        player_profile_instance = Player('walidmujahid')
        country = player_profile_instance.country()

        assert country == "https://api.chess.com/pub/country/XX"

    def test_player_joined(self):
        player_profile_instance = Player('walidmujahid')
        joined = player_profile_instance.joined()

        assert joined == 1310740631

    def test_player_last_online(self):
        player_profile_instance = Player('walidmujahid')
        last_online = player_profile_instance.last_online()

        assert last_online == last_online

    def test_player_followers(self):
        player_profile_instance = Player('walidmujahid')
        followers = player_profile_instance.followers()

        assert followers == followers

    def test_player_status(self):
        player_profile_instance = Player('walidmujahid')
        status = player_profile_instance.status()

        assert status == 'basic'


class TestDailyGames:
    @fixture
    def current_daily_games_keys(self):
        return ['white', 'black', 'url', 'fen', 'turn', 'move_by', 'start_time',
                'time_class', 'rules']

    @fixture
    def to_move_daily_games_keys(self):
        return ['url', 'move_by', 'last_activity']

    def test_current_daily_games(self, current_daily_games_keys):
        daily_games = DailyGames('walidmujahid')

        assert isinstance(daily_games.current_daily_games(), list)

        for game in daily_games.current_daily_games():
            assert isinstance(game, dict)
            assert game['white'] or game['black'] == Player('walidmujahid'
                                                            ).id(), "This" \
                                                                    "username" \
                                                                    "should" \
                                                                    "be " \
                                                                    "either " \
                                                                    "white " \
                                                                    "or black."
            assert set(current_daily_games_keys
                       ).issubset(game.keys()), "All keys should be in the " \
                                                "game."

    def test_to_move_daily_games(self, to_move_daily_games_keys):
        daily_games = DailyGames('walidmujahid')

        assert isinstance(daily_games.to_move_daily_games(), list)

        for game in daily_games.to_move_daily_games():
            assert isinstance(game, dict)
            assert set(to_move_daily_games_keys
                       ).issubset(game.keys()), "All keys should be in the " \
                                                "game."


class TestMonthlyArchives:
    @fixture
    def monthly_archive_keys(self):
        return ['url', 'pgn', 'time_control', 'end_time', 'fen',
                'time_class', 'rules', 'white', 'black']

    def test_games_in_archive(self, monthly_archive_keys):
        monthly_archives = MonthlyArchives('walidmujahid', 2017, 9)

        assert isinstance(monthly_archives.games_in_archive(), list)

        for game in monthly_archives.games_in_archive():
            assert isinstance(game, dict)

            if not game['time_class'] == 'daily':
                assert set(monthly_archive_keys
                           ).issubset(game.keys()), "All keys should be " \
                                                    "in the game."
            else:
                assert set(monthly_archive_keys + ['start_time']
                           ).issubset(game.keys()), "All keys should be " \
                                                    "in the game."

    def test_list_of_games_played_against(self):
        monthly_archives = MonthlyArchives('walidmujahid', 2017, 9,
                                           opponent_username='renobezzina')

        assert isinstance(
            monthly_archives.list_of_games_played_against(),
            list)

        for game in monthly_archives.list_of_games_played_against():
            assert isinstance(game, dict)
