#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
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

This module contains the functions to run the backup.
"""

import argparse
import base64
import json
import os
import sys
from io import StringIO

from .backup_entra import backup_entra
from .backup_intune import backup_intune
from .intunecdlib.archive import move_to_archive
from .intunecdlib.get_accesstoken import obtain_azure_token
from .intunecdlib.get_authparams import getAuth

REPO_DIR = os.environ.get("REPO_DIR")


def start():
    parser = argparse.ArgumentParser(description="Save backup of Intune configurations")
    parser.add_argument(
        "-o",
        "--output",
        help="The format backups will be saved as, valid options are json or yaml. Default is json",
        type=str,
        default="json",
    )
    parser.add_argument(
        "-p",
        "--path",
        help="The path to which the configurations will be saved. Default value is $(Build.SourcesDirectory)",
        type=str,
        default=REPO_DIR,
    )
    parser.add_argument(
        "-m",
        "--mode",
        help=(
            "The mode in which the script is run, 0 = devtoprod (backup from dev -> update to prod) "
            "uses os.environ DEV_TENANT_NAME, DEV_CLIENT_ID, DEV_CLIENT_SECRET, "
            "1 = standalone (backup from prod) uses os.environ TENANT_NAME, CLIENT_ID, CLIENT_SECRET"
        ),
        type=int,
        default=0,
    )
    parser.add_argument(
        "-a",
        "--localauth",
        help=(
            "When this paramater is set, provide a path to a local dict file containing the following keys: "
            "params:TENANT_NAME, CLIENT_ID, CLIENT_SECRET when run in standalone mode and "
            "params:DEV_TENANT_NAME, DEV_CLIENT_ID, DEV_CLIENT_SECRET when run in devtoprod"
        ),
        type=str,
    )
    parser.add_argument(
        "-c",
        "--certauth",
        help="When using certificate auth, the following ENV variables is required: TENANT_NAME, CLIENT_ID, THUMBPRINT, KEY_FILE",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--interactiveauth",
        help="When using interactive auth, the following ENV variables is required: TENANT_NAME, CLIENT_ID",
        action="store_true",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        help="List of objects to exclude from the backup, separated by space.",
        choices=[
            "assignments",
            "AppConfigurations",
            "AppProtection",
            "APNs",
            "VPP",
            "Applications",
            "Compliance",
            "NotificationTemplate",
            "Profiles",
            "GPOConfigurations",
            "AppleEnrollmentProfile",
            "WindowsEnrollmentProfile",
            "EnrollmentStatusPage",
            "Filters",
            "ManagedGooglePlay",
            "Intents",
            "CompliancePartner",
            "ManagementPartner",
            "RemoteAssistancePartner",
            "ProactiveRemediation",
            "PowershellScripts",
            "ShellScripts",
            "ConfigurationPolicies",
            "ConditionalAccess",
            "EnrollmentConfigurations",
            "DeviceManagementSettings",
            "CustomAttributes",
            "DeviceCategories",
            "windowsDriverUpdates",
            "windowsFeatuteUpdates",
            "windowsQualityUpdates",
            "entraApplications",
            "entraAuthenticationFlowsPolicy",
            "entraAuthenticationMethods",
            "entraAuthorizationPolicy",
            "entraB2BPolicy",
            "entraDeviceRegistrationPolicy",
            "entraExternalIdentitiesPolicy",
            "entraGroupSettings",
            "entraRoamingSettings",
            "entraSecurityDefaults",
            "entraSSPR",
            "entraUserSettings",
            "entraDomains",
            "Roles",
        ],
        nargs="+",
    )
    parser.add_argument(
        "--intunecdmonitor",
        help="When this parameter is set, the script is run in the IntuneCDMonitor context",
        action="store_true",
    )
    parser.add_argument(
        "-ap",
        "--autopilot",
        help="If set to True, a record of autopilot devices will be saved",
    )
    parser.add_argument(
        "-f",
        "--frontend",
        help="***This parameter is deprecated and will be removed in a future release***",
        type=str,
    )
    parser.add_argument(
        "--prefix",
        help="When set, only backs up configurations whose name starts with the configured prefix",
        type=str,
    )
    parser.add_argument(
        "--append-id",
        help="When set, the id of the configuration will be appended to the name of the exported file",
        action="store_true",
    )
    parser.add_argument(
        "--entrabackup",
        help="When set, backs up Entra configurations",
        action="store_true",
    )
    parser.add_argument(
        "--ignore-omasettings",
        help="When set, ignores encrypted OMA Settings configuration type. Useful if you only want read permissions to Graph API.",
        action="store_true",
    )
    parser.add_argument(
        "--activationlock",
        help="When set, backs up Activation Lock Bypass Codes",
        action="store_true",
    )

    args = parser.parse_args()

    def devtoprod():
        return "devtoprod"

    def standalone():
        return "standalone"

    switcher = {0: devtoprod, 1: standalone}

    def selected_mode(argument):
        func = switcher.get(argument, "nothing")
        return func()

    if args.certauth or args.interactiveauth:
        args.mode = None
    else:
        args.mode = selected_mode(args.mode)

    token = getAuth(
        args.mode,
        args.localauth,
        args.certauth,
        args.interactiveauth,
        args.entrabackup,
        tenant="DEV",
    )

    if args.entrabackup:
        azure_token = obtain_azure_token(os.environ.get("TENANT_ID"), args.path)

    def run_backup(path, output, exclude, token, prefix, append_id):
        results = []

        if args.entrabackup:
            print("***Entra backup***")

            backup_entra(results, path, output, token, azure_token, args, exclude)

            print("***Intune backup***")

        backup_intune(results, path, output, exclude, token, prefix, append_id, args)

        from .intunecdlib.assignment_report import get_group_report

        get_group_report(path, output)

        config_count = sum([result.get("config_count", 0) for result in results])

        created_files = [
            output
            for result in results
            if result.get("outputs", None)
            for output in result.get("outputs", None)
            if output is not None
        ]

        move_to_archive(path, created_files, output)

        return config_count

    if args.output == "json" or args.output == "yaml":
        if args.frontend:
            print(
                "***The --forntend argument is deprecated and will be removed in a future release***"
            )
            print(
                "***Please migrate to --intunecdmonitor instead, see https;//github.com/almenscorner/intunecd/wiki***"
            )

        if token is None:
            raise Exception("Token is empty, please check os.environ variables")

        if args.exclude:
            exclude = args.exclude
        else:
            exclude = []

        if args.intunecdmonitor:
            old_stdout = sys.stdout
            sys.stdout = feedstdout = StringIO()
            count = run_backup(
                args.path, args.output, exclude, token, args.prefix, args.append_id
            )
            sys.stdout = old_stdout
            feed_bytes = feedstdout.getvalue().encode("utf-8")
            out = base64.b64encode(feed_bytes).decode("utf-8")

            summary = {"config_count": count, "feed": out}

            with open(f"{args.path}/backup_summary.json", "w") as f:
                f.write(json.dumps(summary))

        else:
            run_backup(
                args.path, args.output, exclude, token, args.prefix, args.append_id
            )

    else:
        print("Please enter a valid output format, json or yaml")


if __name__ == "__main__":
    start()
