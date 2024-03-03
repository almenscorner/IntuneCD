# -*- coding: utf-8 -*-
def update_intune(
    diff_summary,
    diff_count,
    path,
    token,
    assignment,
    report,
    create_groups,
    remove,
    exclude,
    args,
):
    """
    Imports all the update functions and runs them
    """

    from .intunecdlib.process_scope_tags import get_scope_tags

    if "ScopeTags" not in exclude:
        from .update.Intune.update_scopeTags import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )
        scope_tags = get_scope_tags(token)
    else:
        scope_tags = None

    if "AppConfigurations" not in exclude:
        from .update.Intune.update_appConfiguration import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "AppProtection" not in exclude:
        from .update.Intune.update_appProtection import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "ReusablePolicySettings" not in exclude:
        from .update.Intune.update_reusablePolicySettings import update

        diff_summary.append(update(path, token, report, remove))

    if "ComplianceScripts" not in exclude:
        from .update.Intune.update_complianceScripts import update

        diff_summary.append(update(path, token, report, remove, scope_tags))

    if "DeviceCompliancePolicies" not in exclude:
        from .update.Intune.update_compliancePolicies import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "Compliance" not in exclude:
        from .update.Intune.update_compliance import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "DeviceManagementSettings" not in exclude and args.interactiveauth is True:
        from .update.Intune.update_deviceManagementSettings import update

        diff_summary.append(update(path, token, report))
    else:
        print("-" * 90)
        print(
            "***Device Management Settings is only available with interactive auth***"
        )

    if "DeviceCategories" not in exclude:
        from .update.Intune.update_deviceCategories import update

        diff_summary.append(update(path, token, report, remove, scope_tags))

    if "NotificationTemplate" not in exclude:
        from .update.Intune.update_notificationTemplate import update

        diff_summary.append(update(path, token, report, remove, scope_tags))

    if "Profiles" not in exclude:
        from .update.Intune.update_profiles import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "GPOConfigurations" not in exclude:
        from .update.Intune.update_groupPolicyConfiguration import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "AppleEnrollmentProfile" not in exclude:
        from .update.Intune.update_appleEnrollmentProfile import update

        diff_summary.append(update(path, token, report))

    if "WindowsEnrollmentProfile" not in exclude:
        from .update.Intune.update_windowsEnrollmentProfile import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "EnrollmentStatusPage" not in exclude:
        from .update.Intune.update_enrollmentStatusPage import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "EnrollmentConfigurations" not in exclude:
        from .update.Intune.update_enrollmentConfigurations import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "Filters" not in exclude:
        from .update.Intune.update_assignmentFilter import update

        diff_summary.append(update(path, token, report, scope_tags))

    if "Intents" not in exclude:
        from .update.Intune.update_managementIntents import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "ProactiveRemediation" not in exclude:
        from .update.Intune.update_proactiveRemediation import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "PowershellScripts" not in exclude:
        from .update.Intune.update_powershellScripts import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "ShellScripts" not in exclude:
        from .update.Intune.update_shellScripts import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "CustomAttribute" not in exclude:
        from .update.Intune.update_customAttributeShellScript import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "ConfigurationPolicies" not in exclude:
        from .update.Intune.update_configurationPolicies import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "ConditionalAccess" not in exclude:
        from .update.Intune.update_conditionalAccess import update

        diff_count += update(path, token, report, remove)

    if "WindowsDriverUpdateProfiles" not in exclude:
        from .update.Intune.update_windowsDriverUpdates import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "windowsFeatureUpdates" not in exclude:
        from .update.Intune.update_windowsFeatureUpdates import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "windowsQualityUpdates" not in exclude:
        from .update.Intune.update_windowsQualityUpdates import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove, scope_tags)
        )

    if "Roles" not in exclude:
        from .update.Intune.update_roles import update

        diff_summary.append(update(path, token, report, remove, scope_tags))
