# -*- coding: utf-8 -*-
def update_intune(
    diff_summary,
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
    params = {
        "path": path,
        "token": token,
        "exclude": exclude,
        "report": report,
        "remove": remove,
        "create_groups": create_groups,
        "handle_assignment": assignment,
    }

    from .intunecdlib.process_scope_tags import ProcessScopeTags

    process_scope_tags = ProcessScopeTags(token)

    if "ScopeTags" not in exclude:
        from .update.Intune.ScopeTags import ScopeTagsUpdateModule

        diff_summary.append(ScopeTagsUpdateModule(**params).main())
        scope_tags = process_scope_tags.get_scope_tags()
    else:
        scope_tags = None

    params["scope_tags"] = scope_tags

    if "Filters" not in exclude:
        from .update.Intune.Filters import FiltersUpdateModule

        diff_summary.append(FiltersUpdateModule(**params).main())

    if "AppConfigurations" not in exclude:
        from .update.Intune.AppConfiguration import AppConfigurationUpdateModule

        diff_summary.append(AppConfigurationUpdateModule(**params).main())

    if "AppProtection" not in exclude:
        from .update.Intune.AppProtection import AppProtectionUpdateModule

        diff_summary.append(AppProtectionUpdateModule(**params).main())

    if "NotificationTemplate" not in exclude:
        from .update.Intune.NotificationTemplate import NotificationTemplateUpdateModule

        diff_summary.append(NotificationTemplateUpdateModule(**params).main())

    if "ReusablePolicySettings" not in exclude:
        from .update.Intune.ReusableSettings import ReusableSettingsUpdateModule

        diff_summary.append(ReusableSettingsUpdateModule(**params).main())

    if "ComplianceScripts" not in exclude:
        from .update.Intune.ComplianceScripts import ComplianceScriptsUpdateModule

        diff_summary.append(ComplianceScriptsUpdateModule(**params).main())

    if "DeviceCompliancePolicies" not in exclude:
        from .update.Intune.Compliance import ComplianceUpdateModule

        diff_summary.append(ComplianceUpdateModule(**params).main())

    if "Compliance" not in exclude:
        from .update.Intune.DeviceCompliance import DeviceComplianceUpdateModule

        diff_summary.append(DeviceComplianceUpdateModule(**params).main())

    if "DeviceManagementSettings" not in exclude and args.interactiveauth is True:
        from .update.Intune.DeviceManagementSettings import (
            DeviceManagementSettingsUpdateModule,
        )

        diff_summary.append(DeviceManagementSettingsUpdateModule(**params).main())
    else:
        print(
            "***Device Management Settings is only available with interactive auth***"
        )

    if "DeviceCategories" not in exclude:
        from .update.Intune.DeviceCategories import DeviceCategoriesUpdateModule

        diff_summary.append(DeviceCategoriesUpdateModule(**params).main())

    if "Profiles" not in exclude:
        from .update.Intune.DeviceConfigurations import DeviceConfigurationsUpdateModule

        diff_summary.append(DeviceConfigurationsUpdateModule(**params).main())

    if "GPOConfigurations" not in exclude:
        from .update.Intune.GroupPolicyConfigurations import (
            GroupPolicyConfigurationsUpdateModule,
        )

        diff_summary.append(GroupPolicyConfigurationsUpdateModule(**params).main())

    if "AppleEnrollmentProfile" not in exclude:
        from .update.Intune.AppleEnrollmentProfile import (
            AppleEnrollmentProfileUpdateModule,
        )

        diff_summary.append(AppleEnrollmentProfileUpdateModule(**params).main())

    if "WindowsEnrollmentProfile" not in exclude:
        from .update.Intune.WindowsEnrollmentProfile import (
            WindowsEnrollmentProfileUpdateModule,
        )

        diff_summary.append(WindowsEnrollmentProfileUpdateModule(**params).main())

    if "EnrollmentStatusPage" not in exclude:
        from .update.Intune.EnrollmentStatusPage import EnrollmentStatusPageUpdateModule

        diff_summary.append(EnrollmentStatusPageUpdateModule(**params).main())

    if "EnrollmentConfigurations" not in exclude:
        from .update.Intune.EnrollmentConfigurations import (
            EnrollmentConfigurationsUpdateModule,
        )

        diff_summary.append(EnrollmentConfigurationsUpdateModule(**params).main())

    if "Intents" not in exclude:
        from .update.Intune.ManagementIntents import ManagementIntentsUpdateModule

        diff_summary.append(ManagementIntentsUpdateModule(**params).main())

    if "ProactiveRemediation" not in exclude:
        from .update.Intune.ProactiveRemediation import ProactiveRemediationUpdateModule

        diff_summary.append(ProactiveRemediationUpdateModule(**params).main())

    if "PowershellScripts" not in exclude:
        from .update.Intune.PowerShellScripts import PowerShellScriptsUpdateModule

        diff_summary.append(PowerShellScriptsUpdateModule(**params).main())

    if "ShellScripts" not in exclude:
        from .update.Intune.ShellScripts import ShellScriptsUpdateModule

        diff_summary.append(ShellScriptsUpdateModule(**params).main())

    if "CustomAttribute" not in exclude:
        from .update.Intune.CustomAttributes import CustomAttributesUpdateModule

        diff_summary.append(CustomAttributesUpdateModule(**params).main())

    if "ConfigurationPolicies" not in exclude:
        from .update.Intune.SettingsCatalog import SettingsCatalogUpdateModule

        diff_summary.append(SettingsCatalogUpdateModule(**params).main())

    if "ConditionalAccess" not in exclude:
        from .update.Intune.ConditionalAccess import ConditionalAccessUpdateModule

        diff_summary.append(ConditionalAccessUpdateModule(**params).main())

    if "WindowsDriverUpdateProfiles" not in exclude:
        from .update.Intune.WindowsDriverUpdates import WindowsDriverUpdatesUpdateModule

        diff_summary.append(WindowsDriverUpdatesUpdateModule(**params).main())

    if "windowsFeatureUpdates" not in exclude:
        from .update.Intune.WindowsFeatureUpdates import (
            WindowsFeatureUpdatesUpdateModule,
        )

        diff_summary.append(WindowsFeatureUpdatesUpdateModule(**params).main())

    if "windowsQualityUpdates" not in exclude:
        from .update.Intune.WindowsQualityUpdates import (
            WindowsQualityUpdatesUpdateModule,
        )

        diff_summary.append(WindowsQualityUpdatesUpdateModule(**params).main())

    if "Roles" not in exclude:
        from .update.Intune.Roles import RolesUpdateModule

        diff_summary.append(RolesUpdateModule(**params).main())
