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

from distutils.core import setup
import survey_data_converter.version
import survey_data_converter.info
import py2exe
import os
import sys
from glob import glob
import shutil


def create_build_script():
    dest_dir = os.path.join('build', '_scripts')
    dest_file = os.path.join(dest_dir, 'survey_data_converter')
    src_file = os.path.join('survey_data_converter', '__main__.py')

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    shutil.copyfile(src_file, dest_file)

create_build_script()

sys.path.append("C:\\Windows\\WinSxS\\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.21022.8_none_bcb86ed6ac711f91")
data_files = [("Microsoft.VC90.CRT", glob(r'C:\Windows\WinSxS\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.21022.8_none_bcb86ed6ac711f91\*.*'))]

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(PATH), "survey_data_converter"))

setup(
    version = survey_data_converter.version.__version__,
    description = survey_data_converter.info.__description__,
    name = survey_data_converter.info.__appname__,
    author = survey_data_converter.__author__,
    license = survey_data_converter.__license__,
    data_files = data_files,
    # targets to build
    windows = [{
        'script': 'build\\_scripts\\survey_data_converter',
    }],
    packages = ['survey_data_converter'],
    )
