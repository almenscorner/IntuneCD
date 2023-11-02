#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to get diff summary from the diff.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DiffSummary:
    """
    This class is used to get a summary of the diff.

    :param data: The diff data
    :param name: The name of the object
    :param type: The type of the object
    :param count: The number of changes
    :param message: A message to display
    :param notify: Whether to notify if no changes are found
    :param diffs: The list of changes
    """

    data: dict = field(default_factory=dict)
    name: str = ""
    type: str = ""
    count: int = field(init=False, default=0)
    message: str = ""
    notify: bool = True
    diffs: list = field(init=False, default_factory=list)

    def __post_init__(self):
        for key, value in self.data.items():
            vals = {}
            setting = re.search("\\[(.*)\\]", key)
            if setting:
                setting = setting.group(1).split("[")[-1]

            vals["setting"] = str(setting).replace("'", "").replace('"', "")
            vals["new_val"] = str(value["new_value"]).replace("'", "").replace('"', "")
            vals["old_val"] = str(value["old_value"]).replace("'", "").replace('"', "")
            vals["change_date"] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.diffs.append(vals)

        if self.diffs and not self.message:
            if self.name:
                print(f"Updating {self.type}: {self.name}, values changed:")
            else:
                print(f"Updating {self.type}, values changed:")
            for item in self.diffs:
                print(
                    f"Setting: {item['setting']}, New Value: {item['new_val']}, Old Value: {item['old_val']}"
                )
        elif self.data and self.message:
            self.diffs = [self.message]
            print(self.message)
        else:
            if self.notify:
                print(f"No changes found for {self.type}: {self.name}")

        self.count = len(self.diffs)
