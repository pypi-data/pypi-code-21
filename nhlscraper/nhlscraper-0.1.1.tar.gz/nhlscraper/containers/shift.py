from nhlscrapi.games.toi import ShiftSummary as ShiftSummarpi

from gametime import game_time, period_time

class ShiftSummary:
    def __init__(self, shift_summary: ShiftSummarpi, game):
        self.shift_summary = shift_summary
        self.game = game

        player_name = shift_summary.player_name['first'] + ' ' + shift_summary.player_name['last']
        self.player = game.onice_json_from_scrapi(shift_summary.player_num, [player_name])


    @property
    def shifts(self):
        if not (hasattr(self, '_shifts') and self._shifts):
            self._shifts = [Shift(shift, self) for shift in self.shift_summary.shifts]

        return self._shifts


class Shift:
    def __init__(self, shift: dict, parent_summary: ShiftSummary):
        self.shift = shift
        self.parent_summary = parent_summary
        self.game = game = parent_summary.game

        self.player = parent_summary.player
        # self.state = game._find_state(shift['period'], period_time(shift['end'])) Shifts have no concept of "state" as the NHL defines them
        self.shift_number = shift['shift_num']

        self.start = game_time(shift['period'], shift['start'])
        self.end = game_time(shift['period'], shift['end'])
        self.duration = abs(self.end - self.start)

    @property
    def events(self):
        if not(hasattr(self, '_events') and self._events):
            self._events = [event for event in self.game.scrapi_game.plays
                            if self.start < game_time(event.period, event.time) <= self.end
                            or (self.start == game_time(event.period, event.time) and event.event.event_type_str.upper() == 'FACEOFF')
                            ]

        return self._events
