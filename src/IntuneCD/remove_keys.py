#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to remove keys from the data.
"""


def remove_keys(data):
    """
    This function removes keys from the data.
    :param data: The data to remove keys from.
    :return: The data with removed keys.
    """

    keys = {
        "id",
        "version",
        "topicIdentifier",
        "certificate",
        "createdDateTime",
        "lastModifiedDateTime",
        "isDefault",
        "isAssigned",
        "@odata.context",
        "scheduledActionConfigurations@odata.context",
        "scheduledActionsForRule@odata.context",
        "sourceId",
        "supportsScopeTags",
        "companyCodes",
        "isGlobalScript",
        "highestAvailableVersion",
        "token",
        "lastSyncDateTime",
        "isReadOnly",
        "secretReferenceValueId",
        "isEncrypted",
        "modifiedDateTime",
        "deployedAppCount",
    }
    for k in keys:
        data.pop(k, None)

    return data
