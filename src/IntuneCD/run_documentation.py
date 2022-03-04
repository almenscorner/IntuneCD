#!/usr/bin/env python3

import os
from datetime import datetime
from .documentation_functions import document_configs,document_management_intents,md_file
from markdown_toclify import markdown_toclify
from optparse import OptionParser

REPO_DIR = os.environ.get("REPO_DIR")

def start ():

    parser = OptionParser(description="Create markdown document from backup files")
    parser.add_option(
        "-p", "--path",
        help = 'Path to where the backup is saved, default is REPO_DIR',
        default = REPO_DIR
    )
    parser.add_option(
        "-o", "--outpath",
        help = 'The path to save the document, default is REPO_DIR/README.md',
        default = f'{REPO_DIR}/README.md'
    )
    parser.add_option(
        '-t', '--tenantname',
        help = 'Name of the tenant'
    )
    parser.add_option(
        '-i', '--intro',
        help = 'Introduction that will be added to the top of the document',
        default = 'This document contains documentation of all configurations exported by the IntuneCD tool'
    )

    (opts, _) = parser.parse_args()

    def run_documentation(configpath,outpath,tenantname):

        now = datetime.now()
        current_date = now.strftime("%d/%m/%Y %H:%M:%S")

        # Create or clear markdown file
        md_file(outpath)

        # Document App Configuration
        document_configs(f'{configpath}/App Configuration',outpath,'App Configuration')

        # Document App Protection
        document_configs(f'{configpath}/App Protection',outpath,'App Protection')

        # Document Apple Push Notification
        document_configs(f'{configpath}/Apple Push Notification',outpath,'Apple Push Notification')

        # Document Apple VPP Tokens
        document_configs(f'{configpath}/Apple VPP Tokens',outpath,'Apple VPP Tokens')

        # Document iOS Applications
        document_configs(f'{configpath}/Applications/iOS',outpath,'iOS Applications')

        # Document macOS Applications
        document_configs(f'{configpath}/Applications/macOS',outpath,'macOS Applications')

        # Document Android Applications
        document_configs(f'{configpath}/Applications/Android',outpath,'Android Applications')

        # Document Windows Applications
        document_configs(f'{configpath}/Applications/Windows',outpath,'Windows Applications')

        # Document Web Apps
        document_configs(f'{configpath}/Applications/Web App',outpath,'Web Applications')

        # Document Office Suite apps
        document_configs(f'{configpath}/Applications/Office Suite',outpath,'Office Suite Applications')

        # Document compliance
        document_configs(f'{configpath}/Compliance Policies/Policies',outpath,'Compliance Policies')

        # Message Templates
        document_configs(f'{configpath}/Compliance Policies/Message Templates',outpath,'Message Templates')

        # Document profiles
        document_configs(f'{configpath}/Device Configurations',outpath,'Configuration Profiles')

        # Document Apple Enrollment Profiles
        document_configs(f'{configpath}/Enrollment Profiles/Apple',outpath,'Apple Enrollment Profiles')

        # Document Windows Enrollment Profiles
        document_configs(f'{configpath}/Enrollment Profiles/Windows',outpath,'Windows Enrollment Profiles')

        # Document filters
        document_configs(f'{configpath}/Filters',outpath,'Filters')

        # Managed Google Play
        document_configs(f'{configpath}/Managed Google Play',outpath,'Managed Google Play')

        # Document Intents
        document_management_intents(f'{configpath}/Management Intents/',outpath,'Management Intents')

        #Document Partner Connections
        document_configs(f'{configpath}/Partner Connections/',outpath,'Partner Connections')

        # Document Proactive Remediations
        document_configs(f'{configpath}/Proactive Remediations',outpath,'Proactive Remediations')

        # Document Shell Scripts
        document_configs(f'{configpath}/Scripts/Shell',outpath,'Shell Scripts')

        # Document Powershell Scripts
        document_configs(f'{configpath}/Scripts/Powershell',outpath,'Powershell Scripts')

        # Document Settings Catalog
        document_configs(f'{configpath}/Settings Catalog',outpath,'Settings Catalog')

        document = markdown_toclify(input_file=outpath,back_to_top=True,exclude_h=[3])
        with open(outpath, 'w') as doc:
            l1='# MEM Documentation \n\n'
            l2=f'{opts.intro} \n\n'
            l3=f'**Tenant:** {tenantname} \n\n'
            l4=f'**Document updated on:** {current_date} \n\n'
            doc.writelines([l1,l2,l3,l4,document])

    run_documentation(opts.path,opts.outpath,opts.tenantname)

if __name__ == '__main__':
    start()