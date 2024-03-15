# -*- coding: utf-8 -*-


def backup_intune(results, path, output, exclude, token, prefix, append_id, args):
    """
    Imports all the backup functions and runs them
    """

    from .intunecdlib.process_scope_tags import ProcessScopeTags

    process_scope_tags = ProcessScopeTags(token)

    if "ScopeTags" not in exclude:
        scope_tags = process_scope_tags.get_scope_tags()
    else:
        scope_tags = None

    params = {
        "token": token,
        "path": path,
        "filetype": output,
        "audit": args.audit,
        "append_id": append_id,
        "exclude": exclude,
        "scope_tags": scope_tags,
        "prefix": prefix,
        "ignore_oma_settings": args.ignore_omasettings,
    }

    if args.activationlock:
        from .backup.Intune.Activationlock import ActivationLockBackupModule

        ActivationLockBackupModule(**params).main()

    if args.autopilot:
        from .backup.Intune.AutopilotDevices import AutopilotDevicesBackupModule

        AutopilotDevicesBackupModule(**params).main()

    if "AppConfigurations" not in exclude:
        from .backup.Intune.AppConfiguration import AppConfigurationBackupModule

        results.append(AppConfigurationBackupModule(**params).main())

    if "AppProtection" not in exclude:
        from .backup.Intune.AppProtection import AppProtectionBackupModule

        results.append(AppProtectionBackupModule(**params).main())

    if "APNS" not in exclude:
        from .backup.Intune.APNs import APNSBackupModule

        results.append(APNSBackupModule(**params).main())

    if "VPP" not in exclude:
        from .backup.Intune.VolumePurchaseProgram import VPPBackupModule

        results.append(VPPBackupModule(**params).main())

    if "Applications" not in exclude:
        from .backup.Intune.Applications import ApplicationsBackupModule

        results.append(ApplicationsBackupModule(**params).main())

    if "DeviceCompliancePolicies" not in exclude:
        from .backup.Intune.DeviceCompliance import DeviceComplianceBackupModule

        results.append(DeviceComplianceBackupModule(**params).main())

    if "ReusablePolicySettings" not in exclude:
        from .backup.Intune.ReusableSettings import ReusableSettingsBackupModule

        results.append(ReusableSettingsBackupModule(**params).main())

    if "ComplianceScripts" not in exclude:
        from .backup.Intune.ComplianceScripts import ComplianceScriptsBackupModule

        results.append(ComplianceScriptsBackupModule(**params).main())

    if "Compliance" not in exclude:
        from .backup.Intune.Compliance import ComplianceBackupModule

        results.append(ComplianceBackupModule(**params).main())

    if "DeviceManagementSettings" not in exclude:
        from .backup.Intune.DeviceManagementSettings import (
            DeviceManagementSettingsBackupModule,
        )

        results.append(DeviceManagementSettingsBackupModule(**params).main())

    if "DeviceCategories" not in exclude:
        from .backup.Intune.DeviceCategories import DeviceCategoriesBackupModule

        results.append(DeviceCategoriesBackupModule(**params).main())

    if "NotificationTemplate" not in exclude:
        from .backup.Intune.NotificationTemplates import (
            NotificationTemplateBackupModule,
        )

        results.append(NotificationTemplateBackupModule(**params).main())

    if "Profiles" not in exclude:
        from .backup.Intune.DeviceConfigurations import DeviceConfigurationBackupModule

        results.append(DeviceConfigurationBackupModule(**params).main())

    if "GPOConfigurations" not in exclude:
        from .backup.Intune.GroupPolicyConfigurations import (
            GroupPolicyConfigurationsBackupModule,
        )

        results.append(GroupPolicyConfigurationsBackupModule(**params).main())

    if "AppleEnrollmentProfile" not in exclude:
        from .backup.Intune.AppleEnrollmentProfiles import (
            AppleEnrollmentProfilesBackupModule,
        )

        results.append(AppleEnrollmentProfilesBackupModule(**params).main())

    if "WindowsEnrollmentProfile" not in exclude:
        from .backup.Intune.WindowsEnrollmentProfile import (
            WindowsEnrollmentProfilesBackupModule,
        )

        results.append(WindowsEnrollmentProfilesBackupModule(**params).main())

    if "EnrollmentStatusPage" not in exclude:
        from .backup.Intune.EnrollmentStatusPage import EnrollmentStatusPageBackupModule

        results.append(EnrollmentStatusPageBackupModule(**params).main())

    if "EnrollmentConfigurations" not in exclude:
        from .backup.Intune.EnrollmentConfigurations import (
            EnrollmentConfigurationsBackupModule,
        )

        results.append(EnrollmentConfigurationsBackupModule(**params).main())

    if "Filters" not in exclude:
        from .backup.Intune.Filters import FiltersBackupModule

        results.append(FiltersBackupModule(**params).main())

    if "ManagedGooglePlay" not in exclude:
        from .backup.Intune.ManagedGooglePlay import ManagedGooglePlayBackupModule

        results.append(ManagedGooglePlayBackupModule(**params).main())

    if "Intents" not in exclude:
        from .backup.Intune.ManagementIntents import ManagementIntentsBackupModule

        results.append(ManagementIntentsBackupModule(**params).main())

    if "CompliancePartner" not in exclude:
        from .backup.Intune.CompliancePartner import CompliancePartnerBackupModule

        results.append(CompliancePartnerBackupModule(**params).main())

    if "ManagementPartner" not in exclude:
        from .backup.Intune.ManagementPartner import ManagementPartnerBackupModule

        results.append(ManagementPartnerBackupModule(**params).main())

    if "RemoteAssistancePartner" not in exclude:
        from .backup.Intune.RemoteAssistancePartner import (
            RemoteAssistancePartnerBackupModule,
        )

        results.append(RemoteAssistancePartnerBackupModule(**params).main())

    if "ProactiveRemediation" not in exclude:
        from .backup.Intune.ProactiveRemediation import (
            ProactiveRemediationScriptBackupModule,
        )

        results.append(ProactiveRemediationScriptBackupModule(**params).main())

    if "PowershellScripts" not in exclude:
        from .backup.Intune.PowershellScripts import PowershellScriptsBackupModule

        results.append(PowershellScriptsBackupModule(**params).main())

    if "ShellScripts" not in exclude:
        from .backup.Intune.ShellScripts import ShellScriptsBackupModule

        results.append(ShellScriptsBackupModule(**params).main())

    if "CustomAttributes" not in exclude:
        from .backup.Intune.CustomAttributes import CustomAttributesBackupModule

        results.append(CustomAttributesBackupModule(**params).main())

    if "ConfigurationPolicies" not in exclude:
        from .backup.Intune.SettingsCatalog import SettingsCatalogBackupModule

        results.append(SettingsCatalogBackupModule(**params).main())

    if "ConditionalAccess" not in exclude:
        from .backup.Intune.ConditionalAccess import ConditionalAccessBackupModule

        results.append(ConditionalAccessBackupModule(**params).main())

    if "WindowsDriverUpdates" not in exclude:
        from .backup.Intune.WindowsDriverUpdates import WindowsDriverUpdatesBackupModule

        results.append(WindowsDriverUpdatesBackupModule(**params).main())

    if "WindowsFeatureUpdates" not in exclude:
        from .backup.Intune.WindowsFeatureUpdates import (
            WindowsFeatureUpdatesBackupModule,
        )

        results.append(WindowsFeatureUpdatesBackupModule(**params).main())

    if "WindowsQualityUpdates" not in exclude:
        from .backup.Intune.WindowsQualityUpdates import (
            WindowsQualityUpdatesBackupModule,
        )

        results.append(WindowsQualityUpdatesBackupModule(**params).main())

    if "Roles" not in exclude:
        from .backup.Intune.Roles import RolesBackupModule

        results.append(RolesBackupModule(**params).main())

    if "ScopeTags" not in exclude:
        from .backup.Intune.ScopeTags import ScopeTagsBackupModule

        results.append(ScopeTagsBackupModule(**params).main())
