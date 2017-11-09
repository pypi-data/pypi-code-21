import datetime
import pytz
import execjs

class DateJS():
    def __init__(self, JS_STRING, y=0, m=0, d=0, h=0, minute=0, s=0, ms=0, tzo=0):
        self.YEAR = y
        self.MONTH = m + 1
        self.DATE = d
        self.HOUR = h
        self.MINUTE = minute
        self.SECOND = s
        self.MILLISECONDS = ms
        self.OFFSET = int(tzo)
        self.TZ = None
        self.TZ_SIMPLE = None
        self.TZ_CUSTOM = None
        self.JS_TIME = JS_STRING
        self.PYTIME = datetime.datetime.now()
        self.PYTIME_SIMPLE = datetime.datetime.now()
        self.PYTIME_CUSTOM = datetime.datetime.now()
        self.CUSTOM_TIMEZONES = []
        self.ctx = None
        if self.YEAR == 0:
            self.setCTX()
        self.setAllValues()

    def setCTX(self):
        self.ctx = execjs.compile("""
                function y(x){
                    return new Date(x).getFullYear();
                }
                function m(x){
                    return new Date(x).getMonth();
                }
                function d(x){
                    return new Date(x).getDate();
                }
                function h(x){
                    return new Date(x).getHours();
                }
                function i(x){
                    return new Date(x).getMinutes();
                }
                function s(x){
                    return new Date(x).getSeconds();
                }
                function l(x){
                    return new Date(x).getMilliseconds();
                }
                function t(x){
                    return new Date(x).getTimezoneOffset();
                }
            """)

    def setAllValues(self):
        if not self.ctx == None:
            self.setYear()
            self.setMonth()
            self.setDate()
            self.setHour()
            self.setMinute()
            self.setSecond()
            self.setMillisecond()
        self.setTZ()

    def getTime(self):
        self.PYTIME = self.PYTIME.replace(year=self.YEAR, month=self.MONTH, day=self.DATE, hour=self.HOUR, minute=self.MINUTE, second=self.SECOND, microsecond=self.MILLISECONDS, tzinfo=pytz.timezone(self.TZ))
        return self.PYTIME

    def getSimpleTime(self):
        self.PYTIME_SIMPLE = self.PYTIME_SIMPLE.replace(year=self.YEAR, month=self.MONTH, day=self.DATE, hour=self.HOUR, minute=self.MINUTE, second=self.SECOND, microsecond=self.MILLISECONDS, tzinfo=pytz.timezone(self.TZ_SIMPLE))
        return self.PYTIME_SIMPLE

    def getCustomTime(self):
        self.PYTIME_CUSTOM = self.PYTIME_CUSTOM.replace(year=self.YEAR, month=self.MONTH, day=self.DATE, hour=self.HOUR, minute=self.MINUTE, second=self.SECOND, microsecond=self.MILLISECONDS, tzinfo=pytz.timezone(self.TZ_CUSTOM))
        return self.PYTIME_CUSTOM

    def getYear(self):
        return self.YEAR

    def setYear(self):
        self.YEAR = self.ctx.call("y", self.JS_TIME)
        return

    def getMonth(self):
        return self.MONTH

    def setMonth(self):
        self.MONTH = self.ctx.call("m", self.JS_TIME) + 1 # This +1 moves month numbers from 0-11 to 1-12
        return

    def getDate(self):
        return self.DATE

    def setDate(self):
        self.DATE = self.ctx.call("d", self.JS_TIME)
        return

    def getHours(self):
        return self.HOUR

    def setHour(self):
        self.HOUR = self.ctx.call("h", self.JS_TIME)
        return

    def getMinutes(self):
        return self.MINUTE

    def setMinute(self):
        self.MINUTE = self.ctx.call("i", self.JS_TIME)
        return

    def getSeconds(self):
        return self.SECOND

    def setSecond(self):
        self.SECOND = self.ctx.call("s", self.JS_TIME)
        return

    def getMilliseconds(self):
        return self.MILLISECONDS

    def setMillisecond(self):
        self.MILLISECONDS = self.ctx.call("l", self.JS_TIME)
        return

    def getTimezone(self):
        return self.TZ

    def getSimpleTimezone(self):
        return self.TZ_SIMPLE

    def getCustomTimezone(self):
        return self.TZ_CUSTOM

    def setTZ(self):
        if not self.ctx == None:
            self.OFFSET = self.ctx.call("t", self.JS_TIME)
        self.OFFSET = self.offsetFormat()
        sorted_tzs = self.allTimezones()
        for zone in sorted_tzs:
            if self.OFFSET in zone[1]:
                self.TZ = zone[0]
                break
        simple_tzs = self.basicTimezones()
        for z in simple_tzs:
            if self.OFFSET in z[1]:
                self.TZ_SIMPLE = z[0]
                break
        custom_tzs = self.CUSTOM_TIMEZONES
        if custom_tzs == []:
            return
        for w in custom_tzs:
            if self.OFFSET in w[1]:
                self.TZ_CUSTOM = w[0]
                return
        raise Exception("No Timezone Found!")

    def offsetFormat(self):
        west = True
        if int(self.OFFSET) < 0:
            west = False
        hours_offset = int(self.OFFSET/60)
        if abs(hours_offset) < 10:
            hours_offset = "0" + str(hours_offset)
        minutes_offset = int(self.OFFSET%60)
        if minutes_offset < 10:
            minutes_offset = "0" + str(minutes_offset)
        if west:
            return "-" + str(hours_offset) + str(minutes_offset)
        return str(hours_offset) + str(minutes_offset)

    def allTimezones(self):
        tz = [(item, datetime.datetime.now(pytz.timezone(item)).strftime('%z') + " " + item) for item in pytz.common_timezones]
        sorted_tzs = sorted(tz, key=lambda x: int(x[1].split()[0]))
        return sorted_tzs

    def basicTimezones(self):
        SHORT_LIST_TIMEZONES = ['Pacific/Midway', 'US/Hawaii', 'Pacific/Marquesas', 'Pacific/Gambier', 'US/Alaska', 'US/Pacific', 'US/Mountain', 'US/Central', 'US/Eastern', 'America/Argentina/Buenos_Aires',  'Canada/Newfoundland', 'America/Sao_Paulo', 'Atlantic/Cape_Verde', 'UTC', 'Europe/London', 'Europe/Paris', 'Europe/Moscow', 'Asia/Tehran', 'Asia/Dubai', 'Asia/Kabul', 'Asia/Karachi', 'Asia/Kolkata', 'Asia/Kathmandu', 'Asia/Dhaka', 'Indian/Cocos', '+0630 Indian/Cocos', 'Asia/Bangkok', 'Asia/Hong_Kong', 'Asia/Pyongyang', 'Australia/Eucla', 'Asia/Tokyo', 'Australia/Darwin', 'Australia/Brisbane', 'Australia/Adelaide', 'Australia/Sydney', 'Pacific/Fiji', 'Pacific/Auckland', 'Pacific/Chatham', 'Pacific/Kiritimati']
        tz = [(item, datetime.datetime.now(pytz.timezone(item)).strftime('%z') + " " + item) for item in pytz.common_timezones if item in SHORT_LIST_TIMEZONES]
        sorted_tzs = sorted(tz, key=lambda x: int(x[1].split()[0]))
        return sorted_tzs

    def setcustomTimezones(self, CUSTOM_LIST):
        tz = [(item, datetime.datetime.now(pytz.timezone(item)).strftime('%z') + " " + item) for item in pytz.common_timezones if item in CUSTOM_LIST]
        sorted_tzs = sorted(tz, key=lambda x: int(x[1].split()[0]))
        self.TZ_CUSTOM = sorted_tzs
        return
