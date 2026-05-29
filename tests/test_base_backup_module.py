# -*- coding: utf-8 -*-
from src.IntuneCD.intunecdlib.BaseBackupModule import BaseBackupModule


def test_prepare_file_name_replaces_linebreaks():
    module = BaseBackupModule()

    prepared = module._prepare_file_name("Application_win32_6_17_2_2\r\n")

    assert prepared == "Application_win32_6_17_2_2"
    assert "\r" not in prepared
    assert "\n" not in prepared


def test_prepare_file_name_replaces_windows_reserved_characters():
    module = BaseBackupModule()

    prepared = module._prepare_file_name('Application/\\:*?<>"|Name')

    assert prepared == "Application_________Name"


def test_prepare_file_name_removes_zero_width_characters():
    module = BaseBackupModule()

    prepared = module._prepare_file_name("Application\u200bName\ufeff")

    assert prepared == "ApplicationName"
