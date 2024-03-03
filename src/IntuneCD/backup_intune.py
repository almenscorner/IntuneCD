# -*- coding: utf-8 -*-


def backup_intune(results, path, output, exclude, token, prefix, append_id, args):
    """
    Imports all the backup functions and runs them
    """

    from .intunecdlib.process_scope_tags import get_scope_tags

    if "ScopeTags" not in exclude:
        scope_tags = get_scope_tags(token)
    else:
        scope_tags = None

    if args.activationlock:
        from .backup.Intune.backup_activationLock import savebackup

        savebackup(path, output, token)

    if "AppConfigurations" not in exclude:
        from .backup.Intune.backup_appConfiguration import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "AppProtection" not in exclude:
        from .backup.Intune.backup_AppProtection import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "APNs" not in exclude:
        from .backup.Intune.backup_apns import savebackup

        results.append(savebackup(path, output, args.audit, token))

    if "VPP" not in exclude:
        from .backup.Intune.backup_vppTokens import savebackup

        results.append(
            savebackup(path, output, token, append_id, args.audit, scope_tags)
        )

    if "Applications" not in exclude:
        from .backup.Intune.backup_applications import savebackup

        results.append(
            savebackup(path, output, exclude, token, append_id, args.audit, scope_tags)
        )

    if "DeviceCompliancePolicies" not in exclude:
        from .backup.Intune.backup_compliancePolicies import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "ReusablePolicySettings" not in exclude:
        from .backup.Intune.backup_reusablePolicySettings import savebackup

        results.append(
            savebackup(path, output, token, prefix, append_id, args.audit, scope_tags)
        )

    if "ComplianceScripts" not in exclude:
        from .backup.Intune.backup_complianceScripts import savebackup

        results.append(
            savebackup(path, output, token, prefix, append_id, args.audit, scope_tags)
        )

    if "Compliance" not in exclude:
        from .backup.Intune.backup_compliance import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "DeviceManagementSettings" not in exclude:
        from .backup.Intune.backup_deviceManagementSettings import savebackup

        results.append(savebackup(path, output, args.audit, token))

    if "DeviceCategories" not in exclude:
        from .backup.Intune.backup_deviceCategories import savebackup

        results.append(
            savebackup(path, output, token, prefix, append_id, args.audit, scope_tags)
        )

    if "NotificationTemplate" not in exclude:
        from .backup.Intune.backup_notificationTemplate import savebackup

        results.append(
            savebackup(path, output, token, prefix, append_id, args.audit, scope_tags)
        )

    if "Profiles" not in exclude:
        from .backup.Intune.backup_profiles import savebackup

        results.append(
            savebackup(
                path,
                output,
                exclude,
                token,
                prefix,
                append_id,
                args.ignore_omasettings,
                args.audit,
                scope_tags,
            )
        )

    if "GPOConfigurations" not in exclude:
        from .backup.Intune.backup_groupPolicyConfiguration import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "AppleEnrollmentProfile" not in exclude:
        from .backup.Intune.backup_appleEnrollmentProfile import savebackup

        results.append(savebackup(path, output, token, prefix, append_id, args.audit))

    if "WindowsEnrollmentProfile" not in exclude:
        from .backup.Intune.backup_windowsEnrollmentProfile import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "EnrollmentStatusPage" not in exclude:
        from .backup.Intune.backup_enrollmentStatusPage import savebackup

        results.append(
            savebackup(path, output, exclude, token, prefix, append_id, scope_tags)
        )

    if "EnrollmentConfigurations" not in exclude:
        from .backup.Intune.backup_enrollmentConfigurations import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if args.autopilot == "True":
        from .backup.Intune.backup_autopilotDevices import savebackup

        savebackup(path, output, token)

    if "Filters" not in exclude:
        from .backup.Intune.backup_assignmentFilters import savebackup

        results.append(
            savebackup(path, output, token, prefix, append_id, args.audit, scope_tags)
        )

    if "ManagedGooglePlay" not in exclude:
        from .backup.Intune.backup_managedGPlay import savebackup

        results.append(savebackup(path, output, exclude, token, append_id, args.audit))

    if "Intents" not in exclude:
        from .backup.Intune.backup_managementIntents import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "CompliancePartner" not in exclude:
        from .backup.Intune.backup_compliancePartner import savebackup

        results.append(savebackup(path, output, exclude, token, append_id, args.audit))

    if "ManagementPartner" not in exclude:
        from .backup.Intune.backup_managementPartner import savebackup

        results.append(savebackup(path, output, token, append_id, args.audit))

    if "RemoteAssistancePartner" not in exclude:
        from .backup.Intune.backup_remoteAssistancePartner import savebackup

        results.append(savebackup(path, output, token, append_id, args.audit))

    if "ProactiveRemediation" not in exclude:
        from .backup.Intune.backup_proactiveRemediation import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "PowershellScripts" not in exclude:
        from .backup.Intune.backup_powershellScripts import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "ShellScripts" not in exclude:
        from .backup.Intune.backup_shellScripts import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "CustomAttributes" not in exclude:
        from .backup.Intune.backup_customAttributeShellScript import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "ConfigurationPolicies" not in exclude:
        from .backup.Intune.backup_configurationPolicies import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "ConditionalAccess" not in exclude:
        from .backup.Intune.backup_conditionalAccess import savebackup

        results.append(savebackup(path, output, token, prefix, append_id))

    if "WindowsDriverUpdates" not in exclude:
        from .backup.Intune.backup_windowsDriverUpdates import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "WindowsFeatureUpdates" not in exclude:
        from .backup.Intune.backup_windowsFeatureUpdates import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "WindowsQualityUpdates" not in exclude:
        from .backup.Intune.backup_windowsQualityUpdates import savebackup

        results.append(
            savebackup(
                path, output, exclude, token, prefix, append_id, args.audit, scope_tags
            )
        )

    if "Roles" not in exclude:
        from .backup.Intune.backup_roles import savebackup

        results.append(
            savebackup(path, output, exclude, token, append_id, args.audit, scope_tags)
        )

    if "ScopeTags" not in exclude:
        from .backup.Intune.backup_scopeTags import savebackup

        results.append(savebackup(path, output, exclude, token, append_id, args.audit))
