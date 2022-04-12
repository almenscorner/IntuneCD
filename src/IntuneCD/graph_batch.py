"""
This module is used to batch requests to the Graph Batch endpoint. Two additional functions,
get_object_assignment and get_object_details is used to retrieve the objects assignment and details from
the batch request.

Parameters batch_request
----------
data : list
    List of object IDs to get data for
url : str
    MS graph endpoint for the object
extra_url : str
    Used if anything extra is needed for the url such as /assignments or ?$filter
token : str
    OAuth token used for authentication

Parameters batch_assignment
----------
data : list
    List of objects
url : str
    MS graph endpoint for the object
extra_url : str
    Used if anything extra is needed for the url such as /assignments or ?$filter
token : str
    OAuth token used for authentication
app_protection : bool
    By default False, set to true when getting assignments for APP to get the platform

Parameters batch_intents
----------
data : list
    List of objects
token : str
    OAuth token used for authentication

Parameters get_object_assignments
----------
id : str
    ID of the object to get assignments for
responses : list
    Responses from batch_assignment

Parameters get_object_details
----------
id : str
    ID of the object to get assignments for
responses : list
    Responses from batch request
"""

import json
from .graph_request import makeapirequestPost

def batch_request(data, url, extra_url, token, method='GET') -> list:

    responses = []
    batch_id = 1
    batch_count = 20
    ## Split objects into lists of 20
    batch_list = [data[i:i + batch_count]
                  for i in range(0, len(data), batch_count)]

    ## Build a body for each ID in the list
    for i in range(0, len(batch_list)):
        query_data = {'requests': []}
        for id in batch_list[i]:
            body = {
                'id': batch_id,
                'method': method,
                'url': url+id+extra_url
            }

            batch_id += 1
            query_data['requests'].append(body)

        ## POST to the graph batch endpoint
        json_data = json.dumps(query_data)
        request = makeapirequestPost(
            'https://graph.microsoft.com/beta/$batch', token, jdata=json_data)
        request_data = sorted(
            request['responses'], key=lambda item: item.get("id"))

        ## Append each succcessful request to responses list
        for resp in request_data:
            if resp['status'] == 200:
                responses.append(resp['body'])

    return responses

def batch_assignment(data, url, extra_url, token, app_protection=False) -> list:

    data_ids = []
    group_ids = []
    filter_ids = []

    ## If getting App Protection Assignments, get the platform
    if app_protection is True:
        for id in data['value']:
            if id['@odata.type'] == "#microsoft.graph.mdmWindowsInformationProtectionPolicy":
                data_ids.append(
                    f"mdmWindowsInformationProtectionPolicies/{id['id']}")
            if id['@odata.type'] == "#microsoft.graph.windowsInformationProtectionPolicy":
                data_ids.append(
                    f"windowsInformationProtectionPolicies/{id['id']}")
            else:
                data_ids.append(
                    f"{str(id['@odata.type']).split('.')[2]}s/{id['id']}")
    ## Else, just add the objects ID to the list
    else:
        for id in data['value']:
            data_ids.append(id['id'])
    ## If we have any IDs, batch request the assignments
    if data_ids:
        responses = batch_request(data_ids, url, extra_url, token)
        if responses:
            group_ids = [val for list in responses for val in list['value']
                         for keys, val in val.items() if 'target' in keys
                         for keys, val in val.items() if 'groupId' in keys]
            filter_ids = [val for list in responses for val in list['value']
                          for keys, val in val.items() if 'target' in keys
                          for keys, val in val.items() if 'deviceAndAppManagementAssignmentFilterId' in keys if val != None]

        ## Batch get name of the groups
        if group_ids:
            group_responses = batch_request(
                group_ids, f'groups/', '?$select=displayName,id', token)
            for value in responses:
                if value['value']:
                    for val in value['value']:
                        if 'groupId' in val['target']:
                            for id in group_responses:
                                if id['id'] == val['target']['groupId']:
                                    val['target']['groupName'] = id['displayName']

        ## Batch get name of the Filters
        if filter_ids:
            filter_responses = batch_request(
                filter_ids, f'deviceManagement/assignmentFilters/', '?$select=displayName', token)
            for value in responses:
                if value['value']:
                    for val in value['value']:
                        if 'deviceAndAppManagementAssignmentFilterId' in val['target']:
                            for id in filter_responses:
                                if id['id'] == val['target']['deviceAndAppManagementAssignmentFilterId']:
                                    val['target']['deviceAndAppManagementAssignmentFilterId'] = id['displayName']

        return responses

def batch_intents(data, token) -> dict:
    base_url = 'deviceManagement'
    template_ids = []
    settings_id = []
    categories_responses = []
    settings_responses = []
    intent_values = {'value': []}

    ## Get each template ID
    filtered_data = [val for list in data['value']
                     for key, val in list.items() if 'templateId' in key]
    template_ids = list(dict.fromkeys(filtered_data))

    ## Batch get all categories from templates
    if template_ids:
        categories_responses = batch_request(
            template_ids, f'{base_url}/templates/', '/categories', token)

    ## Build ID for requesting settings for each Intent
    if categories_responses:
        for intent in data['value']:
            settings_ids = [val for list in categories_responses if intent['templateId'] in list['@odata.context']
                            for val in list['value'] for keys, val in val.items() if 'id' in keys]
            for setting_id in settings_ids:
                settings_id.append(f"{intent['id']}/categories/{setting_id}")

    ## Batch get all settings for all Intents
    if settings_id:
        settings_responses = batch_request(
            settings_id, f'{base_url}/intents/', '/settings', token)

    ## If the Intent ID is in the responses, save the settings to settingsDelta for the Intent
    if settings_responses:
        for intent in data['value']:
            settingsDelta = [val for list in settings_responses if intent['id']
                             in list['@odata.context'] for val in list['value']]
            intent_values['value'].append({
                "id": intent['id'],
                "displayName": intent['displayName'],
                "description": intent['description'],
                "templateId": intent['templateId'],
                "settingsDelta": settingsDelta,
                "roleScopeTagIds": intent['roleScopeTagIds']
            })

    return intent_values

def get_object_assignment(id, responses) -> list:
    remove_keys = {'id', 'groupId', 'sourceId'}
    assignments_list = [
        val for list in responses if id in list['@odata.context'] for val in list['value']]
    for value in assignments_list:
        for k in remove_keys:
            value.pop(k, None)
            value['target'].pop(k, None)
    return assignments_list

def get_object_details(id, responses) -> list:
    details = [val for list in responses if id in list['@odata.context'] for val in list['value']]
    return details