#!/usr/bin/env python2 -*- coding: utf-8 -*-

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

from __future__ import unicode_literals

import sys
import os

import wx
import wx.lib.agw.persist as PERSIST

from .info import (
    __appname__,
    __projecturl__
)

from .version import __version__

from survey_data import SurveyReader, SurveyWriter


class MainFrame(wx.Frame):
    FRAME_STYLE = wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
    SURVEY_LABEL_TEXT = "Survey File:"
    SURVEY_FILE_CTRL_MESSAGE = "Select Survey Data File"

    LICENSE_LABEL_TEXT = "Add standard header in exported file"
    LICENSE_TEXT = """This survey data is made available under the Open Data Commons Attribution License:
http://opendatacommons.org/licenses/by/1.0/"""

    ALERT_UNSUPPORTED_FILE_TYPE_CAPTION = "Unsupported file"
    ALERT_UNSUPPORTED_FILE_TYPE_MESSAGE = "Can't recognize this file as a " \
                                          "survey data, probably it isn't " \
                                          "supported yet."
    ALERT_FINISHED_CAPTION = "File saved"
    ALERT_FINISHED_MESSAGE = "All data have been exported to the file you selected."

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, wx.ID_ANY, __appname__,
                          style=self.FRAME_STYLE, name="MainFrame")
        self.__active = False

        supported_files = SurveyReader.supported_files()
        supported_extensions = []
        for supported_file in supported_files:
            supported_extensions.append(supported_file[-1])
        supported_extensions = list(set(supported_extensions))

        file_types_string = ""
        for extension in supported_extensions:
            file_types_string += "*.%s;" % extension
        file_types_string = file_types_string.strip(';')

        wildcard = "Supported files (%s)|%s" % (
        file_types_string, file_types_string)

        if hasattr(self, 'SetMinClientSize'):
            self.SetMinClientSize(wx.Size(400, -1))

        self._panel = wx.Panel(self)

        self._source_file_label = wx.StaticText(self._panel,
                                                label=self.SURVEY_LABEL_TEXT)
        self._source_file_ctrl = wx.FilePickerCtrl(self._panel,
                                                   message=self.SURVEY_FILE_CTRL_MESSAGE,
                                                   wildcard=wildcard)

        self._writers = SurveyWriter.__subclasses__()
        writer_types = []
        for writer in self._writers:
            writer_types.append(writer.file_type())

        self._writers_panel = wx.RadioBox(self._panel, label="Convert to:",
                                          majorDimension=1,
                                          choices=writer_types,
                                          style=wx.RA_SPECIFY_ROWS,
                                          name="SelectedWriter")

        self._license_checkbox = wx.CheckBox(self._panel, style=wx.CHK_2STATE,
                                             label=self.LICENSE_LABEL_TEXT,
                                             name="AddLicense")
        self._license_checkbox.SetValue(True)
        self._license_textfield = wx.TextCtrl(self._panel,
                                              style=wx.TE_MULTILINE,
                                              size=(-1, 60),
                                              name="LicenseText")
        self._license_textfield.SetValue(self.LICENSE_TEXT)

        self._save_button = wx.Button(self._panel, label="Save")
        self._save_button.Bind(wx.EVT_BUTTON, self._on_save)

        if sys.platform == "win32":
            self._source_file_ctrl.GetPickerCtrl().SetLabel("Browse...")

        self._add_sizers()

        self._toggle_export_interface(False)

        self.Center()

        self._register_and_restore()

        self.Bind(wx.EVT_CLOSE, self._on_exit)
        self._source_file_ctrl.Bind(wx.EVT_FILEPICKER_CHANGED,
                                    self._on_file_selected)

    def _register_and_restore(self):
        mgr = PERSIST.PersistenceManager.Get()
        mgr.RegisterAndRestore(self)
        mgr.RegisterAndRestore(self._writers_panel)
        mgr.RegisterAndRestore(self._license_checkbox)
        mgr.RegisterAndRestore(self._license_textfield)
        self.Fit()

    def _on_exit(self, event):
        mgr = PERSIST.PersistenceManager.Get()
        mgr.SaveAndUnregister()
        event.Skip()

    def _on_save(self, event):
        header = ""
        if self._license_checkbox.GetValue():
            header = self._license_textfield.GetValue()

        idx = self._writers_panel.GetSelection()
        writer = self._writers[idx]
        survey_file_path = self._source_file_ctrl.GetPath()
        save_file_name = os.path.basename(survey_file_path)
        save_file_name = os.path.splitext(save_file_name)[0]
        save_file_name += "." + writer.file_extension()
        save_file_dialog = wx.FileDialog(self, message="Save As",
                                         defaultFile=save_file_name,
                                         style=wx.FD_SAVE |
                                               wx.FD_OVERWRITE_PROMPT)
        if save_file_dialog.ShowModal() == wx.ID_OK:
            footer = "Created with %s v%s (%s)" % (
                __appname__, __version__, __projecturl__)
            writer(self._file_reader, save_file_dialog.GetPath(), header,
                   footer)
            alert = wx.MessageDialog(self, self.ALERT_FINISHED_MESSAGE,
                                     self.ALERT_FINISHED_CAPTION,
                                     wx.OK | wx.ICON_INFORMATION)
            alert.Center()
            alert.ShowModal()
            alert.Destroy()

        save_file_dialog.Destroy()
        event.Skip()

    def _on_file_selected(self, event):
        survey_file_path = self._source_file_ctrl.GetPath()
        self._file_reader = SurveyReader(survey_file_path)
        export_possible = self._file_reader is not None
        self._toggle_export_interface(export_possible)
        if not export_possible:
            self._alert_unsupported_survey_file()
        event.Skip()

    def _add_sizers(self):
        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        source_file_sizer = wx.BoxSizer(wx.HORIZONTAL)

        source_file_sizer.Add(self._source_file_label, 0,
                              wx.ALIGN_CENTER_VERTICAL)
        source_file_sizer.AddSpacer(5)
        source_file_sizer.Add(self._source_file_ctrl, 1)

        vertical_sizer.Add(source_file_sizer, 0, wx.TOP | wx.BOTTOM | wx.EXPAND,
                           0)
        vertical_sizer.Add(wx.StaticLine(self._panel), 0,
                           wx.TOP | wx.BOTTOM | wx.EXPAND, 10)

        vertical_sizer.Add(self._writers_panel, 0,
                           wx.TOP | wx.BOTTOM | wx.EXPAND,
                           0)

        vertical_sizer.Add(wx.StaticLine(self._panel), 0,
                           wx.TOP | wx.BOTTOM | wx.EXPAND, 10)
        vertical_sizer.Add(self._license_checkbox, 0,
                           wx.ALIGN_CENTER_HORIZONTAL, 0)
        vertical_sizer.AddSpacer(5)
        vertical_sizer.Add(self._license_textfield, 0,
                           wx.TOP | wx.BOTTOM | wx.EXPAND, 0)
        vertical_sizer.AddSpacer(5)
        vertical_sizer.Add(wx.StaticLine(self._panel), 0,
                           wx.TOP | wx.BOTTOM | wx.EXPAND, 10)
        vertical_sizer.Add(self._save_button, 0, wx.ALIGN_RIGHT,
                           0)

        horizontal_sizer.Add(vertical_sizer, 1, wx.EXPAND | wx.ALL, 10)
        self._panel.SetSizer(horizontal_sizer)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self._panel, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

    def _alert_unsupported_survey_file(self):
        alert = wx.MessageDialog(self, self.ALERT_UNSUPPORTED_FILE_TYPE_MESSAGE,
                                 self.ALERT_UNSUPPORTED_FILE_TYPE_CAPTION,
                                 wx.OK | wx.ICON_ERROR)
        alert.Center()
        alert.ShowModal()
        alert.Destroy()

    def _toggle_export_interface(self, active):
        self._writers_panel.Enable(active)
        self._save_button.Enable(active)
