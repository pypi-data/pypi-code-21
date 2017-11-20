#!/usr/bin/env python
# -*- coding: utf-8 -*-

s = 'bbb'


class Employe(object):
    empCount = 0

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        Employe.empCount += 1

    def displayCount(self):
        print "Total Employee %d" % Employe.empCount

    def displayEmployee(self):
        print "Name : ", self.name + s, ", Salary: ", self.salary
