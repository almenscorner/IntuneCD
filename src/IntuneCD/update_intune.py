# -*- coding: utf-8 -*-
import importlib
from concurrent.futures import ThreadPoolExecutor, as_completed

from .intunecdlib.process_scope_tags import ProcessScopeTags
from .decorators import time_command


def import_update_module(module_path: str):
    """
    Dynamically imports a update module, handling both installed and local Git repository cases.
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


@time_command()
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
    max_workers,
):
    """
    Dynamically imports and runs update modules in parallel.
    """

    process_scope_tags = ProcessScopeTags(token)
    scope_tags = None
    if "ScopeTags" not in exclude:
        scope_tags = process_scope_tags.get_scope_tags()

    params = {
        "path": path,
        "token": token,
        "exclude": exclude,
        "report": report,
        "remove": remove,
        "create_groups": create_groups,
        "handle_assignment": assignment,
        "scope_tags": scope_tags,
    }

    update_modules = [
        ("ScopeTags", ".update.Intune.ScopeTags", "ScopeTagsUpdateModule"),
        ("Filters", ".update.Intune.Filters", "FiltersUpdateModule"),
        (
            "AppConfigurations",
            ".update.Intune.AppConfiguration",
            "AppConfigurationUpdateModule",
        ),
        ("AppProtection", ".update.Intune.AppProtection", "AppProtectionUpdateModule"),
        (
            "NotificationTemplate",
            ".update.Intune.NotificationTemplate",
            "NotificationTemplateUpdateModule",
        ),
        (
            "ReusablePolicySettings",
            ".update.Intune.ReusableSettings",
            "ReusableSettingsUpdateModule",
        ),
        (
            "ComplianceScripts",
            ".update.Intune.ComplianceScripts",
            "ComplianceScriptsUpdateModule",
        ),
        (
            "DeviceCompliancePolicies",
            ".update.Intune.Compliance",
            "ComplianceUpdateModule",
        ),
        (
            "Compliance",
            ".update.Intune.DeviceCompliance",
            "DeviceComplianceUpdateModule",
        ),
        (
            "DeviceCategories",
            ".update.Intune.DeviceCategories",
            "DeviceCategoriesUpdateModule",
        ),
        (
            "Profiles",
            ".update.Intune.DeviceConfigurations",
            "DeviceConfigurationsUpdateModule",
        ),
        (
            "GPOConfigurations",
            ".update.Intune.GroupPolicyConfigurations",
            "GroupPolicyConfigurationsUpdateModule",
        ),
        (
            "AppleEnrollmentProfile",
            ".update.Intune.AppleEnrollmentProfile",
            "AppleEnrollmentProfileUpdateModule",
        ),
        (
            "WindowsEnrollmentProfile",
            ".update.Intune.WindowsEnrollmentProfile",
            "WindowsEnrollmentProfileUpdateModule",
        ),
        (
            "EnrollmentStatusPage",
            ".update.Intune.EnrollmentStatusPage",
            "EnrollmentStatusPageUpdateModule",
        ),
        (
            "EnrollmentConfigurations",
            ".update.Intune.EnrollmentConfigurations",
            "EnrollmentConfigurationsUpdateModule",
        ),
        (
            "Intents",
            ".update.Intune.ManagementIntents",
            "ManagementIntentsUpdateModule",
        ),
        (
            "ProactiveRemediation",
            ".update.Intune.ProactiveRemediation",
            "ProactiveRemediationUpdateModule",
        ),
        (
            "PowershellScripts",
            ".update.Intune.PowerShellScripts",
            "PowerShellScriptsUpdateModule",
        ),
        ("ShellScripts", ".update.Intune.ShellScripts", "ShellScriptsUpdateModule"),
        (
            "CustomAttribute",
            ".update.Intune.CustomAttributes",
            "CustomAttributesUpdateModule",
        ),
        (
            "ConfigurationPolicies",
            ".update.Intune.SettingsCatalog",
            "SettingsCatalogUpdateModule",
        ),
        (
            "ConditionalAccess",
            ".update.Intune.ConditionalAccess",
            "ConditionalAccessUpdateModule",
        ),
        (
            "WindowsDriverUpdateProfiles",
            ".update.Intune.WindowsDriverUpdates",
            "WindowsDriverUpdatesUpdateModule",
        ),
        (
            "windowsFeatureUpdates",
            ".update.Intune.WindowsFeatureUpdates",
            "WindowsFeatureUpdatesUpdateModule",
        ),
        (
            "windowsQualityUpdates",
            ".update.Intune.WindowsQualityUpdates",
            "WindowsQualityUpdatesUpdateModule",
        ),
        ("Roles", ".update.Intune.Roles", "RolesUpdateModule"),
    ]

    if "DeviceManagementSettings" not in exclude and args.interactiveauth is True:
        update_modules.append(
            (
                "DeviceManagementSettings",
                ".update.Intune.DeviceManagementSettings",
                "DeviceManagementSettingsUpdateModule",
            )
        )
    else:
        print(
            "***Device Management Settings is only available with interactive auth***"
        )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_module = {}

        for exclude_key, module_path, class_name in update_modules:
            if exclude_key not in exclude:
                module = import_update_module(module_path)
                if module:
                    update_class = getattr(module, class_name)
                    future = executor.submit(update_class(**params).main)
                    future_to_module[future] = exclude_key

        # Collect results as tasks complete
        for future in as_completed(future_to_module):
            module_name = future_to_module[future]
            try:
                result = future.result()
                if result:
                    diff_summary.append(result)
            except Exception as e:
                print(f"[ERROR] {module_name} failed with exception: {e}")
