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
import os


class WallsSurveyWriter(SurveyWriter):
    def __init__(self, survey_reader, file_path, precalculate, hide_duplicates, move_splays, show_roll, header,
                 footer=""):
        super(WallsSurveyWriter, self).__init__(survey_reader, file_path,
                                                True, hide_duplicates, move_splays, show_roll, header, footer)

    @classmethod
    def file_type(cls):
        return "Walls"

    @classmethod
    def file_extension(cls):
        return "srv"

    def _write_data(self, file_path):
        f = open(file_path, 'w')
        first_line = os.path.splitext(os.path.basename(self._survey_reader.file_path))[0]
        if self._survey_reader.survey.name:
            first_line = self._survey_reader.survey.name
        f.write(";%s\n" % first_line)

        if self._header:
            f.write("\n")
            header_lines = self._header.splitlines()
            for header_line in header_lines:
                f.write(";%s\n" % header_line.strip())
            f.write("\n")

        f.write(";Data imported from: %s (%s)\n\n" % (os.path.basename(self._survey_reader.file_path), self._survey_reader.file_type()))


        f.write(";#PREFIX %s\n" % first_line)
        f.write("#UNITS D=M A=G V=G Order=DAV\n\n")

        first_trip = True
        for trip in self._survey_reader.survey.trips:

            if trip.shots_count == 0:
                continue

            if not first_trip:
                f.write("\n\n")

            if trip.date:
                date_string = trip.date.strftime("%Y-%m-%d")
                f.write("#DATE %s\n\n" % date_string)
            else:
                f.write(";#DATE <YYYY-MM-DD>\n\n")

            if first_trip:
                first_trip = False

            if trip.comment:
                f.write(";Comment from file:\n")
                comment = StringIO.StringIO(trip.comment)
                for comment_line in comment:
                    f.write(";%s\n" % comment_line.strip())
                f.write("\n")

            for data in trip.data:
                if data.type == DataLine.Type.SPLIT:
                    f.write("\n\n;Splay shots:\n")
                    continue

                prefix = ""
                if data.type == DataLine.Type.DUPLICATED_SHOT:
                    if self._hide_duplicates:
                        continue
                    else:
                        prefix = ";"

                toSt = data.toSt
                if data.type == DataLine.Type.SPLAY: toSt = "-"
                if data.tape == 0: prefix = ";"

                f.write(
                        "%s%s\t%s\t%0.3f\t%0.2f\t%0.2f" % (
                            prefix, data.fromSt, toSt, data.tape, data.compass,
                            data.clino))

                comment = data.comment
                comment = (" ".join(comment.splitlines())).strip()
                if data.tape == 0:
                    if data.type != DataLine.Type.SPLAY:
                        comment = "Connecting shot; " + comment
                    else:
                        comment = "Continuation shot; " + comment
                comment = comment.strip(' ;').strip()
                if comment:
                    f.write("\t;%s" % comment)
                f.write("\n")

        if self._footer:
            f.write("\n;%s\n" % self._footer)

        f.close()