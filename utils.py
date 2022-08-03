import os
import json
import re
import boto3
from statics import SwitchStatus


def retrieve_feature_flag(keys, event_platform: str, event_environment: str):
    feature_flags = {}
    dynamodb = boto3.client(
        service_name="dynamodb",
        region_name=os.getenv("DYNAMODB_REGION"),
        endpoint_url=os.getenv("DYNAMODB_HOST"),
    )
    # Process each feature flag key
    # Adjust key to switchboard keys
    key_index = 0
    keys = list(set(keys))
    for key in keys:
        morphed_key = f"/switchboard/{key}"
        keys[key_index] = morphed_key
        key_index += 1

    batch_keys = {"switchboard": {"Keys": [{"key": {"S": key}} for key in keys]}}

    responses = dynamodb.batch_get_item(RequestItems=batch_keys)

    feature_flag_items = responses.get("Responses").get("switchboard")

    for feature_flag_item in feature_flag_items:
        is_enabled = False
        feature_flag_morphed_key = feature_flag_item.get("key").get("S")

        # Remove switchboar identifier
        feature_flag_key = re.sub(r"/switchboard/", "", feature_flag_morphed_key)
        # Get Status
        if feature_flag_item.get("status"):
            feature_flag_status_value = feature_flag_item.get("status").get("N")
        else:
            feature_flag_status_value = SwitchStatus.DISABLED

        # When the status is selective, it is only active for specific platforms.
        if feature_flag_status_value == SwitchStatus.SELECTIVE:
            feature_flag_value_raw = None
            if feature_flag_item.get("value"):
                feature_flag_value_raw = feature_flag_item.get("value").get("S")

            # Remove json identifiers used by switchboard
            active_platforms = []
            active_environments = []
            if feature_flag_value_raw:
                feature_flag_value = re.sub(r"__json__=", "", feature_flag_value_raw)
                # Check if platform is enabled
                platforms = json.loads(feature_flag_value).get("platform")
                platform_list = []
                if platforms:
                    platform_list = platforms.get("platform")
                    for platform in platform_list:
                        active_platforms.append(platform[1])
                    if event_platform.lower() in active_platforms:
                        is_enabled = True

                # Check if environment is enabled
                environments = json.loads(feature_flag_value).get("environment")
                environment_list = []
                if environments:
                    environment_list = environments.get("environment")
                    for environment in environment_list:
                        active_environments.append(environment[1])
                    if event_environment.lower() in active_environments:
                        is_enabled = True

        if (
            feature_flag_status_value == SwitchStatus.GLOBAL
            or feature_flag_status_value == SwitchStatus.INHERIT
        ):
            is_enabled = True

        feature_flags[feature_flag_key] = is_enabled

    feature_flag_response = {"data": feature_flags, "success": True}

    return feature_flag_response
