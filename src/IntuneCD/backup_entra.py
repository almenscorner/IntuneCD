# -*- coding: utf-8 -*-
def backup_entra(results, path, output, token, azure_token, args, exclude):
    """
    Imports all the backup functions and runs them
    """
    if args.interactiveauth:
        from .backup.Entra.backup_deviceRegistrationPolicy import savebackup

        results.append(savebackup(path, output, token))

    else:
        print(
            "***Device Registration Policy is only available with interactive auth***"
        )

    # Payloads that uses Graph API's

    if "entraAuthenticationMethods" not in exclude:
        from .backup.Entra.backup_authenticationMethods import savebackup

        results.append(savebackup(path, output, token))

    if "entraAuthorizationPolicy" not in exclude:
        from .backup.Entra.backup_authorizationPolicy import savebackup

        results.append(savebackup(path, output, token))

    if "entraAuthenticationFlowsPolicy" not in exclude:
        from .backup.Entra.backup_authenticationFlowsPolicy import savebackup

        results.append(savebackup(path, output, token))

    if "entraDomains" not in exclude:
        from .backup.Entra.backup_domains import savebackup

        results.append(savebackup(path, output, token))

    if "entraExternalIdentitiesPolicy" not in exclude:
        from .backup.Entra.backup_externalIdentitiesPolicy import savebackup

        results.append(savebackup(path, output, token))

    if "entraB2BPolicy" not in exclude:
        from .backup.Entra.backup_b2bPolicy import savebackup

        results.append(savebackup(path, output, azure_token))

    if "entraApplications" not in exclude:
        from .backup.Entra.backup_applications import savebackup

        results.append(savebackup(path, output, token))

    if "entraGroupSettings" not in exclude:
        from .backup.Entra.backup_groupSettings import savebackup

        results.append(savebackup(path, output, token))

    if "entraSecurityDefaults" not in exclude:
        from .backup.Entra.backup_securityDefaults import savebackup

        results.append(savebackup(path, output, token))

    if "entraSSPR" not in exclude:
        from .backup.Entra.backup_SSPR import savebackup

        results.append(savebackup(path, output, azure_token))

    if "entraRoamingSettings" not in exclude:
        from .backup.Entra.backup_roamingSettings import savebackup

        results.append(savebackup(path, output, azure_token))
