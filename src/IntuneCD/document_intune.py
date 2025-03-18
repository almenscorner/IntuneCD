# -*- coding: utf-8 -*-
from .intunecdlib.documentation_functions import (
    document_configs,
    document_management_intents,
)


def document_intune(
    configpath,
    outpath,
    maxlength,
    split,
    cleanup,
    decode,
    split_per_config,
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

    for task in sorted(doc_tasks):
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

    # Run document_management_intents() sequentially
    document_management_intents(
        f"{configpath}/Management Intents/", outpath, "Management Intents", split
    )
