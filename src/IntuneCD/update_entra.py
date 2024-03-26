# -*- coding: utf-8 -*-
def update_entra(diff_summary, path, token, azure_token, report, args, exclude):
    """
    Imports all the update functions and runs them
    """

    params = {
        "path": path,
        "token": token,
        "report": report,
        "exclude": exclude,
        "azure_token": azure_token,
    }
    if args.interactiveauth:
        from .update.Entra.DeviceRegistration import (
            DeviceRegistrationPolicyUpdateModule,
        )

        diff_summary.append(DeviceRegistrationPolicyUpdateModule(**params).main())
    else:
        print(
            "***Device Registration Policy is only available with interactive auth***"
        )

    if "entraAuthenticationMethodsPolicy" not in exclude:
        from .update.Entra.AuthenticationMethodsPolicy import (
            AuthenticationMethodsPolicyUpdateModule,
        )

        diff_summary.append(AuthenticationMethodsPolicyUpdateModule(**params).main())

    if "entraAuthenticationMethodsConfigurations" not in exclude:
        from .update.Entra.AuthenticationMethodsConfigurations import (
            AuthenticationMethodsConfigurationsUpdateModule,
        )

        diff_summary.append(
            AuthenticationMethodsConfigurationsUpdateModule(**params).main()
        )

    if "entraAuthorizationPolicy" not in exclude:
        from .update.Entra.AuthorizationPolicy import AuthorizationPolicyUpdateModule

        diff_summary.append(AuthorizationPolicyUpdateModule(**params).main())

    if "entraAuthenticationFlowsPolicy" not in exclude:
        from .update.Entra.AuthenticationFlows import (
            AuthenticationFlowsPolicyUpdateModule,
        )

        diff_summary.append(AuthenticationFlowsPolicyUpdateModule(**params).main())

    if "entraExternalIdentitiesPolicy" not in exclude:
        from .update.Entra.ExternalIdentitiesPolicy import (
            ExternalIdentitiesPolicyUpdateModule,
        )

        diff_summary.append(ExternalIdentitiesPolicyUpdateModule(**params).main())

    if "entraB2BPolicy" not in exclude:
        from .update.Entra.B2B import B2BUpdateModule

        diff_summary.append(B2BUpdateModule(**params).main())

    if "entraDomains" not in exclude:
        from .update.Entra.Domains import DomainsUpdateModule

        diff_summary.append(DomainsUpdateModule(**params).main())

    if "entraGroupSettings" not in exclude:
        from .update.Entra.GroupSettings import GroupSettingsUpdateModule

        diff_summary.append(GroupSettingsUpdateModule(**params).main())

    if "entraSecurityDefaults" not in exclude:
        from .update.Entra.SecurityDefaults import SecurityDefaultsUpdateModule

        diff_summary.append(SecurityDefaultsUpdateModule(**params).main())

    if "entraRoamingSettings" not in exclude:
        from .update.Entra.RoamingSettings import RoamingSettingsUpdateModule

        diff_summary.append(RoamingSettingsUpdateModule(**params).main())

    if "entraSSPR" not in exclude:
        from .update.Entra.SSPR import SSPRUpdateModule

        diff_summary.append(SSPRUpdateModule(**params).main())
