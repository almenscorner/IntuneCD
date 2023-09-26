#!/usr/bin/env python3

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

import os
import sys
import base64
import argparse
import json

from io import StringIO
from .get_authparams import getAuth

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
        "-f",
        "--frontend",
        help="***This parameter is deprecated and will be removed in a future release***",
        type=str,
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
        tenant="PROD",
    )

    def run_update(path, token, assignment, exclude, report, create_groups, remove):
        diff_count = 0
        diff_summary = []

        if "AppConfigurations" not in exclude:
            from .update_appConfiguration import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "AppProtection" not in exclude:
            from .update_appProtection import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "Compliance" not in exclude:
            from .update_compliance import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "DeviceManagementSettings" not in exclude and args.interactiveauth is True:
            from .update_deviceManagementSettings import update

            diff_summary.append(update(path, token, report))
        else:
            print("-" * 90)
            print(
                "***Device Management Settings is only available with interactive auth***"
            )

        if "DeviceCategories" not in exclude:
            from .update_deviceCategories import update

            diff_summary.append(update(path, token, report, remove))

        if "NotificationTemplate" not in exclude:
            from .update_notificationTemplate import update

            diff_summary.append(update(path, token, report, remove))

        if "Profiles" not in exclude:
            from .update_profiles import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "GPOConfigurations" not in exclude:
            from .update_groupPolicyConfiguration import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "AppleEnrollmentProfile" not in exclude:
            from .update_appleEnrollmentProfile import update

            diff_summary.append(update(path, token, report))

        if "WindowsEnrollmentProfile" not in exclude:
            from .update_windowsEnrollmentProfile import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "EnrollmentStatusPage" not in exclude:
            from .update_enrollmentStatusPage import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "EnrollmentConfigurations" not in exclude:
            from .update_enrollmentConfigurations import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "Filters" not in exclude:
            from .update_assignmentFilter import update

            diff_summary.append(update(path, token, report))

        if "Intents" not in exclude:
            from .update_managementIntents import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "ProactiveRemediation" not in exclude:
            from .update_proactiveRemediation import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "PowershellScripts" not in exclude:
            from .update_powershellScripts import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "ShellScripts" not in exclude:
            from .update_shellScripts import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "CustomAttribute" not in exclude:
            from .update_customAttributeShellScript import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "ConfigurationPolicies" not in exclude:
            from .update_configurationPolicies import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "ConditionalAccess" not in exclude:
            from .update_conditionalAccess import update

            diff_count += update(path, token, report, remove)

        if "WindowsDriverUpdateProfiles" not in exclude:
            from .update_windowsDriverUpdates import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "windowsFeatureUpdates" not in exclude:
            from .update_windowsFeatureUpdates import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        if "windowsQualityUpdates" not in exclude:
            from .update_windowsQualityUpdates import update

            diff_summary.append(
                update(path, token, assignment, report, create_groups, remove)
            )

        for sum in diff_summary:
            for config in sum:
                diff_count += config.count

        return diff_count, diff_summary

    if token is None:
        raise Exception("Token is empty, please check os.environ variables")
    else:
        if args.frontend:
            print(
                "***The --frontend argument is deprecated and will be removed in a future release***"
            )
            print(
                "***Please migrate to --intunecdmonitor instead, see https;//github.com/almenscorner/intunecd/wiki***"
            )

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
                args.u,
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
                    if config.diffs:
                        changes.append(
                            {
                                "name": config.name,
                                "type": config.type,
                                "diffs": config.diffs,
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
                args.u,
                exclude,
                args.report,
                args.create_groups,
                args.remove,
            )


if __name__ == "__main__":
    start()
