from datetime import date
from dateutil.parser import parse

from amaascore.assets.real_asset import RealAsset
from amaascore.assets.enums import *


class Automobile(RealAsset):

    def __init__(self, asset_manager_id, asset_id, client_id, asset_issuer_id=None,
                 country_id=None, display_name='', description='',
                 venue_id=None, issue_date=None, maturity_date=date.max, comments=None,
                 links=None, references=None, additional=None, currency=None,
                 asset_status='Active', model_year=None,
                 vehicle_id=None, make=None, model=None, color=None,
                 style=None, genre=None, rarity=None,
                 condition=None, imported=None, imported_country_id=None,
                 engine_id=None, chassis_id=None, steering=None, gearbox=None, gears=None,
                 drive=None, engine_cap=None, power=None, weight=None,
                 speed=None, fuel_type=None, petrol_grade=None, *args, **kwargs):
        super(Automobile, self).__init__(asset_manager_id=asset_manager_id,
                                         asset_id=asset_id, client_id=client_id,
                                         asset_issuer_id=asset_issuer_id, asset_status=asset_status,
                                         display_name=display_name,
                                         description=description, country_id=country_id,
                                         venue_id=venue_id, issue_date=issue_date,
                                         currency=currency, maturity_date=maturity_date,
                                         comments=comments, links=links, references=references,
                                         additional=additional,
                                         *args, **kwargs)
        self.model_year = model_year
        self.vehicle_id = vehicle_id
        self.make = make
        self.model = model
        self.color = color
        self.style = style
        self.genre = genre
        self.rarity = rarity
        self.condition = condition
        self.imported = imported
        self.imported_country_id = imported_country_id
        self.engine_id = engine_id
        self.chassis_id = chassis_id
        self.steering = steering
        self.gearbox = gearbox
        self.gears = gears
        self.drive = drive
        self.engine_cap = engine_cap
        self.power = power
        self.weight = weight
        self.speed = speed
        self.fuel_type = fuel_type
        self.petrol_grade = petrol_grade

    @property
    def model_year(self):
        return self._model_year

    @model_year.setter
    def model_year(self, model_year):
        if isinstance(model_year, str):
            model_year = int(model_year)
        self._model_year = model_year

    @property
    def make(self):
        return self._make

    @make.setter
    def make(self, make):
        if not make:
            self._make = None
        elif make in CAR_MAKE_RECORD:
            self._make = make
        else:
            raise ValueError("Invalid input for car make: %s" % make)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        if not color:
            self._color = None
        elif color in CAR_COLOR_RECORD:
            self._color = color
        else:
            raise ValueError("Invalid input for car color: %s" % color)

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, style):
        if not style:
            self._style = None
        elif style in set(CAR_STYLE.keys()):
            self._style = style
        elif style in set(CAR_STYLE.values()):
            self._style = list(CAR_STYLE.keys())[list(CAR_STYLE.values()).index(style)]
        else:
            raise ValueError("Invalid input for car style: %s" % style)

    @property
    def genre(self):
        return self._genre

    @genre.setter
    def genre(self, genre):
        if not genre:
            self._genre = None
        elif genre in set(CAR_GENRE.keys()):
            self._genre = genre
        elif genre in set(CAR_GENRE.values()):
            self._genre = list(CAR_GENRE.keys())[list(CAR_GENRE.values()).index(genre)]
        else:
            raise ValueError("Invalid input for car genre: %s" % genre)

    @property
    def rarity(self):
        return self._rarity

    @rarity.setter
    def rarity(self, rarity):
        if not rarity:
            self._rarity = None
        elif rarity in CAR_RARITY:
            self._rarity = rarity
        else:
            raise ValueError("Invalid input for car rarity: %s" % rarity)

    @property
    def condition(self):
        return self._condition

    @condition.setter
    def condition(self, condition):
        if not condition:
            self._condition = None
        elif condition in set(CAR_CONDITION.keys()):
            self._condition = condition
        elif condition in set(CAR_CONDITION.values()):
            self._condition = list(CAR_CONDITION.keys())[list(CAR_CONDITION.values()).index(condition)]
        else:
            raise ValueError("Invalid input for car condition: %s" % condition)

    @property
    def imported(self):
        return self._imported

    @imported.setter
    def imported(self, imported):
        if not imported:
            self._imported = None
        else:
            if imported not in [True, False]:
                raise ValueError("imported should be True or False: %s" % imported)
            self._imported = imported

    @property
    def steering(self):
        return self._steering

    @steering.setter
    def steering(self, steering):
        if not steering:
            self._steering = None
        else:
            if steering not in ['LHD', 'RHD']:
                raise ValueError("Invalid steering LHD/RHD: %s" % steering)
            self._steering = steering

    @property
    def gearbox(self):
        return self._gearbox

    @gearbox.setter
    def gearbox(self, gearbox):
        if not gearbox:
            self._gearbox = None
        else:
            if gearbox not in ['A', 'M']:
                raise ValueError("Invalid gearbox A/M: %s" % gearbox)
            self._gearbox = gearbox

    @property
    def drive(self):
        return self._drive

    @drive.setter
    def drive(self, drive):
        if not drive:
            self._drive = None
        else:
            if drive not in ['RWD', 'FWD', 'AWD']:
                raise ValueError("Invalid drive RWD/FWD/AWD: %s" % drive)
            self._drive = drive

    @property
    def fuel_type(self):
        return self._fuel_type

    @fuel_type.setter
    def fuel_type(self, fuel_type):
        if not fuel_type:
            self._fuel_type = None
        else:
            if fuel_type not in ['Petrol', 'Diesel']:
                raise ValueError("Invalid fuel_type Petrol/Diesel: %s" % fuel_type)
            self._fuel_type = fuel_type

    @property
    def petrol_grade(self):
        return self._petrol_grade

    @petrol_grade.setter
    def petrol_grade(self, petrol_grade):
        if not petrol_grade:
            self._petrol_grade = None
        else:
            if isinstance(petrol_grade, str):
                petrol_grade = int(float(petrol_grade))
            if petrol_grade in set(CAR_PETROL_GRADE.keys()):
                self._petrol_grade = CAR_PETROL_GRADE[petrol_grade]
            else:
                raise ValueError("Invalid data type for petrol_grade (87~94): %s" % petrol_grade)
