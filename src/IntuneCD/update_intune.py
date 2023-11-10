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
    if "AppConfigurations" not in exclude:
        from .update.Intune.update_appConfiguration import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "AppProtection" not in exclude:
        from .update.Intune.update_appProtection import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "Compliance" not in exclude:
        from .update.Intune.update_compliance import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
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

        diff_summary.append(update(path, token, report, remove))

    if "NotificationTemplate" not in exclude:
        from .update.Intune.update_notificationTemplate import update

        diff_summary.append(update(path, token, report, remove))

    if "Profiles" not in exclude:
        from .update.Intune.update_profiles import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "GPOConfigurations" not in exclude:
        from .update.Intune.update_groupPolicyConfiguration import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "AppleEnrollmentProfile" not in exclude:
        from .update.Intune.update_appleEnrollmentProfile import update

        diff_summary.append(update(path, token, report))

    if "WindowsEnrollmentProfile" not in exclude:
        from .update.Intune.update_windowsEnrollmentProfile import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "EnrollmentStatusPage" not in exclude:
        from .update.Intune.update_enrollmentStatusPage import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "EnrollmentConfigurations" not in exclude:
        from .update.Intune.update_enrollmentConfigurations import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "Filters" not in exclude:
        from .update.Intune.update_assignmentFilter import update

        diff_summary.append(update(path, token, report))

    if "Intents" not in exclude:
        from .update.Intune.update_managementIntents import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "ProactiveRemediation" not in exclude:
        from .update.Intune.update_proactiveRemediation import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "PowershellScripts" not in exclude:
        from .update.Intune.update_powershellScripts import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "ShellScripts" not in exclude:
        from .update.Intune.update_shellScripts import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "CustomAttribute" not in exclude:
        from .update.Intune.update_customAttributeShellScript import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "ConfigurationPolicies" not in exclude:
        from .update.Intune.update_configurationPolicies import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "ConditionalAccess" not in exclude:
        from .update.Intune.update_conditionalAccess import update

        diff_count += update(path, token, report, remove)

    if "WindowsDriverUpdateProfiles" not in exclude:
        from .update.Intune.update_windowsDriverUpdates import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "windowsFeatureUpdates" not in exclude:
        from .update.Intune.update_windowsFeatureUpdates import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )

    if "windowsQualityUpdates" not in exclude:
        from .update.Intune.update_windowsQualityUpdates import update

        diff_summary.append(
            update(path, token, assignment, report, create_groups, remove)
        )
