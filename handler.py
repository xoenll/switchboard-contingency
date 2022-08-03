import json
from utils import retrieve_feature_flag
from statics import Routes
from responses import INVALID_ROUTE


def get_feature_flags(event, context):
    body = {"input": event}

    is_post = False
    is_get = False

    route_key = event.get("routeKey")
    route = route_key.split(" ")[1]
    route_map = {
        Routes.ADD: INVALID_ROUTE,
        Routes.REMOVE: INVALID_ROUTE,
        Routes.STATUS: INVALID_ROUTE,
        Routes.GET: None,
        Routes.POST: None,
    }

    if route_map[route]:
        return route_map[route]

    if "POST" in route_key:
        is_post = True
    if "GET" in route_key:
        is_get = True

    if is_post:
        response = process_post_request(event)
        return response
    if is_get:
        response = process_get_request(event)
        return response


def process_post_request(event):
    event_body = json.loads(event["body"])
    event_features = event_body["feature_flags"]
    event_platform = event_body["platform"]
    event_environment = event_body["environment"]

    response = {
        "body": json.dumps(
            retrieve_feature_flag(
                keys=event_features,
                event_platform=event_platform,
                event_environment=event_environment,
            )
        ),
        "statusCode": 200,
    }

    return response


def process_get_request(event):
    event_parameters = event.get("queryStringParameters")
    event_features_list = event_parameters.get("feature_flags")
    event_features = event_features_list.split(",")
    event_platform = event_parameters.get("platform")
    event_environment = event_parameters.get("environment")

    response = {
        "body": json.dumps(
            retrieve_feature_flag(
                keys=event_features,
                event_platform=event_platform,
                event_environment=event_environment,
            )
        ),
        "statusCode": 200,
    }

    return response
