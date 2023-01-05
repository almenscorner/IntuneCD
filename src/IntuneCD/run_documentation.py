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

This module contains the functions to run the documentation.
"""

import os
import json
import argparse

from datetime import datetime
from markdown_toclify import markdown_toclify
from .documentation_functions import document_configs, document_management_intents, md_file, get_md_files

REPO_DIR = os.environ.get("REPO_DIR")


def start():
    parser = argparse.ArgumentParser(description="Create markdown document from backup files")
    parser.add_argument("-p", "--path", help="Path to where the backup is saved, default is REPO_DIR", default=REPO_DIR)
    parser.add_argument(
        "-o", "--outpath", help="The path to save the document, default is REPO_DIR/README.md", default=f"{REPO_DIR}/README.md"
    )
    parser.add_argument("-t", "--tenantname", help="Name of the tenant")
    parser.add_argument(
        "-i",
        "--intro",
        help="Introduction that will be added to the top of the document",
        default="This document contains documentation of all configurations exported by the IntuneCD tool",
    )
    parser.add_argument(
        "-j",
        "--jsondata",
        help='Lets you configure line 1-4 using a JSON string: "{\\"title\\": \\"demo\\", \\"intro\\": \\"demo\\", '
        '\\"tenant\\": \\"demo\\", \\"updated\\": \\"demo\\"}" ',
    )
    parser.add_argument(
        "-m",
        "--maxlength",
        help='Maximum length of the configuration value, values with a higher count will be displayed with "Value '
        'too long to display"',
        type=int,
    )
    parser.add_argument(
        "-s",
        "--split",
        help="Split the documentation into multiple files and create index.md in the configpath directory with a "
        "list of all files",
        action="store_true",
    )
    parser.add_argument("-c", "--cleanup", help="If set, will remove all table rows with an empty value", action="store_true")

    args = parser.parse_args()

    def run_documentation(configpath, outpath, tenantname, jsondata, maxlength, split, cleanup):

        now = datetime.now()
        current_date = now.strftime("%d/%m/%Y %H:%M:%S")

        if not split:
            md_file(outpath)

        # Document App Configuration
        document_configs(f"{configpath}/App Configuration", outpath, "App Configuration", maxlength, split, cleanup)

        # Document App Protection
        document_configs(f"{configpath}/App Protection", outpath, "App Protection", maxlength, split, cleanup)

        # Document Apple Push Notification
        document_configs(
            f"{configpath}/Apple Push Notification", outpath, "Apple Push Notification", maxlength, split, cleanup
        )

        # Document Apple VPP Tokens
        document_configs(f"{configpath}/Apple VPP Tokens", outpath, "Apple VPP Tokens", maxlength, split, cleanup)

        # Document iOS Applications
        document_configs(f"{configpath}/Applications/iOS", outpath, "iOS Applications", maxlength, split, cleanup)

        # Document macOS Applications
        document_configs(f"{configpath}/Applications/macOS", outpath, "macOS Applications", maxlength, split, cleanup)

        # Document Android Applications
        document_configs(f"{configpath}/Applications/Android", outpath, "Android Applications", maxlength, split, cleanup)

        # Document Windows Applications
        document_configs(f"{configpath}/Applications/Windows", outpath, "Windows Applications", maxlength, split, cleanup)

        # Document Web Apps
        document_configs(f"{configpath}/Applications/Web App", outpath, "Web Applications", maxlength, split, cleanup)

        # Document Office Suite apps
        document_configs(
            f"{configpath}/Applications/Office Suite", outpath, "Office Suite Applications", maxlength, split, cleanup
        )

        # Document compliance
        document_configs(
            f"{configpath}/Compliance Policies/Policies", outpath, "Compliance Policies", maxlength, split, cleanup
        )

        # Message Templates
        document_configs(
            f"{configpath}/Compliance Policies/Message Templates", outpath, "Message Templates", maxlength, split, cleanup
        )

        # Conditional Access
        document_configs(f"{configpath}/Conditional Access", outpath, "Conditional Access", maxlength, split, cleanup)

        # Document profiles
        document_configs(f"{configpath}/Device Configurations", outpath, "Configuration Profiles", maxlength, split, cleanup)

        # Document Group Policy Configurations
        document_configs(
            f"{configpath}/Group Policy Configurations", outpath, "Group Policy Configurations", maxlength, split, cleanup
        )

        # Document Apple Enrollment Profiles
        document_configs(
            f"{configpath}/Enrollment Profiles/Apple", outpath, "Apple Enrollment Profiles", maxlength, split, cleanup
        )

        # Document Windows Enrollment Profiles
        document_configs(
            f"{configpath}/Enrollment Profiles/Windows", outpath, "Windows Enrollment Profiles", maxlength, split, cleanup
        )

        # Document Enrollment Status Page profiles
        document_configs(
            f"{configpath}/Enrollment Profiles/Windows/ESP", outpath, "Enrollment Status Page", maxlength, split, cleanup
        )

        # Document filters
        document_configs(f"{configpath}/Filters", outpath, "Filters", maxlength, split, cleanup)

        # Managed Google Play
        document_configs(f"{configpath}/Managed Google Play", outpath, "Managed Google Play", maxlength, split, cleanup)

        # Document Intents
        document_management_intents(f"{configpath}/Management Intents/", outpath, "Management Intents", split)

        # Document Partner Connections
        document_configs(f"{configpath}/Partner Connections/", outpath, "Partner Connections", maxlength, split, cleanup)

        # Document Proactive Remediations
        document_configs(f"{configpath}/Proactive Remediations", outpath, "Proactive Remediations", maxlength, split, cleanup)

        # Document Shell Scripts
        document_configs(f"{configpath}/Scripts/Shell", outpath, "Shell Scripts", maxlength, split, cleanup)

        # Document Powershell Scripts
        document_configs(f"{configpath}/Scripts/Powershell", outpath, "Powershell Scripts", maxlength, split, cleanup)

        # Document Settings Catalog
        document_configs(f"{configpath}/Settings Catalog", outpath, "Settings Catalog", maxlength, split, cleanup)

        if jsondata:
            json_dict = json.loads(jsondata)
            if "title" in json_dict:
                title = json_dict["title"]
            else:
                title = "MEM Documentation"
            if "intro" in json_dict:
                intro = json_dict["intro"]
            else:
                intro = args.intro
            if "tenant" in json_dict:
                tenant = json_dict["tenant"]
            else:
                tenant = f"**Tenant:** {tenantname}"
            if "updated" in json_dict:
                updated = json_dict["updated"]
            else:
                updated = f"**Document updated on:**"
        else:
            title = "MEM Documentation"
            intro = args.intro
            tenant = f"**Tenant:** {tenantname}"
            updated = f"**Document updated on:**"

        if split:
            files = get_md_files(configpath)
            index_md = f"{configpath}/index.md"
            md_file(index_md)

            with open(index_md, "w") as doc:
                l1 = f"# {title} \n\n"
                l2 = f"{intro} \n\n"
                l3 = f"{tenant} \n\n"
                l4 = f"{updated} {current_date} \n\n"
                l5 = "## File index \n\n"
                doc.writelines([l1, l2, l3, l4, l5])
                for file in files:
                    doc.writelines(["[", str(file).split("/")[-1], "](", str(file).replace(" ", "%20"), ") \n\n"])

        else:
            document = markdown_toclify(input_file=outpath, back_to_top=True, exclude_h=[3])
            with open(outpath, "w") as doc:
                l1 = f"# {title} \n\n"
                l2 = f"{intro} \n\n"
                l3 = f"{tenant} \n\n"
                l4 = f"{updated} {current_date} \n\n"
                doc.writelines([l1, l2, l3, l4, document])

    run_documentation(args.path, args.outpath, args.tenantname, args.jsondata, args.maxlength, args.split, args.cleanup)


if __name__ == "__main__":
    start()
