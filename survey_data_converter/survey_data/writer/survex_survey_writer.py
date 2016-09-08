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

from survey_writer import *
import StringIO
import math
import os


class SurvexSurveyWriter(SurveyWriter):
    def __init__(self, survey_reader, file_path, precalculate, hide_duplicates, move_splays, show_roll, header,
                 footer=""):
        super(SurvexSurveyWriter, self).__init__(survey_reader, file_path,
                                                 precalculate, hide_duplicates, move_splays, show_roll, header, footer)

    @classmethod
    def file_type(cls):
        return "Survex"

    @classmethod
    def file_extension(cls):
        return "svx"

    def _write_data(self, file_path):
        f = open(file_path, 'w')

        if self._header:
            header_lines = self._header.splitlines()
            for header_line in header_lines:
                f.write(";%s\n" % header_line.strip())
            f.write("\n")

        f.write(";Data imported from: %s (%s)\n" % (
            os.path.basename(self._survey_reader.file_path),
            self._survey_reader.file_type()))

        survey_name = \
        os.path.splitext(os.path.basename(self._survey_reader.file_path))[0]
        if self._survey_reader.survey.name:
            survey_name = self._survey_reader.survey.name

        trip_count = len(self._survey_reader.survey.trips)
        for trip in self._survey_reader.survey.trips:
            if trip.shots_count == 0: trip_count = trip_count - 1;

        trip_number = 0

        for trip in self._survey_reader.survey.trips:
            if trip.shots_count == 0:
                continue

            f.write("\n*begin %s" % survey_name)
            if trip_count > 1:
                if not trip.name:
                    trip_number = trip_number + 1
                    f.write("-%d" % trip_number)
                else:
                    f.write("-%s" & trip.name)
            f.write("\n")

            if trip.date:
                date_string = trip.date.strftime("%Y.%m.%d")
                f.write("*date %s\n\n" % date_string)
            else:
                f.write(";#*date <YYYY.MM.DD>\n\n")

            if trip.comment:
                f.write(";Comment from file:\n")
                comment = StringIO.StringIO(trip.comment)
                for comment_line in comment:
                    f.write(";%s\n" % comment_line.strip())
                f.write("\n")

            f.write(";*export <STATION>\n;*entrance <STATION>\n\n")

            f.write(";*team \"<PERSON NAME>\" tape compass clino\n")
            f.write(";*team \"<PERSON NAME>\" notes pictures\n")
            f.write(";*team \"<PERSON NAME>\" assistant\n")
            f.write(";*instrument tape compass clino \"DistoX\"\n\n")

            f.write("*units tape meters\n*units compass clino degrees\n")
            f.write("*data normal from to tape compass clino\n\n")

            for data in trip.data:
                if self._hide_duplicates and data.type == DataLine.Type.DUPLICATED_SHOT:
                    continue
                if data.type == DataLine.Type.SPLIT:
                    f.write("\n\n;Splay shots:\n")
                    continue
                if not self._precalculate and data.calculated:
                    continue

                additional_line = ''
                fromSt = data.fromSt.replace(".", "_")
                toSt = data.toSt
                if data.type == DataLine.Type.SPLAY:
                    toSt = ".."
                else:
                    toSt = toSt.replace(".", "_")

                prefix = ""
                if data.tape == 0: prefix = ";"
                if data.tape == 0 and data.type != DataLine.Type.SPLAY:  prefix = "\n" + prefix

                if self._precalculate and data.type == DataLine.Type.DUPLICATED_SHOT:
                    prefix = ";"

                f.write(
                    "%s%s\t%s\t%0.3f\t%0.2f\t%0.2f" % (
                        prefix, fromSt, toSt, data.tape, data.compass,
                        data.clino))

                comment = ""
                if self._precalculate and data.calculated and self._hide_duplicates:
                    comment = comment + data.calculated_comment
                comment = comment + " ;" + data.comment
                comment = (" ".join(comment.splitlines())).strip()
                if data.tape == 0:
                    if data.type != DataLine.Type.SPLAY:
                        comment = "Connecting shot; " + comment
                        additional_line = ';*equate %s\t%s\t;Generated automatically\n\n' % (
                            fromSt, toSt)
                    else:
                        comment = "Continuation shot; " + comment
                comment = comment.strip(' ;').strip()
                if comment:
                    f.write("\t;%s" % comment)
                f.write("\n")
                if additional_line:
                    f.write(additional_line)

            f.write("\n*end %s" % survey_name)
            if trip_count > 1:
                if not trip.name:
                    f.write("-%d" % trip_number)
                else:
                    f.write("-%s" & trip.name)
            f.write("\n")

        if self._footer:
            f.write("\n;%s\n" % self._footer)

        f.close()
