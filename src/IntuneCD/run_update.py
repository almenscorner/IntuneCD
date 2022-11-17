#!/usr/bin/env python3

"""
This module contains the functions to run the update.
"""

import os
import sys
import base64
import argparse

from io import StringIO
from .get_authparams import getAuth
from .update_frontend import update_frontend

REPO_DIR = os.environ.get("REPO_DIR")


def start():
    parser = argparse.ArgumentParser(
        description="Update Intune configurations with values from backup")
    parser.add_argument(
        "-p",
        "--path",
        help='The path to which the configurations are saved. Default value is $(Build.SourcesDirectory)',
        default=REPO_DIR,
    )
    parser.add_argument(
        "-m",
        "--mode",
        help=(
            "The mode in which the script is run, 0 = devtoprod (backup from dev -> update to prod) "
            "uses os.environ PROD_TENANT_NAME, PROD_CLIENT_ID, PROD_CLIENT_SECRET, "
            "1 = standalone (backup from prod) uses os.environ TENANT_NAME, CLIENT_ID, CLIENT_SECRET"),
        type=int,
        default=0)
    parser.add_argument(
        "-a",
        "--localauth",
        help=(
            "When this paramater is set, provide a path to a local dict file containing the following keys: "
            "params:TENANT_NAME, CLIENT_ID, CLIENT_SECRET when run in standalone mode and "
            "params:PROD_TENANT_NAME, PROD_CLIENT_ID, PROD_CLIENT_SECRET when run in devtoprod"),
        type=str)
    parser.add_argument(
        "-u",
        help="When this parameter is set, assignments are updated for all configurations",
        action="store_true")
    parser.add_argument(
        "-f",
        "--frontend",
        help="Set the frontend URL to update with configuration count and backup stream",
        type=str)
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
            "AppleEnrollmentProfile",
            "WindowsEnrollmentProfile",
            "EnrollmentStatusPage",
            "Filters",
            "Intents",
            "ProactiveRemediation",
            "PowershellScripts",
            "ShellScripts",
            "ConfigurationPolicies",
            "ConditionalAccess"],
        nargs='+')

    args = parser.parse_args()

    def devtoprod():
        return "devtoprod"

    def standalone():
        return "standalone"

    switcher = {
        0: devtoprod,
        1: standalone
    }

    def selected_mode(argument):
        func = switcher.get(argument, "nothing")
        return func()

    token = getAuth(selected_mode(args.mode), args.localauth, tenant="PROD")

    def run_update(path, token, assignment, exclude):

        diff_count = 0

        if "AppConfigurations" not in exclude:
            from .update_appConfiguration import update
            diff_count += update(path, token, assignment)

        if "AppProtection" not in exclude:
            from .update_appProtection import update
            diff_count += update(path, token, assignment)

        if "Compliance" not in exclude:
            from .update_compliance import update
            diff_count += update(path, token, assignment)

        if "NotificationTemplate" not in exclude:
            from .update_notificationTemplate import update
            diff_count += update(path, token)

        if "Profiles" not in exclude:
            from .update_profiles import update
            diff_count += update(path, token, assignment)

        if "AppleEnrollmentProfile" not in exclude:
            from .update_appleEnrollmentProfile import update
            diff_count += update(path, token)

        if "WindowsEnrollmentProfile" not in exclude:
            from .update_windowsEnrollmentProfile import update
            diff_count += update(path, token, assignment)

        if "EnrollmentStatusPage" not in exclude:
            from .update_enrollmentStatusPage import update
            diff_count += update(path, token, assignment)

        if "Filters" not in exclude:
            from .update_assignmentFilter import update
            diff_count += update(path, token)

        if "Intents" not in exclude:
            from .update_managementIntents import update
            diff_count += update(path, token, assignment)

        if "ProactiveRemediation" not in exclude:
            from .update_proactiveRemediation import update
            diff_count += update(path, token, assignment)

        if "PowershellScripts" not in exclude:
            from .update_powershellScripts import update
            diff_count += update(path, token, assignment)

        if "ShellScripts" not in exclude:
            from .update_shellScripts import update
            diff_count += update(path, token, assignment)

        if "ConfigurationPolicies" not in exclude:
            from .update_configurationPolicies import update
            diff_count += update(path, token, assignment)

        if "ConditionalAccess" not in exclude:
            from .update_conditionalAccess import update
            diff_count += update(path, token)

        return diff_count

    if token is None:
        raise Exception("Token is empty, please check os.environ variables")
    else:

        if args.exclude:
            exclude = args.exclude
        else:
            exclude = []

        if args.frontend:

            old_stdout = sys.stdout
            sys.stdout = feedstdout = StringIO()
            count = run_update(args.path, token, args.u, exclude)
            sys.stdout = old_stdout
            feed_bytes = feedstdout.getvalue().encode("utf-8")
            out = base64.b64encode(feed_bytes).decode("utf-8")

            body = {
                "type": "diff_count",
                "diff_count": count
            }
            update_frontend(f'{args.frontend}/api/overview/summary', body)

            body = {
                "type": "update",
                "feed": out
            }
            update_frontend(f'{args.frontend}/api/feed/update', body)

        else:
            run_update(args.path, token, args.u, exclude)


if __name__ == "__main__":
    start()
