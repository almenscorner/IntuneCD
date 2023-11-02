# -*- coding: utf-8 -*-
def update_entra(diff_summary, path, token, azure_token, report, args, exclude):
    """
    Imports all the update functions and runs them
    """
    if args.interactiveauth:
        from .update.Entra.update_deviceRegistrationPolicy import update

        diff_summary.append(update(path, token, report))
    else:
        print(
            "***Device Registration Policy is only available with interactive auth***"
        )

    if "entraAuthenticationMethodsPolicy" not in exclude:
        from .update.Entra.update_authenticationMethodsPolicy import update

        diff_summary.append(update(path, token, report))

    if "entraAuthenticationMethodsConfigurations" not in exclude:
        from .update.Entra.update_authenticationMethodsConfigurations import update

        diff_summary.append(update(path, token, report))

    if "entraAuthorizationPolicy" not in exclude:
        from .update.Entra.update_authorizationPolicy import update

        diff_summary.append(update(path, token, report))

    if "entraAuthenticationFlowsPolicy" not in exclude:
        from .update.Entra.update_authenticationFlowsPolicy import update

        diff_summary.append(update(path, token, report))

    if "entraDomains" not in exclude:
        from .update.Entra.update_domains import update

        diff_summary.append(update(path, token, report))

    if "entraExternalIdentitiesPolicy" not in exclude:
        from .update.Entra.update_externalIdentitiesPolicy import update

        diff_summary.append(update(path, token, report))

    if "entraB2BPolicy" not in exclude:
        from .update.Entra.update_b2bPolicy import update

        diff_summary.append(update(path, azure_token, report))

    if "entraGroupSettings" not in exclude:
        from .update.Entra.update_groupSettings import update

        diff_summary.append(update(path, token, report))

    if "entraSecurityDefaults" not in exclude:
        from .update.Entra.update_securityDefaults import update

        diff_summary.append(update(path, token, report))

    if "entraRoamingSettings" not in exclude:
        from .update.Entra.update_roamingSettings import update

        diff_summary.append(update(path, azure_token, report))

    if "entraSSPR" not in exclude:
        from .update.Entra.update_SSPR import update

        diff_summary.append(update(path, azure_token, report))
