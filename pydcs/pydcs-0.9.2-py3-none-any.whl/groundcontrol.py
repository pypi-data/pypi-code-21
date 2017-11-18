class GroundControl:
    def __init__(self):
        self.pilot_can_control_vehicles = False
        self.red_game_masters = 0
        self.red_tactical_commander = 0
        self.red_jtac = 0
        self.red_observer = 0

        self.blue_game_masters = 0
        self.blue_tactical_commander = 0
        self.blue_jtac = 0
        self.blue_observer = 0

    def load_from_dict(self, d):
        if d is None:
            return
        self.pilot_can_control_vehicles = d["isPilotControlVehicles"]

        self.red_game_masters = int(d["roles"]["instructor"]["red"])
        self.red_tactical_commander = int(d["roles"]["artillery_commander"]["red"])
        self.red_jtac = int(d["roles"]["forward_observer"]["red"])
        self.red_observer = int(d["roles"]["observer"]["red"])

        self.blue_game_masters = int(d["roles"]["instructor"]["blue"])
        self.blue_tactical_commander = int(d["roles"]["artillery_commander"]["blue"])
        self.blue_jtac = int(d["roles"]["forward_observer"]["blue"])
        self.blue_observer = int(d["roles"]["observer"]["blue"])

    def dict(self):
        return {
            "isPilotControlVehicles": self.pilot_can_control_vehicles,
            "roles": {
                "instructor": {"red": self.red_game_masters, "blue": self.blue_game_masters},
                "artillery_commander": {"red": self.red_tactical_commander, "blue": self.blue_tactical_commander},
                "forward_observer": {"red": self.red_jtac, "blue": self.blue_jtac},
                "observer": {"red": self.red_observer, "blue": self.blue_observer},
            }
        }
