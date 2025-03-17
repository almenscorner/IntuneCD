# -*- coding: utf-8 -*-
import datetime
import json
import os
import time
import uuid
from uuid import uuid4

import requests
from deepdiff import DeepDiff

from .IntuneCDBase import IntuneCDBase


class BaseGraphModule(IntuneCDBase):
    """Base class for the Graph API, used to make requests to the Microsoft Graph API."""

    def make_graph_request(
        self,
        endpoint: str,
        params: dict = None,
        method: str = "GET",
        status_code: int = 200,
        data: dict = None,
    ) -> dict:
        """A function to make a request to the Microsoft Graph API."""

        retry_codes = [504, 502, 503, 429]
        max_retries = 5
        retry_count = 0

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token['access_token']}",
        }

        if (
            method != "GET"
            and self.report
            and endpoint != "https://graph.microsoft.com/beta/$batch"
        ):
            self.log(
                msg=f"Running in report mode, not making Graph {method.upper()} request to {endpoint}"
            )
            return {}

        while retry_count < max_retries:
            response = None  # Ensure response is defined even on exception
            try:
                response = requests.request(
                    method=method,
                    url=endpoint,
                    headers=headers,
                    params=params,
                    timeout=120,
                    data=data,
                )

                # Handle transient errors (5xx and 429)
                if response.status_code in retry_codes:
                    retry_after = response.headers.get("Retry-After", None)
                    wait_time = 10  # Default wait time

                    if response.status_code == 429:
                        if retry_after is not None and retry_after.isdigit():
                            wait_time = int(retry_after)
                            self.log(msg=f"Parsed Retry-After as {wait_time} seconds")
                        else:
                            self.log(
                                tag="warning",
                                msg=f"Retry-After '{retry_after}' is not an integer, using exponential backoff",
                            )
                            wait_time = min((2**retry_count) * 10, 60)

                        self.log(
                            msg=f"Hit Graph throttling (429), retrying in {wait_time} seconds"
                        )
                        time.sleep(wait_time)

                    else:
                        self.log(
                            msg=f"Encountered {response.status_code}, retrying in {wait_time} seconds..."
                        )
                        time.sleep(
                            wait_time
                        )  # Allow each thread to retry at its own rate

                    retry_count += 1
                    continue  # Retry after sleeping

                # Break on success or non-retryable status
                if response.status_code == status_code:
                    break

                self.log(
                    msg=f"Request failed with status {response.status_code}, response: {response.text}"
                )
                break

            except Exception as e:
                self.log(
                    tag="error",
                    msg=f"Error making Graph request to {endpoint}: {type(e).__name__}: {e}\nURL: {endpoint}\nParams: {params}",
                )
                retry_count += 1
                time.sleep(10)
                continue

        # Final check
        if response is None or response.status_code != status_code:
            if response and response.status_code == 404:
                self.log(msg=f"🔎 Resource not found in Microsoft Graph: {endpoint}")
                return {}
            raise requests.exceptions.HTTPError(
                f"Request failed after {max_retries} retries with {response.status_code if response else 'no response'} - {response.text if response else 'no response'}"
            )

        # Handle JSON response
        if method == "GET" and response.text:
            json_data = json.loads(response.text)
            if "@odata.nextLink" in json_data:
                record = self.make_graph_request(
                    method=method, endpoint=json_data["@odata.nextLink"]
                )
                json_data["value"].extend(record["value"])
            return json_data

        return json.loads(response.text) if response.text else {}

    def make_audit_request(self, audit_filter: str):
        """
        This function makes a GET request to the Microsoft Graph API to get the audit logs for a specific object.

        :param pid: The ID of the object to get the audit logs for.
        :param graph_filter: The filter to use for the request.
        :param self.token: The self.token to use for authenticating the request.
        """

        audit_data = []
        if not os.getenv("AUDIT_DAYS_BACK"):
            days_back = 1
        else:
            days_back = int(os.getenv("AUDIT_DAYS_BACK"))
        self.log(function="makeAuditRequest", msg=f"AUDIT_DAYS_BACK: {days_back}")
        # Get the date and time 24 hours ago and format it
        start_date = datetime.datetime.now() - datetime.timedelta(days=days_back)
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.log(function="makeAuditRequest", msg=f"Start date: {start_date}")
        # Get the current date and time
        end_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.log(function="makeAuditRequest", msg=f"End date: {end_date}")
        # Create query to get audit logs for the object
        # if not graph_filter:
        #    graph_filter = f"resources/any(s:s/resourceId eq '{pid}')"
        q_param = {
            "$filter": (
                f"{audit_filter} and activityDateTime gt {start_date} and activityDateTime le {end_date} and "
                "activityOperationType ne 'Get'"
            ),
            "$select": "actor,activityDateTime,activityOperationType,activityResult,resources",
            "$orderby": "activityDateTime desc",
        }
        self.log(function="makeAuditRequest", msg=f"Query parameters: {q_param}")

        # Make the request to the Microsoft Graph API
        endpoint = "https://graph.microsoft.com/v1.0/deviceManagement/auditEvents"
        data = self.make_graph_request(endpoint=endpoint, params=q_param)

        # If there are audit logs, return the latest one
        if data["value"]:
            self.log(
                function="makeAuditRequest", msg=f"Got {len(data['value'])} audit logs."
            )
            for audit_log in data["value"]:
                # is the actor an app or a user?
                if audit_log["actor"]["auditActorType"] == "ItPro":
                    actor = audit_log["actor"].get("userPrincipalName")
                else:
                    actor = audit_log["actor"].get("applicationDisplayName")
                self.log(function="makeAuditRequest", msg=f"Actor found: {actor}")
                audit_data.append(
                    {
                        "resourceId": audit_log["resources"][0]["resourceId"],
                        "auditResourceType": audit_log["resources"][0][
                            "auditResourceType"
                        ],
                        "actor": actor,
                        "activityDateTime": audit_log["activityDateTime"],
                        "activityOperationType": audit_log["activityOperationType"],
                        "activityResult": audit_log["activityResult"],
                    }
                )

        return audit_data

    def create_batch_request(
        self, batch: list, batch_id: str, method: str, url: str, extra_url: str
    ) -> tuple:
        """Creates a batch request for the Graph API.

        Args:
            batch (list): List of objects
            batch_id (str): ID for the batch request
            method (str): HTTP method to use
            url (str): MS graph endpoint for the object
            extra_url (str): Used if anything extra is needed for the url such as /assignments or ?$filter

        Returns:
            tuple: Tuple containing the query data and the batch ID
        """
        query_data = {"requests": []}
        for b_id in batch:
            body = {"id": batch_id, "method": method, "url": url + b_id + extra_url}
            batch_id += 1
            query_data["requests"].append(body)

        return query_data, batch_id

    def handle_responses(
        self,
        initial_request_data: list,
        request_data: list,
        responses: list,
        retry_pool: list,
    ) -> tuple:
        """Handle the responses from the batch request.

        Args:
            initial_request_data (list): List of initial requests
            request_data (list): List of responses from the batch request
            responses (list): List of responses from the batch request
            retry_pool (list): List of failed requests

        Returns:
            tuple: Tuple containing the responses, retry pool and wait time
        """
        wait_time = 0
        for resp in request_data:
            failed_batch_requests = []
            if resp["status"] == 200:
                responses.append(resp["body"])
                retry_pool = [req for req in retry_pool if req["id"] != int(resp["id"])]
            elif resp["status"] in [429, 503]:
                if initial_request_data:
                    failed_batch_requests = [
                        i
                        for i in initial_request_data
                        if i["id"] == int(resp["id"]) and i not in retry_pool
                    ]
                retry_pool += failed_batch_requests

            retry_after = resp["headers"].get("Retry-After")
            wait_time = max(
                wait_time,
                int(retry_after) if retry_after and retry_after.isdigit() else 0,
            )

        return responses, retry_pool, wait_time

    def create_batch_list(self, data: list, batch_count: int) -> list:
        """Create a list of batches from the data.

        Args:
            data (list): List of objects
            batch_count (int): Number of objects to include in each batch

        Returns:
            list: List of batches
        """
        return [data[i : i + batch_count] for i in range(0, len(data), batch_count)]

    def process_batch(
        self,
        batch: list,
        batch_id: str,
        method: str,
        url: str,
        extra_url: str,
        initial_request_data: list,
        responses: list,
        retry_pool: list,
    ) -> tuple:
        """Process the batch request.

        Args:
            batch (list): List of objects
            batch_id (str): ID for the batch request
            method (str): HTTP method to use
            url (str): MS graph endpoint for the object
            extra_url (str): Used if anything extra is needed for the url such as /assignments or ?$filter
            self.token (str): OAuth self.token used for authentication
            initial_request_data (list): List of initial requests
            responses (list): List of responses from the batch request
            retry_pool (list): List of failed requests

        Returns:
            tuple: Tuple containing the batch ID, responses, retry pool and wait time
        """
        query_data, batch_id = self.create_batch_request(
            batch, batch_id, method, url, extra_url
        )
        json_data = json.dumps(query_data)
        request = self.make_graph_request(
            method="POST",
            endpoint="https://graph.microsoft.com/beta/$batch",
            data=json_data,
        )
        request_data = sorted(request["responses"], key=lambda item: item.get("id"))
        initial_request_data += query_data["requests"]
        responses, retry_pool, wait_time = self.handle_responses(
            initial_request_data, request_data, responses, retry_pool
        )
        return batch_id, responses, retry_pool, wait_time

    def retry_failed_requests(
        self,
        retry_pool: list,
        wait_time: int,
        max_retries: int,
        max_wait_time: int,
        initial_request_data: list,
        responses: list,
        batch_count: int,
    ) -> tuple:
        """Retry failed requests.

        Args:
            retry_pool (list): List of failed requests
            wait_time (int): Time to wait before retrying
            max_retries (int): Maximum number of retries
            max_wait_time (int): Maximum time to wait before retrying
            self.token (str): OAuth self.token used for authentication
            initial_request_data (list): List of initial requests
            responses (list): List of responses from the batch request
            batch_count (int): Number of objects to include in each batch

        Returns:
            list: List of responses from the batch request
        """
        retry_count = 0
        failed_retry_requests = []
        while retry_count < max_retries and retry_pool:
            self.log(
                function="retry_failed_requests",
                msg=f"Retrying failed requests, retry pool count: {str(len(retry_pool))}",
            )
            if wait_time > 0:
                self.log(
                    function="retry_failed_requests",
                    msg=f"Sleeping for {str(wait_time)} seconds...",
                )
                time.sleep(wait_time)
                wait_time = min(wait_time * 2, max_wait_time)
            else:
                self.log(
                    function="retry_failed_requests",
                    msg="No wait time in headers, sleeping for 20 seconds...",
                )
                time.sleep(20)
            batch_list = [
                retry_pool[i : i + batch_count]
                for i in range(0, len(retry_pool), batch_count)
            ]
            for batch in batch_list:
                batch_data = {"requests": list(batch)}
                json_data = json.dumps(batch_data)
                request = self.make_graph_request(
                    method="POST",
                    endpoint="https://graph.microsoft.com/beta/$batch",
                    data=json_data,
                )
                request_data = sorted(
                    request["responses"], key=lambda item: item.get("id")
                )
                responses, retry_pool, _ = self.handle_responses(
                    initial_request_data, request_data, responses, retry_pool
                )
                failed_retry_requests = [
                    r for r in request["responses"] if r["status"] != 200
                ]
            retry_count += 1
            self.log(
                function="retry_failed_requests", msg=f"Retry count: {str(retry_count)}"
            )
            if retry_pool and retry_count == max_retries:
                break
        self.log(
            function="retry_failed_requests",
            msg=f"Failed requests after {str(retry_count)} retries: {str(len(failed_retry_requests))}",
        )
        return responses

    def batch_request(
        self, data: list, url: str, extra_url: str, method: str = "GET"
    ) -> list:
        """Batch request to the Graph API.

        Args:
            data (list): List of objects
            url (str): MS graph endpoint for the object
            extra_url (str): Used if anything extra is needed for the url such as /assignments or ?$filter
            self.token (str): OAuth self.token used for authentication
            method (str): HTTP method to use

        Returns:
            list: List of responses from the batch request
        """
        responses = []
        batch_id = 1
        batch_count = 20
        retry_pool = []
        wait_time = 0
        initial_request_data = []

        batch_list = self.create_batch_list(data, batch_count)
        for batch in batch_list:
            batch_id, responses, retry_pool, wait_time = self.process_batch(
                batch,
                batch_id,
                method,
                url,
                extra_url,
                initial_request_data,
                responses,
                retry_pool,
            )

        max_retries = 10
        max_wait_time = 60
        if retry_pool:
            responses = self.retry_failed_requests(
                retry_pool,
                wait_time,
                max_retries,
                max_wait_time,
                initial_request_data,
                responses,
                batch_count,
            )

        return responses

    def get_group_names(self, responses: list, group_ids: list) -> None:
        """get all group names."""
        group_responses = self.batch_request(
            group_ids,
            "groups/",
            "?$select=displayName,id,groupTypes,membershipRule",
        )
        for value in responses:
            if value is None or "value" not in value:
                continue

            for val in value["value"]:
                if "groupId" not in val["target"]:
                    continue

                for g_id in group_responses:
                    if g_id.get("id") == val["target"]["groupId"]:
                        val["target"]["groupName"] = g_id.get("displayName", "")
                        if "DynamicMembership" in g_id.get("groupTypes", []):
                            val["target"]["groupType"] = "DynamicMembership"
                            val["target"]["membershipRule"] = g_id.get(
                                "membershipRule", None
                            )
                        else:
                            val["target"]["groupType"] = "StaticMembership"
                        break

    def get_filter_name(self, val: dict, filter_responses: list) -> None:
        """Get the name of the filter."""
        for f_id in filter_responses:
            if f_id["id"] == val["target"]["deviceAndAppManagementAssignmentFilterId"]:
                val["target"]["deviceAndAppManagementAssignmentFilterId"] = f_id[
                    "displayName"
                ]
                break

    def get_filter_names(self, responses: list, filter_ids: list) -> None:
        """Get all filter names."""
        filter_ids = [
            i for i in filter_ids if i != "00000000-0000-0000-0000-000000000000"
        ]
        filter_responses = self.batch_request(
            filter_ids,
            "deviceManagement/assignmentFilters/",
            "?$select=displayName",
        )
        for value in responses:
            if value["value"]:
                for val in value["value"]:
                    if "deviceAndAppManagementAssignmentFilterId" in val["target"]:
                        self.get_filter_name(val, filter_responses)

    def batch_assignment(self, data: list, url: str, extra_url: str) -> list:
        """
        Batch request to the Graph API.

        :param data: List of objects
        :param url: MS graph endpoint for the object
        :param extra_url: Used if anything extra is needed for the url such as /assignments or ?$filter
        :param self.token: OAuth self.token used for authentication
        :param app_protection: By default False, set to true when getting assignments for APP to get the platform
        :return: List of responses from the batch request
        """

        data_ids = []
        group_ids = []
        filter_ids = []

        # If getting App Protection Assignments, get the platform
        if hasattr(self, "app_protection") and self.app_protection:
            for a_id in data:
                if (
                    a_id["@odata.type"]
                    == "#microsoft.graph.mdmWindowsInformationProtectionPolicy"
                ):
                    data_ids.append(
                        f"mdmWindowsInformationProtectionPolicies/{a_id['id']}"
                    )
                if (
                    a_id["@odata.type"]
                    == "#microsoft.graph.windowsInformationProtectionPolicy"
                ):
                    data_ids.append(
                        f"windowsInformationProtectionPolicies/{a_id['id']}"
                    )
                else:
                    data_ids.append(
                        f"{str(a_id['@odata.type']).split('.')[2]}s/{a_id['id']}"
                    )
        # Else, just add the objects ID to the list
        else:
            for a_id in data:
                data_ids.append(a_id["id"])
        # If we have any IDs, batch request the assignments
        if data_ids:
            responses = self.batch_request(data_ids, url, extra_url)
            if not responses:
                return

            if extra_url == "?$expand=assignments":
                response_values = []
                for value in responses:
                    if value:
                        response_values.append(
                            {
                                "value": value["assignments"],
                                "@odata.context": value["assignments@odata.context"],
                            }
                        )
                responses = response_values

            group_ids = [
                val
                for list in responses
                if list and "value" in list
                for val in list["value"]
                for keys, val in val.items()
                if "target" in keys
                for keys, val in val.items()
                if "groupId" in keys
            ]
            filter_ids = [
                val
                for list in responses
                if list and "value" in list
                for val in list["value"]
                for keys, val in val.items()
                if "target" in keys
                for keys, val in val.items()
                if "deviceAndAppManagementAssignmentFilterId" in keys
                if val is not None
            ]

            # Batch get name of the groups
            if group_ids:
                self.get_group_names(responses, group_ids)

            # Batch get name of the Filters
            if filter_ids:
                self.get_filter_names(responses, filter_ids)

            return responses

    def batch_intents(self, data: list) -> dict:
        """
        Batch request to the Graph API.

        Args:
            data (list): List of objects

        Returns:
            dict: List of responses from the batch request
        """

        base_url = "deviceManagement"
        template_ids = []
        settings_id = []
        categories_responses = []
        settings_responses = []
        intent_values = {"value": []}

        # Get each template ID
        filtered_data = [
            val
            for list in data["value"]
            for key, val in list.items()
            if "templateId" in key and val is not None
        ]
        template_ids = list(dict.fromkeys(filtered_data))

        # Batch get all categories from templates
        if template_ids:
            categories_responses = self.batch_request(
                template_ids, f"{base_url}/templates/", "/categories"
            )

        # Build ID for requesting settings for each Intent
        if categories_responses:
            for intent in data["value"]:
                settings_ids = [
                    val
                    for list in categories_responses
                    if intent["templateId"] is not None
                    and intent["templateId"] in list["@odata.context"]
                    for val in list["value"]
                    for keys, val in val.items()
                    if "id" in keys
                ]
                for setting_id in settings_ids:
                    settings_id.append(f"{intent['id']}/categories/{setting_id}")

        # Batch get all settings for all Intents
        if settings_id:
            settings_responses = self.batch_request(
                settings_id, f"{base_url}/intents/", "/settings"
            )

        # If the Intent ID is in the responses, save the settings to settingsDelta for the Intent
        if settings_responses:
            for intent in data["value"]:
                settingsDelta = [
                    val
                    for list in settings_responses
                    if intent["id"] in list["@odata.context"]
                    for val in list["value"]
                ]
                intent_values["value"].append(
                    {
                        "id": intent["id"],
                        "displayName": intent["displayName"],
                        "description": intent["description"],
                        "templateId": intent["templateId"],
                        "settingsDelta": settingsDelta,
                        "roleScopeTagIds": intent["roleScopeTagIds"],
                    }
                )

        return intent_values

    def get_object_assignment(self, data_id: str, responses: list) -> list:
        """
        Get the object assignment for the object ID.

        :param data_id: Id of the object to get the assignment for
        :param responses: List of responses from the batch request
        :return: List of assignments for the object
        """
        if not responses:
            return []
        remove_keys = {"id", "groupId", "sourceId"}
        assignments_list = [
            val
            for list in responses
            if list and "value" in list
            if data_id in list["@odata.context"]
            for val in list["value"]
        ]
        for value in assignments_list:
            for k in remove_keys:
                value.pop(k, None)
                value["target"].pop(k, None)

        return assignments_list

    def get_object_details(self, object_id: str, responses: list) -> list:
        """
        Get the object details for the object ID.

        :param o_id: Id of the object to get the details for
        :param responses: List of responses from the batch request
        :return: List of details for the object
        """

        details = [
            val
            for list in responses
            if object_id in list["@odata.context"]
            for val in list["value"]
        ]
        return details

    def get_added_removed(self, diff_object: dict) -> list:
        """
        This function is used to get added and removed assignments from the diff object.

        :param diff_object: Object to check for added assignments
        :return: string of added and removed assignments
        """

        update = []
        for root in diff_object:
            intent = ""
            filterID = ""
            filterType = ""
            target = ""

            if "intent" in diff_object[root]:
                intent = diff_object[root]["intent"]

            if "target" in diff_object[root]:
                if (
                    "deviceAndAppManagementAssignmentFilterId"
                    in diff_object[root]["target"]
                ):
                    filterID = diff_object[root]["target"][
                        "deviceAndAppManagementAssignmentFilterId"
                    ]

                if (
                    "deviceAndAppManagementAssignmentFilterType"
                    in diff_object[root]["target"]
                ):
                    filterType = diff_object[root]["target"][
                        "deviceAndAppManagementAssignmentFilterType"
                    ]

                if (
                    diff_object[root]["target"]["@odata.type"]
                    == "#microsoft.graph.groupAssignmentTarget"
                ):
                    target = diff_object[root]["target"]["groupId"]

                if (
                    diff_object[root]["target"]["@odata.type"]
                    == "#microsoft.graph.allDevicesAssignmentTarget"
                ):
                    target = "All Devices"

                if (
                    diff_object[root]["target"]["@odata.type"]
                    == "#microsoft.graph.allLicensedUsersAssignmentTarget"
                ):
                    target = "All Users"

            update.append(
                f"intent: {intent}, Filter ID: {filterID}, Filter Type: {filterType}, target: {target}"
            )

        return update

    def update_assignment(
        self, repo_data: dict, intune_data: dict, create_groups: bool
    ) -> list:
        """
        This function is used to update assignments for configurations in Intune.

        :param repo: Configuration data from repo
        :param mem: Configuration data from Intune
        :param token: OAuth token used for authentication
        :return: If update is true, return repo data, else return None
        """

        diff = DeepDiff(intune_data, repo_data, ignore_order=True)
        added = diff.get("iterable_item_added", {})
        update = False

        if not diff:
            return None

        for val in repo_data:
            # Request group id based on group name
            if "groupName" in val["target"]:
                request = self.make_graph_request(
                    endpoint="https://graph.microsoft.com/beta/groups",
                    params={
                        "$filter": "displayName eq "
                        + "'"
                        + val["target"]["groupName"]
                        + "'"
                    },
                )
                if request["value"]:
                    val["target"].pop("groupName")
                    val["target"].pop("groupType", None)
                    val["target"].pop("membershipRule", None)
                    val["target"]["groupId"] = request["value"][0]["id"]
                else:
                    if create_groups:
                        group_data = {
                            "description": "Created by IntuneCD",
                            "displayName": val["target"]["groupName"],
                            "securityEnabled": True,
                            "mailEnabled": False,
                            "mailNickname": uuid.uuid4().hex,
                        }
                        if val["target"]["groupType"] == "DynamicMembership":
                            group_data["groupTypes"] = ["DynamicMembership"]
                            group_data["membershipRule"] = val["target"][
                                "membershipRule"
                            ]
                            group_data["membershipRuleProcessingState"] = "On"

                        request = self.make_graph_request(
                            endpoint="https://graph.microsoft.com/beta/groups",
                            data=json.dumps(group_data),
                            status_code=201,
                            method="POST",
                        )
                        val["target"].pop("groupName")
                        val["target"].pop("groupType", None)
                        val["target"].pop("membershipRule", None)
                        val["target"]["groupId"] = request["id"]

            # Request filter id based on filter name
            if "deviceAndAppManagementAssignmentFilterId" in val["target"]:
                filters = self.make_graph_request(
                    endpoint="https://graph.microsoft.com/beta/deviceManagement/assignmentFilters",
                )
                for intune_filter in filters["value"]:
                    if (
                        val["target"]["deviceAndAppManagementAssignmentFilterId"]
                        == intune_filter["displayName"]
                    ):
                        val["target"][
                            "deviceAndAppManagementAssignmentFilterId"
                        ] = intune_filter["id"]

                # If filter is None, remove keys
                if val["target"]["deviceAndAppManagementAssignmentFilterId"] is None:
                    val["target"].pop("deviceAndAppManagementAssignmentFilterId")
                    val["target"].pop("deviceAndAppManagementAssignmentFilterType")

            if (
                "groupId" in val["target"]
                or "#microsoft.graph.allDevicesAssignmentTarget"
                in val["target"]["@odata.type"]
                or "#microsoft.graph.allLicensedUsersAssignmentTarget"
                in val["target"]["@odata.type"]
            ):
                update = True

        if update is True:
            # Print added assignments
            added = {
                key: value
                for key, value in added.items()
                if "target" in value and "groupName" not in value["target"]
            }
            if added:
                self.log(msg="Updating assignments, added assignments:")
                updates = self.get_added_removed(added)
                for update in updates:
                    self.log(msg=update)
                return repo_data
            return None

    def make_azure_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: dict = None,
        data: dict = None,
        status_code: int = 200,
    ) -> dict:
        """Make a request to the Azure API.

        Args:
            endpoint (str): The endpoint to make the request to.
            method (str, optional): The method to use for the request. Defaults to "GET".
            q_param (str, optional): Query parameter to use. Defaults to None.

        Raises:
            requests.exceptions.HTTPError: If the request fails.

        Returns:
            dict: The response from the request.
        """
        BASE_URL = "https://main.iam.ad.ext.azure.com/api/"
        header = {
            "Authorization": f"Bearer {self.azure_token}",
            "Content-Type": "application/json",
            "x-ms-client-request-id": str(uuid4()),
            "x-ms-correlation-id": str(uuid4()),
            "host": "main.iam.ad.ext.azure.com",
        }

        if params:
            response = requests.request(
                method,
                f"{BASE_URL}{endpoint}",
                headers=header,
                params=params,
                data=data,
                timeout=120,
            )
        else:
            response = requests.request(
                method, f"{BASE_URL}{endpoint}", headers=header, data=data, timeout=120
            )

        if response.status_code == status_code:
            if method == "GET":
                return json.loads(response.text)

            if response.text:
                return json.loads(response.text)
            return {}
        if response.status_code == 404:
            print(f"Resource not found in Azure: {endpoint}")
        else:
            raise requests.exceptions.HTTPError(
                f"Failed Azure request to {endpoint} - {response.text}"
            )
