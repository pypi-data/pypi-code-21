#!/usr/bin/env python
# -*- coding: utf-8 -*-

RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
EXCHANGE_DCU = 'Pilatus_data'
QUEUE_DCU = 'Pilatus_data'
EXCHANGE_SCAN = 'Pilatus_scans'
WATCHDOG_SLEEP = 0.001  # 10 msec
WAIT_TIME = 1  # sec
WAIT_REPEAT = 10
HTIME_TOLERANCE = 3  # sec
STAMP_TIMETOLIVE = 60 * 60 * 25  # one day
