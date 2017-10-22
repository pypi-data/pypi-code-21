from datetime import datetime
import os
"""Birthday App."""


class App():

    def __init__(self):
        self.sort_keys = ['month']

    # HELPERS #####

    def add_leading_zero(self, number):
        if number < 10:
            number = '0' + str(number)
        return str(number)

    def today(self):
        current_day = self.add_leading_zero(datetime.now().day)
        current_month = str(datetime.now().month)
        return int(current_month + current_day)

    # def textual_month(self, month_int):
    #     # TODO add exception "out of range"
    #     months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    #               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    #     return months[month_int]
    #
    # def textual_date(self, day_int, month_int):
    #     return str(day_int) + '.' + self.textual_month(month_int)

    def last_date_in_year(self, lines):
        max_val = max(lines, key=lambda x: int(x[1] + x[0]))
        return int(max_val[1] + max_val[0])

    def first_bday_in_year(self, lines):
        return min(lines, key=lambda x: int(x[1] + x[0]))

    def strings_to_lists(self, textfile):
        return [line.rstrip().split() for line in textfile]

    def remove_empty_lists(self, lines):
        return [line for line in lines if line]

    # CONSISTENCY CHECK OF TXT FILE #####

    def file_is_consistent(self, textfile):
        # TODO check if file is consistent using REGEX
        return 1

    # COMMAND 'SORT' #####

    def sort_by_day(self, lines, reverse):
        pass

    def sort_by_month(self, lines, reverse):
        return sorted(lines, key=lambda x: int(x[1] + x[0]), reverse=reverse)

    def sort_by_year(self, lines, reverse):
        pass

    def sort_by_forename(self, lines, reverse):
        pass

    def sort_by_surname(self, lines, reverse):
        pass

    def sort_lines(self, lines, sort_key):
        """Sort lines in bdays.txt by
        forename, surname, date or month.
        """
        lines = self.remove_empty_lists(lines)
        sort_keys = {
            'day': self.sort_by_day,
            'month': self.sort_by_month,
            'year': self.sort_by_year,
            'forename': self.sort_by_forename,
            'surname': self.sort_by_surname
        }
        return sort_keys.get(sort_key, 'month')(lines, 0)

    # COMMAND 'UPCOMING' #####

    def bdays_left(self, lines):
        today = self.today()
        for i in lines:
            i_date = int(i[1] + i[0])
            if i_date >= today:
                yield i

    def next_bdays(self, lines):
        next_bday = min(lines, key=lambda x: int(x[1] + x[0]))
        next_bday = int(next_bday[1] + next_bday[0])
        for i in lines:
            if int(i[1] + i[0]) == next_bday:
                yield i

    def textual_date(self, day_int, month_int):
        # TODO add exception "out of range"
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return day_int.decode('utf-8') + '.' + months[int(month_int) - 1]

    def pretty_text(self, lines):
        names = [i[3].decode('utf-8') + ' ' + i[4]
                 [:1].decode('utf-8') + '.' for i in lines]
        bday = int(lines[0][1] + lines[0][0])

        if bday - self.today() == 0:
            return ', '.join(names) + ' TODAY!'
        else:
            return ', '.join(names) + ', ' + \
                self.textual_date(lines[0][0], lines[0][1])

    def upcoming(self, lines):
        bdays_left = list(self.bdays_left(lines))
        if bdays_left:
            return self.pretty_text(list(self.next_bdays(bdays_left)))
        else:
            return self.pretty_text(list(self.next_bdays(lines)))
