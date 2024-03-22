# -*- coding: utf-8 -*-
def backup_entra(results, path, output, token, azure_token, args, exclude):
    """
    Imports all the backup functions and runs them
    """

    params = {
        "token": token,
        "azure_token": azure_token,
        "path": path,
        "filetype": output,
        "exclude": ["assignments"],
    }

    if args.interactiveauth:
        from .backup.Entra.DeviceRegistration import DeviceRegistrationBackupModule

        results.append(DeviceRegistrationBackupModule(**params).main())

    else:
        print(
            "***Device Registration Policy is only available with interactive auth***"
        )

    if "entraApplications" not in exclude:
        from .backup.Entra.Applications import ApplicationsBackupModule

        results.append(ApplicationsBackupModule(**params).main())

    if "entraAuthenticationMethods" not in exclude:
        from .backup.Entra.AuthenticationMethods import (
            AuthenticationMethodsBackupModule,
        )

        results.append(AuthenticationMethodsBackupModule(**params).main())

    if "entraAuthorizationPolicy" not in exclude:
        from .backup.Entra.AuthorizationPolicy import AuthorizationPolicyBackupModule

        results.append(AuthorizationPolicyBackupModule(**params).main())

    if "entraAuthenticationFlowsPolicy" not in exclude:
        from .backup.Entra.AuthenticationFlows import AuthenticationFlowsBackupModule

        results.append(AuthenticationFlowsBackupModule(**params).main())

    if "entraDomains" not in exclude:
        from .backup.Entra.Domains import DomainsBackupModule

        results.append(DomainsBackupModule(**params).main())

    if "entraExternalIdentitiesPolicy" not in exclude:
        from .backup.Entra.ExternalIdentities import (
            ExternalIdentitiesPolicyBackupModule,
        )

        results.append(ExternalIdentitiesPolicyBackupModule(**params).main())

    if "entraB2BPolicy" not in exclude:
        from .backup.Entra.B2B import B2BPolicyBackupModule

        results.append(B2BPolicyBackupModule(**params).main())

    if "entraGroupSettings" not in exclude:
        from .backup.Entra.GroupSettings import GroupSettingsBackupModule

        results.append(GroupSettingsBackupModule(**params).main())

    if "entraSecurityDefaults" not in exclude:
        from .backup.Entra.SecurityDefaults import SecurityDefaultsBackupModule

        results.append(SecurityDefaultsBackupModule(**params).main())

    if "entraSSPR" not in exclude:
        from .backup.Entra.SSPR import SSPRBackupModule

        results.append(SSPRBackupModule(**params).main())

    if "entraRoamingSettings" not in exclude:
        from .backup.Entra.RoamingSettings import RoamingSettingsBackupModule

        results.append(RoamingSettingsBackupModule(**params).main())
