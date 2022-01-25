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

    (opts, _) = parser.parse_args()

    def run_documentation(configpath,outpath,tenantname):

        now = datetime.now()
        current_date = now.strftime("%d/%m/%Y %H:%M:%S")

        # Create or clear markdown file
        md_file(outpath)

        # Document App Configuration
        document_configs(f'{configpath}/App Configuration',outpath,'App Configuration')

        # Document profiles
        document_configs(f'{configpath}/Device Configurations',outpath,'Configuration Profiles')

        # Document compliance
        document_configs(f'{configpath}/Compliance Policies/Policies',outpath,'Compliance Policies')

        # Message Templates
        document_configs(f'{configpath}/Compliance Policies/Message Templates',outpath,'Message Templates')

        # Document Intents
        document_management_intents(f'{configpath}/Management Intents/',outpath,'Management Intents')

        # Document Settings Catalog
        document_configs(f'{configpath}/Settings Catalog',outpath,'Settings Catalog')

        # Document Shell Scripts
        document_configs(f'{configpath}/Scripts/Shell',outpath,'Shell Scripts')

        # Document Powershell Scripts
        document_configs(f'{configpath}/Scripts/Powershell',outpath,'Powershell Scripts')

        # Document Apple Enrollment Profiles
        document_configs(f'{configpath}/Enrollment Profiles/Apple',outpath,'Apple Enrollment Profiles')

        # Document Windows Enrollment Profiles
        document_configs(f'{configpath}/Enrollment Profiles/Windows',outpath,'Windows Enrollment Profiles')

        # Document filters
        document_configs(f'{configpath}/Filters',outpath,'Filters')

        document = markdown_toclify(input_file=outpath,back_to_top=True,exclude_h=[3])
        with open(outpath, 'w') as doc:
            l1='# MEM Documentation \n\n'
            l2='This document contains documentation of all configurations exported by the IntuneCD tool \n\n'
            l3=f'**Tenant:** {tenantname} \n\n'
            l4=f'**Document updated on:** {current_date} \n\n'
            doc.writelines([l1,l2,l3,l4,document])

    run_documentation(opts.path,opts.outpath,opts.tenantname)

if __name__ == '__main__':
    start()