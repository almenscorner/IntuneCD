# -*- coding: utf-8 -*-

import argparse
from IntuneCD.run_backup import get_parser as get_backup_parser, start as run_backup
from IntuneCD.run_documentation import (
    get_parser as get_documentation_parser,
    start as run_documentation,
)
from IntuneCD.run_update import get_parser as get_update_parser, start as run_update
from IntuneCD.run_compare import get_parser as get_compare_parser, start as run_compare
from importlib.metadata import version, PackageNotFoundError


def get_version():
    try:
        return version("IntuneCD")
    except PackageNotFoundError:
        return "unknown"


def banner():
    bold = "\033[1m"
    dim = "\033[2m"
    reset = "\033[0m"

    # Gradient matching the IntuneCD logo: green at the top -> teal/cyan at the
    # bottom (sampled from the project logo on GitHub).
    top = (138, 248, 147)
    bottom = (38, 210, 218)

    # Bolt silhouette sampled from the project logo.
    bolt = [
        "       ▄██      ",
        "      ▄███      ",
        "     ▄████      ",
        "    ▄█████      ",
        "   ███████      ",
        "  ████████▄▄▄▄▄ ",
        " ███████████████",
        "███████████████ ",
        "     ▀███████▀  ",
        "      ██████▀   ",
        "      █████▀    ",
        "      ████▀     ",
        "      ███▀      ",
        "      ██▀       ",
    ]

    wordmark = [
        r" ___       _                     ____ ____",
        r"|_ _|_ __ | |_ _   _ _ __   ___ / ___|  _ \ ",
        r" | || '_ \| __| | | | '_ \ / _ \ |   | | | |",
        r" | || | | | |_| |_| | | | |  __/ |___| |_| |",
        r"|___|_| |_|\__|\__,_|_| |_|\___|\____|____/ ",
    ]

    # The bolt carries the gradient; the wordmark stays plain like the logo,
    # with the tagline dimmed underneath.
    text_block = [f"{bold}{line}{reset}" for line in wordmark]
    text_block += ["", f"{dim}Intune as code{reset}"]
    pad_top = (len(bolt) - len(text_block)) // 2

    steps = max(len(bolt) - 1, 1)
    lines = []
    for i, bolt_line in enumerate(bolt):
        t = i / steps
        r = round(top[0] + (bottom[0] - top[0]) * t)
        g = round(top[1] + (bottom[1] - top[1]) * t)
        b = round(top[2] + (bottom[2] - top[2]) * t)
        text = text_block[i - pad_top] if 0 <= i - pad_top < len(text_block) else ""
        lines.append(f"  \033[38;2;{r};{g};{b}m{bolt_line}{reset}  {text}".rstrip())

    tagline = (
        "\n\nKeep your Intune setup version-controlled and auditable.\n"
        "IntuneCD brings Intune to your CI/CD pipeline and command line with "
        "automated backups, updates, and documentation."
    )

    return "\n".join(lines) + tagline


class BannerArgumentParser(argparse.ArgumentParser):
    # The banner is prepended in format_help rather than via a custom
    # formatter: argparse reuses the parent's formatter_class internally to
    # compute each subcommand's prog, so a banner-injecting formatter leaks
    # the banner into every subparser's usage line.
    def format_help(self):
        return banner() + "\n\n" + super().format_help()


def main():
    parser = BannerArgumentParser()
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

    compare_parser = subparsers.add_parser(
        "compare", parents=[get_compare_parser(include_help=False)]
    )
    compare_parser.set_defaults(func=run_compare)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
