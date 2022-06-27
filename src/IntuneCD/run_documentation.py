#!/usr/bin/env python3

import os
from datetime import datetime
from .documentation_functions import document_configs,document_management_intents,md_file,get_md_files
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
    parser.add_option(
        '-m', '--maxlength',
        help = 'Maximum length of the configuration value, values with a higher count will be displayed with "Value too long to display"',
        type = int
    )
    parser.add_option(
        '-s', '--split',
        help = 'Split the documentation into multiple files and create index.md in the configpath directory with a list of all files',
    )

    (opts, _) = parser.parse_args()

    def run_documentation(configpath,outpath,tenantname,maxlength,split):

        now = datetime.now()
        current_date = now.strftime("%d/%m/%Y %H:%M:%S")

        if split == 'Y':
            split = True
        else:
            md_file(outpath)

        # Document App Configuration
        document_configs(f'{configpath}/App Configuration',outpath,'App Configuration',maxlength,split)

        # Document App Protection
        document_configs(f'{configpath}/App Protection',outpath,'App Protection',maxlength,split)

        # Document Apple Push Notification
        document_configs(f'{configpath}/Apple Push Notification',outpath,'Apple Push Notification',maxlength,split)

        # Document Apple VPP Tokens
        document_configs(f'{configpath}/Apple VPP Tokens',outpath,'Apple VPP Tokens',maxlength,split)

        # Document iOS Applications
        document_configs(f'{configpath}/Applications/iOS',outpath,'iOS Applications',maxlength,split)

        # Document macOS Applications
        document_configs(f'{configpath}/Applications/macOS',outpath,'macOS Applications',maxlength,split)

        # Document Android Applications
        document_configs(f'{configpath}/Applications/Android',outpath,'Android Applications',maxlength,split)

        # Document Windows Applications
        document_configs(f'{configpath}/Applications/Windows',outpath,'Windows Applications',maxlength,split)

        # Document Web Apps
        document_configs(f'{configpath}/Applications/Web App',outpath,'Web Applications',maxlength,split)

        # Document Office Suite apps
        document_configs(f'{configpath}/Applications/Office Suite',outpath,'Office Suite Applications',maxlength,split)

        # Document compliance
        document_configs(f'{configpath}/Compliance Policies/Policies',outpath,'Compliance Policies',maxlength,split)

        # Message Templates
        document_configs(f'{configpath}/Compliance Policies/Message Templates',outpath,'Message Templates',maxlength,split)

        # Document profiles
        document_configs(f'{configpath}/Device Configurations',outpath,'Configuration Profiles',maxlength,split)

        # Document Group Policy Configurations
        document_configs(f'{configpath}/Group Policy Configurations',outpath,'Group Policy Configurations',maxlength,split)

        # Document Apple Enrollment Profiles
        document_configs(f'{configpath}/Enrollment Profiles/Apple',outpath,'Apple Enrollment Profiles',maxlength,split)

        # Document Windows Enrollment Profiles
        document_configs(f'{configpath}/Enrollment Profiles/Windows',outpath,'Windows Enrollment Profiles',maxlength,split)

        # Document filters
        document_configs(f'{configpath}/Filters',outpath,'Filters',maxlength,split)

        # Managed Google Play
        document_configs(f'{configpath}/Managed Google Play',outpath,'Managed Google Play',maxlength,split)

        # Document Intents
        document_management_intents(f'{configpath}/Management Intents/',outpath,'Management Intents',split)

        #Document Partner Connections
        document_configs(f'{configpath}/Partner Connections/',outpath,'Partner Connections',maxlength,split)

        # Document Proactive Remediations
        document_configs(f'{configpath}/Proactive Remediations',outpath,'Proactive Remediations',maxlength,split)

        # Document Shell Scripts
        document_configs(f'{configpath}/Scripts/Shell',outpath,'Shell Scripts',maxlength,split)

        # Document Powershell Scripts
        document_configs(f'{configpath}/Scripts/Powershell',outpath,'Powershell Scripts',maxlength,split)

        # Document Settings Catalog
        document_configs(f'{configpath}/Settings Catalog',outpath,'Settings Catalog',maxlength,split)

        if split == True:
            files = get_md_files()
            index_md = f'{configpath}/index.md'
            md_file(index_md)

            with open(index_md, 'w') as doc:
                l1='# MEM Documentation \n\n'
                l2=f'{opts.intro} \n\n'
                l3=f'**Tenant:** {tenantname} \n\n'
                l4=f'**Document updated on:** {current_date} \n\n'
                l5='## File index \n\n'
                doc.writelines([l1,l2,l3,l4,l5])
                for file in files:
                    doc.writelines(['[',str(file).split('/')[-1],'](',str(file).replace(" ", "%20"),') \n\n'])

        else:
            document = markdown_toclify(input_file=outpath,back_to_top=True,exclude_h=[3])
            with open(outpath, 'w') as doc:
                l1='# MEM Documentation \n\n'
                l2=f'{opts.intro} \n\n'
                l3=f'**Tenant:** {tenantname} \n\n'
                l4=f'**Document updated on:** {current_date} \n\n'
                doc.writelines([l1,l2,l3,l4,document])

    run_documentation(opts.path,opts.outpath,opts.tenantname,opts.maxlength,opts.split)

if __name__ == '__main__':
    start()