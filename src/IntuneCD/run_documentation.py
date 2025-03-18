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

This module contains the functions to run the documentation.
"""

import argparse
import json
import os
from datetime import datetime

from markdown_toclify import markdown_toclify

from .document_entra import document_entra
from .document_intune import document_intune
from .intunecdlib.documentation_functions import (
    get_md_files,
    md_file,
    write_type_header,
)

REPO_DIR = os.environ.get("REPO_DIR")


def start():
    parser = argparse.ArgumentParser(
        description="Create markdown document from backup files"
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Path to where the backup is saved, default is REPO_DIR",
        default=REPO_DIR,
    )
    parser.add_argument(
        "-o",
        "--outpath",
        help="The path to save the document, default is REPO_DIR/README.md",
        default=f"{REPO_DIR}/README.md",
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
    parser.add_argument(
        "-c",
        "--cleanup",
        help="If set, will remove all table rows with an empty value",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--decode",
        help="If set, will decode all base64 encoded values",
        action="store_true",
    )
    parser.add_argument(
        "--split-per-config",
        help="If set, will split the documentation per configuration and save resulting MD file in /docs in the configpath directory",
        action="store_true",
    )

    args = parser.parse_args()

    def run_documentation(
        configpath,
        outpath,
        tenantname,
        jsondata,
        maxlength,
        split,
        cleanup,
        decode,
        split_per_config,
    ):
        now = datetime.now()
        current_date = now.strftime("%d/%m/%Y %H:%M:%S")

        if not split:
            md_file(outpath)

        write_type_header(split, outpath, "Intune")

        document_intune(
            configpath,
            outpath,
            maxlength,
            split,
            cleanup,
            decode,
            split_per_config,
        )

        write_type_header(split, outpath, "Entra")

        document_entra(configpath, outpath, maxlength, split, cleanup, decode)

        if jsondata:
            json_dict = json.loads(jsondata)
            if "title" in json_dict:
                title = json_dict["title"]
            else:
                title = "Intune Documentation"
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
            title = "Intune Documentation"
            intro = args.intro
            tenant = f"**Tenant:** {tenantname}"
            updated = f"**Document updated on:**"

        if split or split_per_config:
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
                    doc.writelines(
                        [
                            "[",
                            str(file).split("/")[-1],
                            "](",
                            str(file).replace(" ", "%20"),
                            ") \n\n",
                        ]
                    )

        else:
            document = markdown_toclify(input_file=outpath, back_to_top=True)
            with open(outpath, "w") as doc:
                l1 = f"# {title} \n\n"
                l2 = f"{intro} \n\n"
                l3 = f"{tenant} \n\n"
                l4 = f"{updated} {current_date} \n\n"
                doc.writelines([l1, l2, l3, l4, document])

    run_documentation(
        args.path,
        args.outpath,
        args.tenantname,
        args.jsondata,
        args.maxlength,
        args.split,
        args.cleanup,
        args.decode,
        args.split_per_config,
    )


if __name__ == "__main__":
    start()
