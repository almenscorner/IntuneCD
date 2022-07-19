#!/usr/bin/env python3

"""This module tests backing up App Configuration."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from src.IntuneCD.backup_configurationPolicies import savebackup
from testfixtures import TempDirectory

BATCH_REQUEST = [
    {
        '@odata.context': "https://graph.microsoft.com/beta/$metadata#deviceManagement/configurationPolicies('0')/settings",
        '@odata.count': 2,
        'value': [
            {
                'id': '0',
                'settingInstance': {
                    '@odata.type': '#microsoft.graph.deviceManagementConfigurationChoiceSettingInstance',
                    'settingDefinitionId': 'com.apple.managedclient.preferences_enforcementlevel',
                    'settingInstanceTemplateReference': None,
                    'choiceSettingValue': {
                        'settingValueTemplateReference': None,
                        'value': 'com.apple.managedclient.preferences_enforcementlevel_0',
                        'children': []}}}]}]
BATCH_ASSIGNMENT = [
    {
        'value': [
            {
                'id': '0',
                'target': {
                    'groupName': 'Group1'}}]}]
OBJECT_ASSIGNMENT = [
    {
        'target': {
            'groupName': 'Group1'}}]


class TestBackupConfigurationPolicy(unittest.TestCase):
    """Test class for backup_appConfiguration."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = 'token'
        self.exclude = []
        self.saved_path = f"{self.directory.path}/Settings Catalog/test."
        self.expected_data = {
            '@odata.type': '#microsoft.graph.deviceManagementConfigurationPolicy',
            'assignments': [
                {
                    'target': {
                        'groupName': 'Group1'}}],
            'description': 'Description value',
            'name': 'test',
            'roleScopeTagIds': ['Role Scope Tag Ids value'],
            'settings': [
                    {
                        'id': '0',
                        'settingInstance': {
                            '@odata.type': '#microsoft.graph.deviceManagementConfigurationChoiceSettingInstance',
                            'choiceSettingValue': {
                                'children': [],
                                'settingValueTemplateReference': None,
                                'value': 'com.apple.managedclient.preferences_enforcementlevel_0'},
                            'settingDefinitionId': 'com.apple.managedclient.preferences_enforcementlevel',
                            'settingInstanceTemplateReference': None}}],
            'templateReference': {
                '@odata.type': 'microsoft.graph.deviceManagementConfigurationPolicyTemplateReference',
                'templateId': 'Template Id value'}}
        self.configuration_policy = {
            "value": [{
                "@odata.type": "#microsoft.graph.deviceManagementConfigurationPolicy",
                "id": "0",
                "name": "test",
                "description": "Description value",
                "roleScopeTagIds": [
                    "Role Scope Tag Ids value"
                ],
                "isAssigned": True,
                "templateReference": {
                    "@odata.type": "microsoft.graph.deviceManagementConfigurationPolicyTemplateReference",
                    "templateId": "Template Id value"
                }
            }
            ]
        }

        self.batch_assignment_patch = patch(
            'src.IntuneCD.backup_configurationPolicies.batch_assignment')
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.batch_request_patch = patch(
            'src.IntuneCD.backup_configurationPolicies.batch_request')
        self.batch_request = self.batch_request_patch.start()
        self.batch_request.return_value = BATCH_REQUEST

        self.object_assignment_patch = patch(
            'src.IntuneCD.backup_configurationPolicies.get_object_assignment')
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            'src.IntuneCD.backup_configurationPolicies.makeapirequest')
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.configuration_policy

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.batch_request.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        self.count = savebackup(
            self.directory.path,
            'yaml',
            self.exclude,
            self.token)

        with open(self.saved_path + 'yaml', 'r') as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.assertTrue(Path(f'{self.directory.path}/Settings Catalog').exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count)

    def test_backup_json(self):
        self.count = savebackup(
            self.directory.path,
            'json',
            self.exclude,
            self.token)

        with open(self.saved_path + 'json', 'r') as f:
            self.saved_data = json.load(f)

        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.assertTrue(Path(f'{self.directory.path}/Settings Catalog').exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count)

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""
        self.makeapirequest.return_value = {'value': []}
        self.count = savebackup(
            self.directory.path,
            'json',
            self.exclude,
            self.token)
        self.assertEqual(0, self.count)
