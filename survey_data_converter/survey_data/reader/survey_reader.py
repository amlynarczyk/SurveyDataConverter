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


class SurveyReader(object):
    __metaclass__ = ABCMeta

    def __new__(cls, file_path):
        reader_classes = cls.__subclasses__()
        for reader_class in reader_classes:
            if reader_class.can_read_file(file_path):
                return object.__new__(reader_class, file_path)
        return None

    def __init__(self, file_path):
        super(SurveyReader, self).__init__()
        self.file_path = file_path
        self.survey = Survey()
        self.survey.trips.append(Trip())
        self._read_data(file_path)
        for trip in self.survey.trips:
            trip.preprocess_data()

    @classmethod
    def can_read_file(cls, file_path):
        raise NotImplementedError

    @classmethod
    def supported_files(cls):
        reader_classes = cls.__subclasses__()
        supported_files = []
        for reader_class in reader_classes:
            supported_files.append(
                [reader_class.file_type(), reader_class.file_extension()])
        return supported_files

    @classmethod
    def file_type(cls):
        raise NotImplementedError

    @classmethod
    def file_extension(cls):
        raise NotImplementedError

    def _read_data(self, file_path):
        raise NotImplementedError

    def _trip_with_name(self, trip_name):
        for trip in self.survey.trips:
            if trip.name == trip_name:
                return trip
        return None
