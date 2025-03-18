# -*- coding: utf-8 -*-
import importlib
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the repo root to sys.path if running locally
if "src" in os.path.abspath(os.path.dirname(__file__)):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def import_backup_module(module_path: str):
    """
    Dynamically imports a backup module, handling both installed and local Git repository cases.
    """
    try:
        # Try importing as an installed package
        return importlib.import_module(module_path, package="IntuneCD")
    except ModuleNotFoundError:
        try:
            # If that fails, assume we're running locally and try direct relative import
            return importlib.import_module(module_path)
        except ModuleNotFoundError as e:
            print(f"[ERROR] Could not import {module_path}: {e}")
            return None


def backup_intune(
    results,
    path,
    output,
    exclude,
    token,
    prefix,
    append_id,
    args,
    max_workers,
    platforms,
):
    """
    Imports all the backup functions dynamically and runs them in parallel.
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
        "platforms": platforms,
    }

    # List of backup modules to dynamically import and execute
    backup_modules = [
        (
            "AppConfigurations",
            ".backup.Intune.AppConfiguration",
            "AppConfigurationBackupModule",
        ),
        (
            "AppProtection",
            ".backup.Intune.AppProtection",
            "AppProtectionBackupModule",
        ),
        ("APNs", ".backup.Intune.APNs", "APNSBackupModule"),
        (
            "AppleEnrollmentProfile",
            ".backup.Intune.AppleEnrollmentProfiles",
            "AppleEnrollmentProfilesBackupModule",
        ),
        (
            "Applications",
            ".backup.Intune.Applications",
            "ApplicationsBackupModule",
        ),
        (
            "DeviceManagementSettings",
            ".backup.Intune.DeviceManagementSettings",
            "DeviceManagementSettingsBackupModule",
        ),
        (
            "DeviceCompliancePolicies",
            ".backup.Intune.DeviceCompliance",
            "DeviceComplianceBackupModule",
        ),
        (
            "Profiles",
            ".backup.Intune.DeviceConfigurations",
            "DeviceConfigurationBackupModule",
        ),
        ("Compliance", ".backup.Intune.Compliance", "ComplianceBackupModule"),
        (
            "CompliancePartner",
            ".backup.Intune.CompliancePartner",
            "CompliancePartnerBackupModule",
        ),
        (
            "ComplianceScripts",
            ".backup.Intune.ComplianceScripts",
            "ComplianceScriptsBackupModule",
        ),
        (
            "CustomAttributes",
            ".backup.Intune.CustomAttributes",
            "CustomAttributesBackupModule",
        ),
        (
            "ConditionalAccess",
            ".backup.Intune.ConditionalAccess",
            "ConditionalAccessBackupModule",
        ),
        (
            "DeviceCategories",
            ".backup.Intune.DeviceCategories",
            "DeviceCategoriesBackupModule",
        ),
        (
            "EnrollmentConfigurations",
            ".backup.Intune.EnrollmentConfigurations",
            "EnrollmentConfigurationsBackupModule",
        ),
        (
            "EnrollmentStatusPage",
            ".backup.Intune.EnrollmentStatusPage",
            "EnrollmentStatusPageBackupModule",
        ),
        ("Filters", ".backup.Intune.Filters", "FiltersBackupModule"),
        (
            "GPOConfigurations",
            ".backup.Intune.GroupPolicyConfigurations",
            "GroupPolicyConfigurationsBackupModule",
        ),
        (
            "ManagedGooglePlay",
            ".backup.Intune.ManagedGooglePlay",
            "ManagedGooglePlayBackupModule",
        ),
        (
            "Intents",
            ".backup.Intune.ManagementIntents",
            "ManagementIntentsBackupModule",
        ),
        (
            "ManagementPartner",
            ".backup.Intune.ManagementPartner",
            "ManagementPartnerBackupModule",
        ),
        (
            "NotificationTemplate",
            ".backup.Intune.NotificationTemplates",
            "NotificationTemplateBackupModule",
        ),
        (
            "PowershellScripts",
            ".backup.Intune.PowershellScripts",
            "PowershellScriptsBackupModule",
        ),
        (
            "ProactiveRemediation",
            ".backup.Intune.ProactiveRemediation",
            "ProactiveRemediationScriptBackupModule",
        ),
        (
            "RemoteAssistancePartner",
            ".backup.Intune.RemoteAssistancePartner",
            "RemoteAssistancePartnerBackupModule",
        ),
        (
            "ReusablePolicySettings",
            ".backup.Intune.ReusableSettings",
            "ReusableSettingsBackupModule",
        ),
        ("Roles", ".backup.Intune.Roles", "RolesBackupModule"),
        ("ScopeTags", ".backup.Intune.ScopeTags", "ScopeTagsBackupModule"),
        (
            "SettingsCatalog",
            ".backup.Intune.SettingsCatalog",
            "SettingsCatalogBackupModule",
        ),
        (
            "ShellScripts",
            ".backup.Intune.ShellScripts",
            "ShellScriptsBackupModule",
        ),
        (
            "VPP",
            ".backup.Intune.VolumePurchaseProgram",
            "VPPBackupModule",
        ),
        (
            "windowsDriverUpdates",
            ".backup.Intune.WindowsDriverUpdates",
            "WindowsDriverUpdatesBackupModule",
        ),
        (
            "WindowsEnrollmentProfile",
            ".backup.Intune.WindowsEnrollmentProfile",
            "WindowsEnrollmentProfilesBackupModule",
        ),
        (
            "windowsFeatureUpdates",
            ".backup.Intune.WindowsFeatureUpdates",
            "WindowsFeatureUpdatesBackupModule",
        ),
        (
            "windowsQualityUpdates",
            ".backup.Intune.WindowsQualityUpdates",
            "WindowsQualityUpdatesBackupModule",
        ),
    ]

    if args.activationlock:
        backup_modules.append(
            (
                "ActivationLock",
                ".backup.Intune.Activationlock",
                "ActivationLockBackupModule",
            )
        )

    if args.autopilot:
        backup_modules.append(
            (
                "Autopilot",
                ".backup.Intune.AutopilotDevices",
                "AutopilotDevicesBackupModule",
            )
        )

    # Use ThreadPoolExecutor to run multiple modules in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_module = {}

        for exclude_key, module_path, class_name in backup_modules:
            if exclude_key not in exclude:
                module = import_backup_module(module_path)
                if module:
                    backup_class = getattr(module, class_name)
                    future = executor.submit(backup_class(**params).main)
                    future_to_module[future] = exclude_key

        # Collect results as tasks complete
        for future in as_completed(future_to_module):
            module_name = future_to_module[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                print(f"[ERROR] {module_name} failed with exception: {e}")
