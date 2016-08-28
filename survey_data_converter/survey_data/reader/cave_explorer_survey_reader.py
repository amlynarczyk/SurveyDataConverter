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

# Unit=Meter
# From	 To	 Length	 Bearing	 Inc	 Comments
# 0	 1	 2.366	 1.4	 -15.5
# 1	 2	 5.254	 91.6	 16.6
# 2	 3	 2.187	 122.4	 -1.3
# 2	 2:A	 16.787	 57.2	 3.8
# 3	 4	 7.745	 351.0	 -74.3

import shlex

from survey_reader import *


class CaveExplorerSurveyReader(SurveyReader):
    TYPICAL_STRING_1 = "Unit=Meter"
    TYPICAL_STRING_2 = "From	 To	 Length	 Bearing	 Inc	 Comments"
    TYPICAL_STRING_3 = "Od	 Do	 Odleglosc	 Azymut	 Upad	 Komentarz"

    def __init__(self, file_path):
        super(CaveExplorerSurveyReader, self).__init__(file_path)

    @classmethod
    def can_read_file(cls, file_path):
        f = open(file_path, 'rb')
        first_line = f.readline().strip()
        second_line = f.readline().strip()
        f.close()
        if first_line == cls.TYPICAL_STRING_1 and (second_line == cls.TYPICAL_STRING_2 or second_line == cls.TYPICAL_STRING_3):
            return True
        else:
            return False

    @classmethod
    def file_type(cls):
        return "CaveExplorer txt"

    @classmethod
    def file_extension(cls):
        return "txt"

    def _read_data(self, file_path):
        state = 0
        trip = self.survey.trips[0]
        with open(file_path, 'rb') as f:
            for line in f.readlines():
                line = line.strip()
                data = shlex.split(line)
                if len(data) == 0:
                    continue
                if state < 2:
                    state+=1
                    continue
                if state == 2:
                    is_splay = data[1].find(":") != -1
                    data_line = DataLine()
                    data_line.fromSt = data[0]
                    if not is_splay: data_line.toSt = data[1]
                    data_line.tape = float(data[2])
                    data_line.compass = float(data[3])
                    data_line.clino = float(data[4])
                    trip.data.append(data_line)
                    if is_splay:
                        data_line.type = DataLine.Type.SPLAY
                        trip.splays_count += 1
                    else:
                        trip.shots_count += 1
                    continue