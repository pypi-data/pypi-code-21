# encoding: utf-8

import timeit
import datetime
import time
import logging_helper
logging = logging_helper.setup_logging()

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'

SECOND = 1
TEN_SECONDS = 10 * SECOND
MINUTE = 60
TEN_MINUTES = 10 * MINUTE
ONE_HOUR = 60 * MINUTE

UTC = datetime.datetime.utcnow()
NOW = datetime.datetime.now()

tz_adjust = (NOW - UTC).seconds


class TimersBase(object):
    @property
    def _now(self):
        """
        Returns a time elapsed value. It's just an elapsed time since the
        timer started rather than a clock value
        :return: seconds since timer started (float)
        """
        return timeit.default_timer()


class Timeout(TimersBase):
    def __init__(self,
                 seconds=0,
                 start_time_offset=0,
                 start_in_an_expired_state=False,
                 ):
        """
        Re-usable timeouts with reporting.
        
        :param seconds:
        :param start_time_offset:
        :param start_in_an_expired_state:
        """
        self.__timeout_length = seconds
        self.__start_time_date = datetime.datetime.now()
        self.__start_time = self._now + start_time_offset

        self.__end_time = self.__start_time
        if not start_in_an_expired_state:
            self.__end_time += self.__timeout_length

        self.__expired = None

    @property
    def expired(self):
        if not self.__expired:
            self.__expired = self._now >= self.__end_time
        return self.__expired

    def expire(self):
        if not self.__expired:
            self.__end_time = self.__start_time
            self.__expired = True

    def restart(self):
        self.__start_time_date = datetime.datetime.now()
        self.__start_time = self._now
        self.__end_time = self.__start_time + self.__timeout_length
        self.__expired = False

    @property
    def elapsed_time(self):
        return self._now - self.__start_time

    @property
    def seconds_remaining(self):
        if self.__expired or self.__timeout_length <= 0:
            logging.debug(u'seconds remaining:{sr}'.format(sr=0))
            return 0

        logging.debug(u'end_time:{et}; reference_timer:{tc}'
                      .format(et=self.__end_time,
                              tc=self._now))

        time_remaining = self.__end_time - self._now

        if time_remaining > self.__timeout_length or time_remaining < 0:
            self.__expired = True
            logging.debug(u'seconds remaining:{sr}'.format(sr=0))
            return 0

        logging.debug(u'seconds remaining:{sr}'.format(sr=time_remaining))
        return time_remaining

    @property
    def time_remaining(self):
        return datetime.timedelta(seconds=self.seconds_remaining)

    def wait(self,
             message=None):

        if message is None:
            while not self.expired:
                wait_time = self.seconds_remaining
                logging.debug(u'wait_time:{wait_time}'.format(wait_time=wait_time))
                time.sleep(wait_time)
        else:
            while not self.expired:
                remaining = self.time_remaining.seconds

                # print rather than log as this gives a live
                # progress to the user for very long intervals
                # but is not relevant in logs.
                print(u'{message} in {minutes}m {seconds}s.'
                      .format(message=message,
                              minutes=remaining / 60,
                              seconds=remaining % 60))

                if remaining > ONE_HOUR:
                    if remaining > ONE_HOUR + TEN_MINUTES:
                        Timeout(ONE_HOUR).wait()
                    else:
                        Timeout(ONE_HOUR - TEN_MINUTES).wait()

                elif remaining > TEN_MINUTES:
                    Timeout(TEN_MINUTES).wait()

                elif remaining > MINUTE:
                    Timeout(MINUTE).wait()

                else:
                    Timeout(TEN_SECONDS
                            if remaining >= TEN_SECONDS
                            else SECOND).wait()

            print (u'Wait finished.')


class Throttle(object):
    def __init__(self,
                 rate=None,
                 interval=None):
        """
        Perpetually restarting timer
        Example use is to limit the number of requests per second to a service

        :param rate: allowed events per second
        :param period: time in seconds before next event is permitted
        """
        if rate:
            try:
                self.interval = 1.0 / rate
            except ZeroDivisionError:
                self.interval = 0
        else:
            self.interval = interval
        # logging.debug(u'Throttle interval:{interval}'
        #               .format(interval=interval))

        self.timeout = Timeout(seconds=self.interval)

    def wait(self,
             message=None):
        self.timeout.wait(message=message)
        self.timeout.restart()


class Stopwatch(TimersBase):
    def __init__(self):
        self.reset()

    def reset(self):
        self.__stop_time = None
        self.__laps = []
        self.__start_time = self._now

    def stop(self):
        if self.__stop_time is None:
            self.__stop_time = self._now
            return self.glance
        else:
            return self.__stop_time

    def lap(self):
        lap_end_time = self._now
        lap_start_time = (self.__start_time
                          if not self.__laps
                          else self.__laps[-1][u'lap_end_time'])
        self.__laps.append({
            u'lap_start_time': lap_start_time,
            u'lap_end_time':   lap_end_time,
            u'lap_time':       lap_end_time - lap_start_time
        })
        return self.__laps[-1][u'lap_time']

    @property
    def lap_times(self):
        return self.__laps

    @property
    def glance(self):
        if self.__stop_time:
            return self.__stop_time - self.__start_time
        else:
            return self._now - self.__start_time
