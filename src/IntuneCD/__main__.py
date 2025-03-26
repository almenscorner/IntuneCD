# -*- coding: utf-8 -*-

import argparse
from IntuneCD.run_backup import get_parser as get_backup_parser, start as run_backup
from IntuneCD.run_documentation import (
    get_parser as get_documentation_parser,
    start as run_documentation,
)
from IntuneCD.run_update import get_parser as get_update_parser, start as run_update
from importlib.metadata import version, PackageNotFoundError


def get_version():
    try:
        return version("IntuneCD")
    except PackageNotFoundError:
        return "unknown"


def banner():
    green = "\033[92m"
    bold = "\033[1m"
    reset = "\033[0m"
    return (
        bold
        + green
        + r"""
          ..
        ....
       .::::
      .:::::            ___       _                     ____ ____
     .::::::           |_ _|_ __ | |_ _   _ _ __   ___ / ___|  _ \
    .:::::::.           | || '_ \| __| | | | '_ \ / _ \ |   | | | |
   ::::::::::::::.      | || | | | |_| |_| | | | |  __/ |___| |_| |
  ::::::::::::::.      |___|_| |_|\__|\__,_|_| |_|\___|\____|____/                 _
        :::::::.       |_ _|_ __ | |_ _   _ _ __   ___    __ _ ___    ___ ___   __| | ___
        ::::::.         | || '_ \| __| | | | '_ \ / _ \  / _` / __|  / __/ _ \ / _` |/ _ \
        :::::.          | || | | | |_| |_| | | | |  __/ | (_| \__ \ | (_| (_) | (_| |  __/
        ::::           |___|_| |_|\__|\__,_|_| |_|\___|  \__,_|___/  \___\___/ \__,_|\___|
        :::
        ::

Keep your Intune setup version-controlled and auditable. 
IntuneCD brings Intune to your CI/CD pipeline and command line with automated backups, updates, and documentation.
    """
        + reset
    )


class BannerHelpFormatter(argparse.RawTextHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = ""
        banner_text = banner()
        super().add_usage(
            banner_text + "\n\n" + (prefix or "Usage: "), actions, groups, ""
        )


def main():
    parser = argparse.ArgumentParser(formatter_class=BannerHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser.add_argument(
        "-v", "--version", action="version", version=f"IntuneCD {get_version()}"
    )

    backup_parser = subparsers.add_parser(
        "backup", parents=[get_backup_parser(include_help=False)]
    )
    backup_parser.set_defaults(func=run_backup)

    update_parser = subparsers.add_parser(
        "update", parents=[get_update_parser(include_help=False)]
    )
    update_parser.set_defaults(func=run_update)

    documentation_parser = subparsers.add_parser(
        "document", parents=[get_documentation_parser(include_help=False)]
    )
    documentation_parser.set_defaults(func=run_documentation)

    args = parser.parse_args()
    args.func(args)
