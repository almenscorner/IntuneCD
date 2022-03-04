#!/usr/bin/env python3

"""
This module contains all functions to create the markdown tables.

Parameters
----------
configpath : str
    The path to where the backup files are saved
outpath : str
    The path to save the markdown document to
header : str
    Header of the configuration being documented
"""

import yaml
import json
import os
import glob

from pytablewriter import MarkdownTableWriter

def md_file(outpath):
    if os.path.exists(f'{outpath}') == False:
        open(outpath, 'w+').close()
    else:
        open(outpath, 'w').close()

def write_table(data):
    writer = MarkdownTableWriter(
        headers=['setting', 'value'],
        value_matrix=data
    )

    return writer

def assignment_table(data):

    def write_assignment_table(data, headers):
        writer = MarkdownTableWriter(
            headers=headers,
            value_matrix=data
        )

        return writer

    table = ""
    if "assignments" in data:
        assignments = data['assignments']
        assignment_list = []
        target = ""
        intent = ""
        for assignment in assignments:
            if assignment['target']['@odata.type'] == "#microsoft.graph.allDevicesAssignmentTarget":
                target = "All Devices"
            if assignment['target']['@odata.type'] == "#microsoft.graph.allLicensedUsersAssignmentTarget":
                target = "All Users"
            if 'groupName' in assignment['target']:
                target = assignment['target']['groupName']
            if "intent" in assignment:
                intent = assignment['intent']
                headers = ['intent', 'target', 'filter type', 'filter name']
            else:
                headers = ['target', 'filter type', 'filter name']
            if intent:
                assignment_list.append([intent,
                                        target,
                                        assignment['target']['deviceAndAppManagementAssignmentFilterType'],
                                        assignment['target']['deviceAndAppManagementAssignmentFilterId']])
            else:
                assignment_list.append([target,
                                        assignment['target']['deviceAndAppManagementAssignmentFilterType'],
                                        assignment['target']['deviceAndAppManagementAssignmentFilterId']])

            table = write_assignment_table(assignment_list, headers)

    return table

def remove_characters(string):
    remove_chars = '#@}{]["'
    for char in remove_chars:
        string = string.replace(char, "")

    return string

def clean_list(data):
    values = []
    liststr = ","
    for item in data:
        string = ""
        if type(item) is list:
            for i in item:
                if type(i) is str:
                    if i.isdigit():
                        string = i
                if type(i) is list:
                        string = i+liststr
                        string = remove_characters(string)
                if type(i) is dict:
                    for k, v in i.items():
                        if type(v) is str and len(v) > 200:
                            i[k] = f'<details><summary>Click to expand...</summary>{v}</details>'
                    string = json.dumps(i)
                    string = remove_characters(string)

            values.append(string)

        elif type(item) is dict:
            string = json.dumps(item)
            string = remove_characters(string)

            values.append(string)

        elif type(item) is str:
            if len(item) > 200:
                string = f'<details><summary>Click to expand...</summary>{item}</details>'
            else:
                string = item
            values.append(string)

        else:
            values.append(item)

    return values

def document_configs(configpath, outpath, header):
    ## If configurations path exists, continue
    if os.path.exists(configpath) == True:
        with open(outpath, 'a') as md:
            md.write('# '+header+'\n')

        pattern = configpath + "*/*"
        for filename in glob.glob(pattern, recursive=True):
            ## If path is Directory, skip
            if os.path.isdir(filename):
                continue
            # If file is .DS_Store, skip
            if filename == ".DS_Store":
                continue

            ## Check which format the file is saved as then open file, load data and set query parameter
            with open(filename) as f:
                    if filename.endswith(".yaml"):
                        data = json.dumps(yaml.safe_load(f))
                        repo_data = json.loads(data)
                    elif filename.endswith(".json"):
                        f = open(filename)
                        repo_data = json.load(f)

                    # Create assignments table
                    assignments_table = ""
                    assignments_table = assignment_table(repo_data)
                    repo_data.pop('assignments', None)

                    description = ""
                    if 'description' in repo_data:
                        if repo_data['description'] != None:
                            description = repo_data['description']
                            repo_data.pop('description')

                    # Write configuration markdown table
                    config_table_list = []
                    for key, value in zip(repo_data.keys(),clean_list(repo_data.values())):
                        config_table_list.append([key, value])
                    config_table = write_table(config_table_list)

                    # Write data to file
                    with open(outpath, 'a') as md:
                        if "displayName" in repo_data:
                            md.write('## '+repo_data['displayName']+'\n')
                        if "name" in repo_data:
                            md.write('## '+repo_data['name']+'\n')
                        if description:
                            md.write(f'Description: {description} \n')
                        if assignments_table:
                            md.write('### Assignments \n')
                            md.write(str(assignments_table)+'\n')
                        md.write(str(config_table)+'\n')

def document_management_intents(configpath, outpath,header):
    ## If configurations path exists, continue
    if os.path.exists(configpath) ==True:
        with open(outpath, 'a') as md:
            md.write('# '+header+'\n')

        pattern = configpath + "*/*"
        for filename in glob.glob(pattern, recursive=True):
            ## If path is Directory, skip
            if os.path.isdir(filename):
                continue
            # If file is .DS_Store, skip
            if filename == ".DS_Store":
                continue

            ## Check which format the file is saved as then open file, load data and set query parameter
            with open(filename) as f:
                    if filename.endswith(".yaml"):
                        data = json.dumps(yaml.safe_load(f))
                        repo_data = json.loads(data)
                    elif filename.endswith(".json"):
                        f = open(filename)
                        repo_data = json.load(f)

                    # Create assignments table
                    assignments_table = ""
                    assignments_table = assignment_table(repo_data)
                    repo_data.pop('assignments', None)

                    intent_settings_list = []

                    for setting in repo_data['settingsDelta']:
                        intent_settings_list.append([setting['definitionId'].split("_")[1],
                                                    str(remove_characters(setting['valueJson']))])

                    repo_data.pop('settingsDelta')

                    description = ""
                    if 'description' in repo_data:
                        if repo_data['description'] != None:
                            description = repo_data['description']
                            repo_data.pop('description')

                    intent_table_list = []

                    for key, value in zip(repo_data.keys(),clean_list(repo_data.values())):
                        intent_table_list.append([key, value])

                    table = intent_table_list + intent_settings_list

                    config_table = write_table(table)
                    # Write data to file
                    with open(outpath, 'a') as md:
                        if "displayName" in repo_data:
                            md.write('## '+repo_data['displayName']+'\n')
                        if "name" in repo_data:
                            md.write('## '+repo_data['name']+'\n')
                        if description:
                            md.write(f'Description: {description} \n')
                        if assignments_table:
                            md.write('### Assignments \n')
                            md.write(str(assignments_table)+'\n')
                        md.write(str(config_table)+'\n')