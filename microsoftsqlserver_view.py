# --
# File: microsoftsqlserver_view.py
#
# Copyright (c) Phantom Cyber Corporation, 2017
#
# This unpublished material is proprietary to Phantom Cyber.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Phantom Cyber.
#
# --

from django.http import HttpResponse
import json


def display_query_results(provides, all_results, context):
    context['results'] = results = []
    for summary, action_results in all_results:
        for result in action_results:

            ctx_result = {}
            ctx_result['param'] = result.get_param()

            add_datasets_as_rows = ctx_result['param'].get('add_datasets_as_rows', False)
            ctx_result['add_datasets_as_rows'] = add_datasets_as_rows
            ctx_result['description_headers'] = ["name", "type_code", "display_size", "internal_size", "precision", "scale", "null_ok"]

            data = reformat_data(result.get_data(), ctx_result['description_headers'], add_datasets_as_rows)
            
            if (data):
                ctx_result['data'] = data

            summary = result.get_summary()
            if (summary):
                ctx_result['summary'] = summary

            results.append(ctx_result)

    return "run_query.html"

def reformat_data(data, description_headers, add_datasets_as_rows):

    ret = []

    if add_datasets_as_rows:

        for index, dataset in enumerate(data):

            newdataset = {}
            ret += [newdataset]
            newdataset['index'] = index
            newdataset['headers'] = sorted(dataset['dataset'][0].keys())
            newdataset['dataset'] = []

            for row in dataset['dataset']:

                newrow = []
                newdataset['dataset'] += [newrow]

                for col in newdataset['headers']:
                    newrow += [row[col]]

            newdataset['description'] = []
            for name in sorted(dataset['description'].keys()):

                newrow = []
                newdataset['description'] += [newrow]
                newrow += [name]

                for i, col in enumerate(description_headers):
                    if i:
                        newrow += [dataset['description'][name].get(col, "")]

            newdataset['dump'] = json.dumps(newdataset)

    else:

        index = 0
        headers = []

        for i, row in enumerate(data):

            newheaders = sorted(row.keys())
            if set(headers) != set(newheaders):
                headers = newheaders
                newdataset = {}
                ret += [newdataset]
                newdataset['index'] = index
                index += 1
                newdataset['headers'] = sorted(row.keys())
                newdataset['dataset'] = []

            newrow = []
            newdataset['dataset'] += [newrow]
            for col in headers:
                newrow += [row[col]]

            newdataset['dump'] = json.dumps(newdataset)

    return ret
