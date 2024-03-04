# -*- coding: utf-8 -*-
from .intunecdlib.documentation_functions import (
    document_configs,
    document_management_intents,
)


def document_intune(configpath, outpath, maxlength, split, cleanup, decode):
    """
    This function is used to document Intune configuration.
    """

    # Document App Configuration
    document_configs(
        f"{configpath}/App Configuration",
        outpath,
        "App Configuration",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document App Protection
    document_configs(
        f"{configpath}/App Protection",
        outpath,
        "App Protection",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Apple Push Notification
    document_configs(
        f"{configpath}/Apple Push Notification",
        outpath,
        "Apple Push Notification",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Apple VPP Tokens
    document_configs(
        f"{configpath}/Apple VPP Tokens",
        outpath,
        "Apple VPP Tokens",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document iOS Applications
    document_configs(
        f"{configpath}/Applications/iOS",
        outpath,
        "iOS Applications",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document macOS Applications
    document_configs(
        f"{configpath}/Applications/macOS",
        outpath,
        "macOS Applications",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Android Applications
    document_configs(
        f"{configpath}/Applications/Android",
        outpath,
        "Android Applications",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Windows Applications
    document_configs(
        f"{configpath}/Applications/Windows",
        outpath,
        "Windows Applications",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Web Apps
    document_configs(
        f"{configpath}/Applications/Web App",
        outpath,
        "Web Applications",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Office Suite apps
    document_configs(
        f"{configpath}/Applications/Office Suite",
        outpath,
        "Office Suite Applications",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document compliance
    document_configs(
        f"{configpath}/Compliance Policies/Policies",
        outpath,
        "Compliance Policies",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Compliance Scripts
    document_configs(
        f"{configpath}/Compliance Policies/Scripts",
        outpath,
        "Compliance Scripts",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Message Templates
    document_configs(
        f"{configpath}/Compliance Policies/Message Templates",
        outpath,
        "Message Templates",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Conditional Access
    document_configs(
        f"{configpath}/Conditional Access",
        outpath,
        "Conditional Access",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document profiles
    document_configs(
        f"{configpath}/Device Configurations",
        outpath,
        "Configuration Profiles",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Device Management Settings
    document_configs(
        f"{configpath}/Device Management Settings",
        outpath,
        "Device Management Settings",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Group Policy Configurations
    document_configs(
        f"{configpath}/Group Policy Configurations",
        outpath,
        "Group Policy Configurations",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Apple Enrollment Profiles
    document_configs(
        f"{configpath}/Enrollment Profiles/Apple",
        outpath,
        "Apple Enrollment Profiles",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Windows Enrollment Profiles
    document_configs(
        f"{configpath}/Enrollment Profiles/Windows",
        outpath,
        "Windows Enrollment Profiles",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Enrollment Status Page profiles
    document_configs(
        f"{configpath}/Enrollment Profiles/Windows/ESP",
        outpath,
        "Enrollment Status Page",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Enrollment Configurations
    document_configs(
        f"{configpath}/Enrollment Configurations",
        outpath,
        "Enrollment Configurations",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Device Categories
    document_configs(
        f"{configpath}/Device Categories",
        outpath,
        "Device Categories",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document filters
    document_configs(
        f"{configpath}/Filters",
        outpath,
        "Filters",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Managed Google Play
    document_configs(
        f"{configpath}/Managed Google Play",
        outpath,
        "Managed Google Play",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Intents
    document_management_intents(
        f"{configpath}/Management Intents/", outpath, "Management Intents", split
    )

    # Document Partner Connections
    document_configs(
        f"{configpath}/Partner Connections/",
        outpath,
        "Partner Connections",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Proactive Remediations
    document_configs(
        f"{configpath}/Proactive Remediations",
        outpath,
        "Proactive Remediations",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Shell Scripts
    document_configs(
        f"{configpath}/Scripts/Shell",
        outpath,
        "Shell Scripts",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Custom Attributes
    document_configs(
        f"{configpath}/Custom Attributes",
        outpath,
        "Custom Attributes",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Powershell Scripts
    document_configs(
        f"{configpath}/Scripts/Powershell",
        outpath,
        "Powershell Scripts",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Settings Catalog
    document_configs(
        f"{configpath}/Settings Catalog",
        outpath,
        "Settings Catalog",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Windows Driver Update Profiles
    document_configs(
        f"{configpath}/Driver Updates",
        outpath,
        "Windows Driver Updates",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Windows Feature Update Profiles
    document_configs(
        f"{configpath}/Feature Updates",
        outpath,
        "Windows Feature Updates",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Windows Quality Update Profiles
    document_configs(
        f"{configpath}/Quality Updates",
        outpath,
        "Windows Quality Updates",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Roles
    document_configs(
        f"{configpath}/Roles",
        outpath,
        "Roles",
        maxlength,
        split,
        cleanup,
        decode,
    )

    # Document Scope Tags
    document_configs(
        f"{configpath}/Scope Tags",
        outpath,
        "Scope Tags",
        maxlength,
        split,
        cleanup,
        decode,
    )
