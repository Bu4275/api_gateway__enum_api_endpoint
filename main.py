#!/usr/bin/env python3
import argparse
from botocore.exceptions import ClientError


module_info = {
    # Name of the module (should be the same as the filename)
    'name': 'api_gateway__enum_api_endpoint',

    # Name and any other notes about the author
    'author': 'bu4275 @ bu472@gmail.com',

    # Category of the module. Make sure the name matches an existing category.
    'category': 'ENUM',

    # One liner description of the module functionality. This shows up when a user searches for modules.
    'one_liner': 'Enumerates API Endpoint from AWS apigateway.',

    # Full description about what the module does and how it works
    'description': 'This module pulls restapi_id, stage_name and resource_path, then combin them to API Endpoint',

    # A list of AWS services that the module utilizes during its execution
    'services': ['apigateway'],

    # For prerequisite modules, try and see if any existing modules return the data that is required for your module before writing that code yourself, that way, session data can stay separated and modular.
    'prerequisite_modules': [],

    # External resources that the module depends on. Valid options are either a GitHub URL (must end in .git) or single file URL.
    'external_dependencies': [],

    # Module arguments to autocomplete when the user hits tab
    'arguments_to_autocomplete': ['--regions'],
}

parser = argparse.ArgumentParser(add_help=False, description=module_info['description'])
parser.add_argument('--regions', required=False, default=None, help='One or more (comma separated) AWS regions in the format us-east-1. Defaults to all session regions.')


def get_rest_api_id(client):

    rest_ids = dict()
    resp = client.get_rest_apis()
    for item in resp['items']:
        rest_ids[item['id']] = []
    return rest_ids

def get_stage_names(client, rest_id):
    stage_names = []
    resp = client.get_stages(restApiId=rest_id)
    for item in resp['item']:
        stage_names.append(item['stageName'])
    return stage_names

def get_resource_path(client, rest_id):
    resource_path = []
    resp = client.get_resources(restApiId=rest_id)
    # print(resp)
    for item in resp['items']:
        resource_path.append(item['path'])
    return resource_path 

def main(args, pacu_main):
    session = pacu_main.get_active_session()

    ###### Don't modify these. They can be removed if you are not using the function.
    args = parser.parse_args(args)
    print = pacu_main.print
    get_regions = pacu_main.get_regions
    ######

    if args.regions:
        regions = args.regions.split(',')
    else:
        regions = get_regions('apigateway')

    summary_data = {}
    url = 'https://{restapi_id}.execute-api.{region}.amazonaws.com/{stage_name}{resource_path}'

    for region in regions:
        print('Starting region {}...'.format(region))

        client = pacu_main.get_boto3_client('apigateway', region)

        try:
            rest_ids = get_rest_api_id(client)
        except ClientError as e:
            if 'AccessDeniedException' in str(e):
                print('AccessDeniedException: get_rest_api_id')
            continue

        if len(rest_ids) > 0:

            for rest_id in rest_ids:
                try:
                    stage_names = get_stage_names(client, rest_id)
                    resource_paths = get_resource_path(client, rest_id)
                except ClientError as e:
                    if 'AccessDeniedException' in str(e):
                        print('AccessDeniedException: get_stage_names or get_resource_path')
                    continue

            summary_data[region] = []
            for stage_name in stage_names:
                for resource_path in  resource_paths:
                    api_endpoint = url.format(restapi_id=rest_id, region=region, stage_name=stage_name, resource_path=resource_path)
                    print('Found: %s' % api_endpoint)
                    summary_data[region].append(api_endpoint)
    print('=========================== End Function ===========================')
    return summary_data


def summary(data, pacu_main):
    out = ''
    for region in data:
        out += 'Region: %s\n' % region

        for api in data[region]:
            out += api + '\n'
    return out
