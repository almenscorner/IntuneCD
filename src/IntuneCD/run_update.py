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

This module contains the functions to run the update.
"""

import argparse
import base64
import json
import os
import sys
from io import StringIO

from .intunecdlib.get_accesstoken import obtain_azure_token
from .intunecdlib.get_authparams import getAuth
from .update_entra import update_entra
from .update_intune import update_intune

REPO_DIR = os.environ.get("REPO_DIR")


def start():
    parser = argparse.ArgumentParser(
        description="Update Intune configurations with values from backup"
    )
    parser.add_argument(
        "-p",
        "--path",
        help="The path to which the configurations are saved. Default value is $(Build.SourcesDirectory)",
        default=REPO_DIR,
    )
    parser.add_argument(
        "-m",
        "--mode",
        help=(
            "The mode in which the script is run, 0 = devtoprod (backup from dev -> update to prod) "
            "uses os.environ PROD_TENANT_NAME, PROD_CLIENT_ID, PROD_CLIENT_SECRET, "
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
            "params:PROD_TENANT_NAME, PROD_CLIENT_ID, PROD_CLIENT_SECRET when run in devtoprod"
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
        "-u",
        "--update-assignments",
        help="When this parameter is set, assignments are updated for all configurations",
        action="store_true",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        help="List of objects to exclude from the backup, separated by space.",
        choices=[
            "AppConfigurations",
            "AppProtection",
            "Compliance",
            "NotificationTemplate",
            "Profiles",
            "GPOConfigurations",
            "AppleEnrollmentProfile",
            "WindowsEnrollmentProfile",
            "EnrollmentStatusPage",
            "Filters",
            "Intents",
            "ProactiveRemediation",
            "PowershellScripts",
            "ShellScripts",
            "ConfigurationPolicies",
            "ConditionalAccess",
            "EnrollmentConfigurations",
            "DeviceManagementSettings",
            "CustomAttributes",
            "DeviceCategories",
            "Roles",
            "ScopeTags",
            "DeviceCompliancePolicies",
            "ComplianceScripts",
            "ReusablePolicySettings",
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
            "entraAuthenticationMethodsConfigurations",
            "entraDomains",
        ],
        nargs="+",
    )
    parser.add_argument(
        "-r",
        "--report",
        help="When this parameter is set, no updates are pushed to Intune but the change summary is pushed to the frontend",
        action="store_true",
    )
    parser.add_argument(
        "-g",
        "--create-groups",
        help="When this parameter is set, groups are created if they do not exist",
        action="store_true",
    )
    parser.add_argument(
        "--remove",
        help="When this parameter is set, configurations in Intune that are not in the backup are removed",
        action="store_true",
    )
    parser.add_argument(
        "--intunecdmonitor",
        help="When this parameter is set, the script is run in the IntuneCDMonitor context",
        action="store_true",
    )
    parser.add_argument(
        "--entraupdate",
        help="When this parameter is set, the script will also update Entra configurations",
        action="store_true",
    )
    parser.add_argument(
        "--scopes",
        help="The scopes to use when obtaining an access token interactively separated by space. Only used when using interactive auth. Default is: DeviceManagementApps.ReadWrite.All, DeviceManagementConfiguration.ReadWrite.All, DeviceManagementManagedDevices.Read.All, DeviceManagementServiceConfig.ReadWrite.All, DeviceManagementRBAC.ReadWrite.All, Group.Read.All, Policy.ReadWrite.ConditionalAccess, Policy.Read.All",
        nargs="+",
    )
    parser.add_argument(
        "-v", "--verbose", help="Prints verbose output", action="store_true"
    )
    parser.add_argument(
        "-t",
        "--token",
        help="The authentication token to use for the update if not using an app registration",
        type=str,
    )
    parser.add_argument(
        "--exit-on-error",
        help="When this parameter is set, IntuneCD will exit on error",
        action="store_true",
    )

    args = parser.parse_args()

    if args.verbose:
        os.environ["VERBOSE"] = "True"

    if args.exit_on_error:
        os.environ["EXIT_ON_ERROR"] = "True"

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

    if not args.scopes:
        args.scopes = [
            "DeviceManagementApps.ReadWrite.All",
            "DeviceManagementConfiguration.ReadWrite.All",
            "DeviceManagementManagedDevices.Read.All",
            "DeviceManagementServiceConfig.ReadWrite.All",
            "DeviceManagementRBAC.ReadWrite.All",
            "Group.Read.All",
            "Policy.ReadWrite.ConditionalAccess",
            "Policy.Read.All",
        ]

    if not args.token:
        token = getAuth(
            args.mode,
            args.localauth,
            args.certauth,
            args.interactiveauth,
            args.scopes,
            args.entraupdate,
            tenant="PROD",
        )
    else:
        token = {"access_token": args.token}

    if args.entraupdate:
        azure_token = obtain_azure_token(os.environ.get("TENANT_ID"), args.path)

    def run_update(path, token, assignment, exclude, report, create_groups, remove):
        diff_count = 0
        diff_summary = []

        if args.entraupdate:
            print("***Entra update***")

            update_entra(diff_summary, path, token, azure_token, report, args, exclude)

            print("-" * 90)
            print("***Intune update***")

        update_intune(
            diff_summary,
            path,
            token,
            assignment,
            report,
            create_groups,
            remove,
            exclude,
            args,
        )

        for sum in diff_summary:
            for config in sum:
                diff_count += config.get("count")

        return diff_count, diff_summary

    if token is None:
        raise Exception("Token is empty, please check os.environ variables")
    else:
        if args.exclude:
            exclude = args.exclude
        else:
            exclude = []

        if args.report:
            print("***Running in report mode, no updates will be pushed to Intune***")

        if args.intunecdmonitor:
            # We are running in the IntuneCDMonitor context, instead of using API calls to the frontend, we will output to file
            old_stdout = sys.stdout
            sys.stdout = feedstdout = StringIO()
            summary = run_update(
                args.path,
                token,
                args.update_assignments,
                exclude,
                args.report,
                args.create_groups,
                args.remove,
            )
            sys.stdout = old_stdout
            feed_bytes = feedstdout.getvalue().encode("utf-8")
            out = base64.b64encode(feed_bytes).decode("utf-8")

            # Write the summary to a file
            changes = []
            for sum in summary[1]:
                for config in sum:
                    if config["diffs"]:
                        changes.append(
                            {
                                "name": config["name"],
                                "type": config["type"],
                                "diffs": config["diffs"],
                            }
                        )

            summary = {
                "type": "diff_count",
                "diff_count": summary[0],
                "changes": changes,
                "feed": out,
            }

            with open(f"{args.path}/update_summary.json", "w") as f:
                f.write(json.dumps(summary))

        else:
            run_update(
                args.path,
                token,
                args.update_assignments,
                exclude,
                args.report,
                args.create_groups,
                args.remove,
            )

    if "VERBOSE" in os.environ:
        del os.environ["VERBOSE"]
    if "EXIT_ON_ERROR" in os.environ:
        del os.environ["EXIT_ON_ERROR"]


if __name__ == "__main__":
    start()
