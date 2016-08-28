#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Arkadiusz Młynarczyk
#
# This file is part of SurveyDataConverter
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


class DataLine(object):
    class Type:
        SHOT = 1
        SPLAY = 2
        DUPLICATED_SHOT = 3

    def __init__(self):
        super(DataLine, self).__init__()
        self.fromSt = ""
        self.toSt = ""
        self.clino = 0
        self.compass = 0
        self.tape = 0
        self.comment = ""
        self.type = 0
        self.type = DataLine.Type.SHOT

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.fromSt == other.fromSt and self.toSt == other.toSt


class Trip(object):
    def __init__(self):
        super(Trip, self).__init__()
        self.data = []
        self.comment = ""
        self.date = None
        self.name = ""
        self.declination = 0
        self.splays_count = 0
        self.shots_count = 0

    @property
    def last_dataline(self):
        if len(self.data):
            return self.data[-1]
        return Trip()


class Survey(object):
    def __init__(self):
        # type: () -> object
        super(Survey, self).__init__()
        self.name = ""
        self.trips = []
