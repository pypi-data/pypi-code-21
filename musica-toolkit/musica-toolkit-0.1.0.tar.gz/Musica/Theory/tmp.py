####################################################################################################

class MainInterval:

    ##############################################

    def __init__(self,
                 number_of_semitones,
                 name, short,
                 altered_name, altered_short,
                 frequency_ratio,
                 alternative_names=None, alternative_short=None,
    ):

        self._number_of_semitones = number_of_semitones
        self._name = name
        self._short = short
        self._altered_name = altered_name
        self._altered_short = altered_short
        self._frequency_ratio = frequency_ratio
        self._alternative_names = alternative_names
        self._alternative_short = alternative_short

        if short is not None:
            self._quality = short[0]
            self._degree = int(short[1])
        else:
            self._quality = None
            self._degree = None

    ##############################################

    @property
    def number_of_semitones(self):
        return self._number_of_semitones

    @property
    def name(self):
        return self._name

    @property
    def short(self):
        return self._short

    @property
    def quality(self):
        return self._quality

    @property
    def degree(self):
        return self._degree

    @property
    def is_unisson(self):
        return self.number_of_semitones == 0

    @property
    def is_perfect(self):
        return self._quality == 'P'

    @property
    def is_minor(self):
        return self._quality == 'm'

    @property
    def is_major(self):
        return self._quality == 'M'

    @property
    def is_diminished(self):
        return self._quality == 'd'

    @property
    def is_augmented(self):
        return self._quality == 'A'

    ##############################################

    def __repr__(self):
        return self._name

    ##############################################

    def __int__(self):
        return self._number_of_semitones

    def __lt__(self, other):
        return self._number_of_semitones < int(other)

####################################################################################################

class MainIntervals:

    __main_intervals__ = sorted((
        MainInterval(
            number_of_semitones=0,
            name='perfect unison', # prime unison
            short='P1',
            altered_name='diminished second',
            altered_short='d2',
            frequency_ratio='1:1',
        ),
        MainInterval(
            number_of_semitones=1,
            name='minor second', # seconde
            short='m2',
            altered_name='augmented unison',
            altered_short='A1',
            alternative_names=('semitone', 'half tone', 'half step'),
            alternative_short='S',
            frequency_ratio='16:15',
        ),
        MainInterval(
            number_of_semitones=2,
            name='major second',
            short='M2',
            altered_name='diminished third',
            altered_short='d3',
            alternative_names=('tone', 'whole tone', 'whole step'),
            alternative_short='S',
            frequency_ratio='9:8',
        ),
        MainInterval(
            number_of_semitones=3,
            name='minor third', # tierce
            short='m3',
            altered_name='augmented second',
            altered_short='A2',
            frequency_ratio='6:5',
        ),
        MainInterval(
            number_of_semitones=4,
            name='major third',
            short='M3',
            altered_name='diminished fourth',
            altered_short='d4',
            frequency_ratio='5:4',
        ),
        MainInterval(
            number_of_semitones=5,
            name='perfect fourth', # quarte
            short='P4',
            altered_name='augmented third',
            altered_short='A3',
            frequency_ratio='4:3',
        ),
        MainInterval(
            number_of_semitones=6,
            name=None,
            short=None,
            altered_name=('diminished fifth', 'augmented fourth'),
            altered_short=('d5', 'A4'),
            alternative_names='tritone',
            alternative_short='TT',
            frequency_ratio='',
        ),
        MainInterval(
            number_of_semitones=7,
            name='perfect fifth', # quinte
            short='P5',
            altered_name='diminished sixth',
            altered_short='d6',
            frequency_ratio='3:2',
        ),
        MainInterval(
            number_of_semitones=8,
            name='minor sixth', # sixte
            short='m6',
            altered_name='augmented fifth',
            altered_short='A5',
            frequency_ratio='8:5',
        ),
        MainInterval(
            number_of_semitones=9,
            name='major sixth',
            short='M6',
            altered_name='diminished seventh',
            altered_short='d7',
            frequency_ratio='5:3',
        ),
        MainInterval(
            number_of_semitones=10,
            name='minor seventh', # septième
            short='m7',
            altered_name='augmented sixth',
            altered_short='A6',
            frequency_ratio='16:9',
        ),
        MainInterval(
            number_of_semitones=11,
            name='major seventh',
            short='M7',
            altered_name='diminished octave',
            altered_short='d8',
            frequency_ratio='15:8',
        ),
        MainInterval(
            number_of_semitones=12,
            name='perfect octave',
            short='P8',
            altered_name='augmented seventh',
            altered_short='A7',
            frequency_ratio='2:1',
        ),


    ))

    __degree_to_interval__ = [None]
    for interval in __main_intervals__:
        if interval.degree is not None:
            if len(__degree_to_interval__) < interval.degree +1:
                __degree_to_interval__.append([interval])
            else:
                __degree_to_interval__[interval.degree].append(interval)

    ##############################################

    @classmethod
    def intervals_for_degree(cls, degree):
        return cls.__degree_to_interval__[degree]
