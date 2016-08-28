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


import shlex
import datetime
import struct
import time

from survey_reader import *


import ReadTop as rt


class PocketTopoTopReader(SurveyReader):
    def __init__(self, file_path):
        super(PocketTopoTopReader, self).__init__(file_path)

    @classmethod
    def can_read_file(cls, file_path):
        with open(file_path, "rb") as tfile:
            if tfile.read(3) == b'Top':
                return True
            return False

    @classmethod
    def file_type(cls):
        return "PocketTopo top"

    @classmethod
    def file_extension(cls):
        return "top"

    def _read_data(self, file_path):
        data = rt.readfile(file_path, False, False)
        # {'trips': trips, 'shots': shots, 'ref': references}
        for rtrip in data['trips']:
            #{'date': tdate, 'comment': comment, 'dec': dec}
            trip = Trip()
            if 'comment' in rtrip and rtrip['comment']:
                trip.comment = rtrip['comment'].strip()
                if trip.comment.startswith('{'):
                    index = trip.comment.find('}')
                    if index > 0:
                        trip.comment = trip.comment[(index+1):]
            if 'date' in rtrip and rtrip['date']:
                trip.date = datetime.datetime.fromtimestamp(time.mktime(rtrip['date']))
            if 'dec' in rtrip and rtrip['dec']:
                trip.declination = rtrip['dec']
            self.survey.trips.append(trip)
        for rshoot in data['shots']:
            # {'from', 'to', 'tape', 'compass', 'clino', 'trip', 'direction', 'comment'}
            if not 'trip' in rshoot or rshoot['trip'] < 0: continue
            trip = self.survey.trips[rshoot['trip']+1]
            data_line = DataLine()
            if 'from' in rshoot:
                data_line.fromSt = rshoot['from']
            if 'to' in rshoot and rshoot['to'] != "-":
                data_line.toSt = rshoot['to']
            if 'compass' in rshoot:
                data_line.compass = round(rshoot['compass'], 2)
            if 'clino' in rshoot:
                data_line.clino = round(rshoot['clino'], 2)
            if 'tape' in rshoot:
                data_line.tape = round(rshoot['tape'], 3)
            if 'comment' in rshoot:
                data_line.comment = rshoot['comment']
            if 'rollangle' in rshoot:
                data_line.comment += " Roll: %.1f " % (rshoot['rollangle'])
            data_line.comment = data_line.comment.strip()
            is_splay = not data_line.toSt
            if is_splay:
                trip.splays_count += 1
                data_line.type = DataLine.Type.SPLAY
            elif data_line != trip.last_dataline:
                trip.shots_count += 1
            trip.data.append(data_line)
        return self.survey
