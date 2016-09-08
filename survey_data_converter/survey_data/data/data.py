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

import math


class DataLine(object):
    class Type:
        SHOT = 1
        SPLAY = 2
        DUPLICATED_SHOT = 3
        SPLIT = 4

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
        self.roll = -1
        self.calculated = False
        self.calculated_comment = ""

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

    def preprocess_data(self):
        self.__find_duplicates()
        self.__calculate_count()

    def show_rolls(self):
        for data_line in self.data:
            if data_line.roll >= 0:
                data_line.comment += " Roll: %.1f " % data_line.roll
                data_line.comment = data_line.comment.strip()

    def move_splays_to_end(self):
        shots = []
        splays = []

        for data_line in self.data:
            if data_line.type == DataLine.Type.SPLAY:
                splays.append(data_line)
            else:
                shots.append(data_line)

        self.data = shots
        if len(splays):
            split_data = DataLine()
            split_data.type = DataLine.Type.SPLIT
            self.data.append(split_data)
            self.data = self.data + splays

    def __write_duplicated_shot(self, new_data):
        if len(self.__tape) > 1:
            calculated_tape = sum(self.__tape) / len(self.__tape)
            calculated_clino = sum(self.__clino) / len(self.__clino)
            x = 0
            y = 0
            for angle in self.__compass:
                x += math.cos(math.radians(angle))
                y += math.sin(math.radians(angle))
            calculated_compass = math.degrees(math.atan2(y, x)) % 360
            if calculated_compass == 360: calculated_compass = 0
            if calculated_tape != 0:
                new_data_line = DataLine()
                new_data_line.clino = calculated_clino
                new_data_line.fromSt = self.__previous_data.fromSt
                new_data_line.toSt = self.__previous_data.toSt
                new_data_line.compass = calculated_compass
                new_data_line.tape = calculated_tape
                new_data_line.type = DataLine.Type.SHOT
                new_data_line.comment = "Calculated from %d shots" % len(self.__tape)
                new_data_line.calculated_comment = (" ".join(self.__comments)).strip()
                new_data_line.calculated = True
                new_data.append(new_data_line)
        elif len(new_data) > 0:
            new_data_line = new_data[-1]
            if new_data_line.type == DataLine.Type.DUPLICATED_SHOT:
                new_data_line.type = DataLine.Type.SHOT

    def __calculate_count(self):
        self.splays_count = 0
        self.shots_count = 0

        for data_line in self.data:
            if data_line.type == DataLine.Type.SHOT:
                self.shots_count = self.shots_count + 1
            elif data_line.type == DataLine.Type.SPLAY:
                self.splays_count = self.splays_count + 1

    def __find_duplicates(self):
        have_duplicates = False
        previous_data = DataLine()
        for data_line in self.data:
            if data_line.toSt:
                data_line.type = DataLine.Type.SHOT
            else:
                data_line.type = DataLine.Type.SPLAY

            if previous_data.toSt and data_line.toSt and previous_data.toSt == data_line.toSt:
                have_duplicates = True
            previous_data = data_line

        if not have_duplicates:
            return

        self.__previous_data = DataLine()
        self.__tape = []
        self.__compass = []
        self.__clino = []
        self.__comments = []

        new_data = []

        for data_line in self.data:
            if not data_line.toSt or (
                            data_line.fromSt !=
                            self.__previous_data.fromSt or data_line.toSt
                        != self.__previous_data.toSt):
                self.__write_duplicated_shot(new_data)
                self.__tape = []
                self.__compass = []
                self.__clino = []
                self.__comments = []
            self.__previous_data = data_line

            if data_line.toSt and data_line.tape != 0:
                self.__tape.append(data_line.tape)
                self.__compass.append(data_line.compass)
                self.__clino.append(data_line.clino)
                self.__comments.append(data_line.comment)
                data_line.type = DataLine.Type.DUPLICATED_SHOT

            new_data.append(data_line)
        self.__write_duplicated_shot(new_data)
        self.data = new_data

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
