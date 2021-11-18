#!/usr/bin/env python3

import os
from .get_authparams import getAuth

from optparse import OptionParser

REPO_DIR = os.environ.get("REPO_DIR")

def start():

    parser = OptionParser(description="Save backup of Intune configurations")
    parser.add_option(
        "-o", "--output", 
        help='The format backups will be saved as, valid options are json or yaml. Default is json',
        type=str,
        default = "json",
    )
    parser.add_option(
        "-p", "--path", 
        help='The path to which the configurations will be saved. Default value is $(Build.SourcesDirectory)',
        type=str,
        default = REPO_DIR,
    )
    parser.add_option(
        "-m", "--mode",
        help = ("The mode in which the script is run, 0 = devtoprod (backup from dev -> update to prod) "
                "uses os.environ DEV_TENANT_NAME, DEV_CLIENT_ID, DEV_CLIENT_SECRET, "
                "1 = standalone (backup from prod) uses os.environ TENANT_NAME, CLIENT_ID, CLIENT_SECRET"),
        type=int,
        default = 0
    )
    parser.add_option(
        "-a", "--localauth",
        help=("When this paramater is set, provide a path to a local dict file containing the following keys: "
                "params:TENANT_NAME, CLIENT_ID, CLIENT_SECRET when run in standalone mode and "
                "params:DEV_TENANT_NAME, DEV_CLIENT_ID, DEV_CLIENT_SECRET when run in devtoprod"),
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

    token = getAuth(selected_mode(opts.mode),opts.localauth,tenant="DEV")

    def run_backup(path,output,token):

        from .backup_profiles import savebackup
        savebackup(path,output,token)

        from .backup_configurationPolicies import savebackup
        savebackup(path,output,token)

        from .backup_compliance import savebackup
        savebackup(path,output,token)

        from .backup_notificationTemplate import savebackup
        savebackup(path,output,token)

        from .backup_appleEnrollmentProfile import savebackup
        savebackup(path,output,token)

        from .backup_windowsEnrollmentProfile import savebackup
        savebackup(path,output,token)

        from .backup_shellScripts import savebackup
        savebackup(path,output,token)

        from .backup_powershellScripts import savebackup
        savebackup(path,output,token)

        from .backup_AppProtection import savebackup
        savebackup(path,output,token)

        from .backup_appConfiguration import savebackup
        savebackup(path,output,token)

        from .backup_assignmentFilters import savebackup
        savebackup(path,output,token)

        from .backup_managementIntents import savebackup
        savebackup(path,output,token)

    if opts.output == 'json' or opts.output == 'yaml':
        if token is None:
            raise Exception("Token is empty, please check os.environ variables")
        else:
            run_backup(opts.path,opts.output,token)

    else:
        print('Please enter a valid output format, json or yaml') 

if __name__ == "__main__":
    start()