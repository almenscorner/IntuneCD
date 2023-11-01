# -*- coding: utf-8 -*-
from .intunecdlib.documentation_functions import document_configs


def document_entra(configpath, outpath, maxlength, split, cleanup, decode):
    """
    This function is used to document Entra settings.
    """
    document_configs(
        f"{configpath}/Entra/Applications",
        outpath,
        "Applications",
        maxlength,
        split,
        cleanup,
        decode,
    )

    document_configs(
        f"{configpath}/Entra/Authentication Methods",
        outpath,
        "Authentication Methods",
        maxlength,
        split,
        cleanup,
        decode,
    )

    document_configs(
        f"{configpath}/Entra/Authentication Flows Policy",
        outpath,
        "Authentication Flows Policy",
        maxlength,
        split,
        cleanup,
        decode,
    )

    document_configs(
        f"{configpath}/Entra/Authorization Policy",
        outpath,
        "Authorization Policy",
        maxlength,
        split,
        cleanup,
        decode,
    )

    document_configs(
        f"{configpath}/Entra/Device Registration Policy",
        outpath,
        "Device Registration Policy",
        maxlength,
        split,
        cleanup,
        decode,
    )

    document_configs(
        f"{configpath}/Entra/Domains",
        outpath,
        "Domains",
        maxlength,
        split,
        cleanup,
        decode,
    )

    document_configs(
        f"{configpath}/Entra/External Collaboration Settings",
        outpath,
        "External Collaboration Settings",
        maxlength,
        split,
        cleanup,
        decode,
    )

    document_configs(
        f"{configpath}/Entra/Group Settings",
        outpath,
        "Group Settings",
        maxlength,
        split,
        cleanup,
        decode,
    )

    document_configs(
        f"{configpath}/Entra/Password Reset Policies",
        outpath,
        "Password Reset Policies",
        maxlength,
        split,
        cleanup,
        decode,
    )

    document_configs(
        f"{configpath}/Entra/Roaming Settings",
        outpath,
        "Roaming Settings",
        maxlength,
        split,
        cleanup,
        decode,
    )

    document_configs(
        f"{configpath}/Entra/Security Defaults",
        outpath,
        "Security Defaults",
        maxlength,
        split,
        cleanup,
        decode,
    )
