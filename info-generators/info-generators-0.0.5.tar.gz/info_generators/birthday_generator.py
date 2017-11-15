from gabc_generator import Generator
import random


class BirthdayGenerator(Generator):
    @staticmethod
    def get():
        consts_months = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')
        consts_days = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
                       '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28',
                       '29', '30')
        return '19{}{}{}'.format(random.randrange(80, 95),
                                 random.choice(consts_months),
                                 random.choice(consts_days))
