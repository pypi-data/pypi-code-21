from Tkinter import *


def countTwoDates():
    def start_end_day(dateStart='2000.01.01', dateEnd="2008.09.06"):
        dateStartList = dateStart.split('.')
        yearStart = int(dateStartList[0])
        monthStart = int(dateStartList[1])
        dayStart = int(dateStartList[2])
        dateEndList = dateEnd.split('.')
        yearEnd = int(dateEndList[0])
        monthEnd = int(dateEndList[1])
        dayEnd = int(dateEndList[2])
        print 'start:', yearStart, monthStart, dayStart
        print 'end:', yearEnd, monthEnd, dayEnd
        return yearStart, monthStart, dayStart, yearEnd, monthEnd, dayEnd

    def is_365_or_366(year):
        flag_365_366 = 0
        if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
            flag_365_366 = 1
        return flag_365_366 + 365

    def countMonthDays(year, month):
        flag_365_366 = is_365_or_366(year)
        if flag_365_366 == 365:
            if month == 1:
                days = 0
            elif month == 2:
                days = 31
            elif month == 3:
                days = 31 + 28
            elif month == 4:
                days = 31 + 28 + 31
            elif month == 5:
                days = 31 + 28 + 31 + 30
            elif month == 6:
                days = 31 + 28 + 31 + 30 + 31
            elif month == 7:
                days = 31 + 28 + 31 + 30 + 31 + 30
            elif month == 8:
                days = 31 + 28 + 31 + 30 + 31 + 30 + 31
            elif month == 9:
                days = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31
            elif month == 10:
                days = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30
            elif month == 11:
                days = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31
            elif month == 12:
                days = 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30
        elif flag_365_366 == 366:
            if month == 1:
                days = 0
            elif month == 2:
                days = 31
            elif month == 3:
                days = 31 + 29
            elif month == 4:
                days = 31 + 29 + 31
            elif month == 5:
                days = 31 + 29 + 31 + 30
            elif month == 6:
                days = 31 + 29 + 31 + 30 + 31
            elif month == 7:
                days = 31 + 29 + 31 + 30 + 31 + 30
            elif month == 8:
                days = 31 + 29 + 31 + 30 + 31 + 30 + 31
            elif month == 9:
                days = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31
            elif month == 10:
                days = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31 + 30
            elif month == 11:
                days = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31
            elif month == 12:
                days = 31 + 29 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30
        return days

    def countYearDays(year):
        days = 0
        years = range(1, year)
        for year_item in years:
            days += is_365_or_366(year_item)
        return days

    def countIt():
        start = start_var.get()
        end = end_var.get()
        yearStart, monthStart, dayStart, yearEnd, monthEnd, dayEnd = start_end_day(start, end)

        if yearEnd == yearStart:
            if monthEnd == monthStart:
                days = abs(dayEnd - dayStart)
            else:
                days = countMonthDays(yearEnd, monthEnd) + dayEnd - countMonthDays(yearStart, monthStart) - dayStart
        else:
            days = countYearDays(yearEnd) + countMonthDays(yearEnd, monthEnd) + dayEnd - countYearDays(
                yearStart) - countMonthDays(
                yearStart, monthStart) - dayStart
        result_var.set(abs(days))
        return abs(days)

    lable_width = 10
    entry_width = 20
    button_width = lable_width + entry_width
    root = Tk()
    root.title('count days!')
    info = Label(root, text="Hello, world!", width=button_width)
    info.grid(row=0, column=0, columnspan=2)
    start_info = Label(root, text="date start:", width=lable_width)
    start_info.grid(row=1, column=0)
    start_var = StringVar()
    start_var.set('2017.07.03')
    start_Entry = Entry(root, width=entry_width, textvariable=start_var)
    start_Entry.grid(row=1, column=1)
    end_info = Label(root, text="date end:", width=lable_width)
    end_info.grid(row=2, column=0)
    end_var = StringVar()
    end_var.set('2019.06.05')
    end_Entry = Entry(root, width=entry_width, textvariable=end_var)
    end_Entry.grid(row=2, column=1)

    submit_button = Button(text='count days', command=countIt, width=button_width)
    submit_button.grid(row=3, column=0, columnspan=2)
    res_info = Label(root, text="total days:", width=lable_width)
    res_info.grid(row=4, column=0)
    result_var = StringVar()
    result_Entry = Entry(root, width=entry_width, textvariable=result_var, state='disabled')
    result_Entry.grid(row=4, column=1)

    root.mainloop()
    return 0


if __name__ == '__main__':
    countTwoDates()
