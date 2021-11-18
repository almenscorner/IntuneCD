#!/usr/bin/env python3

import os
from .get_authparams import getAuth

from optparse import OptionParser

REPO_DIR = os.environ.get("REPO_DIR")

def start():

    parser = OptionParser(description="Update Intune configurations with values from backup")
    parser.add_option(
        "-p", "--path", 
        help='The path to which the configurations are saved. Default value is $(Build.SourcesDirectory)',
        default = REPO_DIR,
    )
    parser.add_option(
        "-m", "--mode",
        help = ("The mode in which the script is run, 0 = devtoprod (backup from dev -> update to prod) "
                "uses os.environ PROD_TENANT_NAME, PROD_CLIENT_ID, PROD_CLIENT_SECRET, "
                "1 = standalone (backup from prod) uses os.environ TENANT_NAME, CLIENT_ID, CLIENT_SECRET"),
        type=int,
        default = 0
    )
    parser.add_option(
        "-a", "--localauth",
        help=("When this paramater is set, provide a path to a local dict file containing the following keys: "
               "params:TENANT_NAME, CLIENT_ID, CLIENT_SECRET when run in standalone mode and "
               "params:PROD_TENANT_NAME, PROD_CLIENT_ID, PROD_CLIENT_SECRET when run in devtoprod"),
        type=str
    )    

    (opts, _) = parser.parse_args()

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

    token = getAuth(selected_mode(opts.mode),opts.localauth,tenant="PROD")   

    def run_update(path,token):

        from .update_profiles import update
        update(path,token)

        from .update_compliance import update
        update(path,token)

        from .update_appConfiguration import update
        update(path,token)

        from .update_appProtection import update
        update(path,token)

        from .update_appleEnrollmentProfile import update
        update(path,token)

        from .update_windowsEnrollmentProfile import update
        update(path,token)

        from .update_shellScripts import update
        update(path,token)

        from .update_powershellScripts import update
        update(path,token)

        from .update_configurationPolicies import update
        update(path,token)

        from .update_assignmentFilter import update
        update(path,token)

        from .update_notificationTemplate import update
        update(path,token)

        from .update_managementIntents import update
        update(path,token)

    if token is None:
        raise Exception("Token is empty, please check os.environ variables")
    else:
        run_update(opts.path,token)

if __name__ == "__main__":
    start()