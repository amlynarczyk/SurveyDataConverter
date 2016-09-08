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

from abc import ABCMeta

from ..data import *


class SurveyWriter(object):
    __metaclass__ = ABCMeta

    def __init__(self, survey_reader, file_path, precalculate, hide_duplicates, move_splays, show_roll, header, footer = ""):
        super(SurveyWriter, self).__init__()
        self._precalculate = precalculate
        self._hide_duplicates = precalculate and hide_duplicates
        self._header = header.strip()
        self._footer = footer.strip()
        self._survey_reader = survey_reader

        if move_splays or show_roll:
            for trip in self._survey_reader.survey.trips:
                if move_splays:
                    trip.move_splays_to_end()
                if show_roll:
                    trip.show_rolls()

        self._write_data(file_path)

    @classmethod
    def supported_files(cls):
        writer_classes = cls.__subclasses__()
        supported_files = []
        for writer_class in writer_classes:
            supported_files.append(
                [writer_class.file_type(), writer_class.file_extension()])
        return supported_files

    @classmethod
    def file_type(cls):
        raise NotImplementedError

    @classmethod
    def file_extension(cls):
        raise NotImplementedError

    def _write_data(self, file_path):
        raise NotImplementedError
