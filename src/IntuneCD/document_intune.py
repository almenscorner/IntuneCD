# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import json

from .intunecdlib.documentation_functions import (
    document_configs,
    document_management_intents,
    document_settings_catalog,
)
from .decorators import time_command


@time_command()
def document_intune(
    configpath,
    outpath,
    maxlength,
    split,
    cleanup,
    decode,
    split_per_config,
    max_workers,
    enrich_documentation=False,
):
    """
    This function is used to document Intune configuration using threading.

    :param configpath: Path where backup files are stored
    :param outpath: Path to save the Markdown documentation
    :param maxlength: Maximum length of values in the documentation
    :param split: Determines if documentation should be split into multiple files
    :param cleanup: Remove empty values from documentation
    :param decode: Decode base64 values
    :param split_per_config: Whether to split each config into its own Markdown file
    :param max_workers: Maximum number of concurrent threads
    :param enrich_documentation: Whether to enrich Settings Catalog documentation with additional details
    """

    # Ensure the output directory exists
    # os.makedirs(outpath, exist_ok=True)

    # List of documentation tasks
    doc_tasks = [
        ("App Configuration", "App Configuration"),
        ("App Protection", "App Protection"),
        ("Apple Push Notification", "Apple Push Notification"),
        ("Apple VPP Tokens", "Apple VPP Tokens"),
        ("Applications/iOS", "iOS Applications"),
        ("Applications/macOS", "macOS Applications"),
        ("Applications/Android", "Android Applications"),
        ("Applications/Windows", "Windows Applications"),
        ("Applications/Web App", "Web Applications"),
        ("Applications/Office Suite", "Office Suite Applications"),
        ("Compliance Policies/Policies", "Compliance Policies"),
        ("Compliance Policies/Scripts", "Compliance Scripts"),
        ("Compliance Policies/Message Templates", "Message Templates"),
        ("Conditional Access", "Conditional Access"),
        ("Device Configurations", "Configuration Profiles"),
        ("Device Management Settings", "Device Management Settings"),
        ("Group Policy Configurations", "Group Policy Configurations"),
        ("Enrollment Profiles/Apple", "Apple Enrollment Profiles"),
        ("Enrollment Profiles/Windows", "Windows Enrollment Profiles"),
        ("Enrollment Profiles/Windows/ESP", "Enrollment Status Page"),
        ("Enrollment Configurations", "Enrollment Configurations"),
        ("Device Categories", "Device Categories"),
        ("Filters", "Filters"),
        ("Managed Google Play", "Managed Google Play"),
        ("Partner Connections", "Partner Connections"),
        ("Proactive Remediations", "Proactive Remediations"),
        ("Scripts/Shell", "Shell Scripts"),
        ("Custom Attributes", "Custom Attributes"),
        ("Scripts/Powershell", "Powershell Scripts"),
        ("Settings Catalog", "Settings Catalog"),
        ("Driver Updates", "Windows Driver Updates"),
        ("Feature Updates", "Windows Feature Updates"),
        ("Quality Updates", "Windows Quality Updates"),
        ("Roles", "Roles"),
        ("Scope Tags", "Scope Tags"),
    ]

    # sort doc_tasks alphabetically
    doc_tasks = sorted(doc_tasks, key=lambda x: x[1])

    settings_lookup = None
    categories_lookup = None

    if enrich_documentation:
        settings_lookup = {}
        categories_lookup = {}

        settings_path = os.path.join(configpath, "configurationSettings.json")
        categories_path = os.path.join(configpath, "configurationCategories.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                settings_json = json.load(f)
        if os.path.exists(categories_path):
            with open(categories_path, "r", encoding="utf-8") as f:
                categories_json = json.load(f)

        # Build lookup dictionaries for enrichment
        if settings_json:
            for s in settings_json.get("value", []):
                settings_lookup[s.get("id")] = s
        if categories_json:
            for c in categories_json.get("value", []):
                categories_lookup[c.get("id")] = c

    if split or split_per_config:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for task in doc_tasks:
                # Submit Settings Catalog with enrichment if enabled
                if task[1] == "Settings Catalog" and enrich_documentation:
                    futures[executor.submit(
                        document_settings_catalog,
                        f"{configpath}/{task[0]}",
                        outpath,
                        task[1],
                        maxlength,
                        split,
                        split_per_config,
                        settings_lookup,
                        categories_lookup,
                    )] = task[1]
                else:
                    futures[executor.submit(
                        document_configs,
                        f"{configpath}/{task[0]}",
                        outpath,
                        task[1],
                        maxlength,
                        split,
                        cleanup,
                        decode,
                        split_per_config,
                    )] = task[1]

            for future in as_completed(futures):
                task_name = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing {task_name}: {e}")

    else:
        # Run sequentially if split options are disabled
        for task in doc_tasks:
            # Submit Settings Catalog with enrichment if enabled
            if task[1] == "Settings Catalog" and enrich_documentation:
                document_settings_catalog(
                    f"{configpath}/{task[0]}",
                    outpath,
                    task[1],
                    maxlength,
                    split,
                    split_per_config,
                    settings_lookup,
                    categories_lookup,
                )
            else:
                document_configs(
                    f"{configpath}/{task[0]}",
                    outpath,
                    task[1],
                    maxlength,
                    split,
                    cleanup,
                    decode,
                    split_per_config,
                )

    # **Run Management Intents Sequentially**
    document_management_intents(
        f"{configpath}/Management Intents/", outpath, "Management Intents", split
    )
