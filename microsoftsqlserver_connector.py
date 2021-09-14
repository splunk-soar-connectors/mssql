# File: microsoftsqlserver_connector.py
# Copyright (c) 2017-2021 Splunk Inc.
#
# SPLUNK CONFIDENTIAL - Use or disclosure of this material in whole or in part
# without a valid written license from Splunk Inc. is PROHIBITED.

# Phantom App imports
import phantom.app as phantom
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# Usage of the consts file is recommended
# from microsoftsqlserver_consts import *
import csv
import json
import pymssql
import binascii
from pymssql import OperationalError
import requests
import datetime


class RetVal(tuple):
    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class MicrosoftSqlServerConnector(BaseConnector):

    def __init__(self):
        super(MicrosoftSqlServerConnector, self).__init__()
        self._state = None
        self._cursor = None

    def _initialize_error(self, msg, exception=None):
        if self.get_action_identifier() == "test_connectivity":
            self.save_progress(msg)
            if exception:
                self.save_progress(str(exception))
            self.set_status(phantom.APP_ERROR, "Test Connectivity Failed")
        else:
            self.set_status(phantom.APP_ERROR, msg, exception)
        return phantom.APP_ERROR

    # fix empty name values in description
    def _remediate_description_names(self, description):

        description = [ list(r) for r in description ]
        name = "__name_not_provided__"
        for i, r in enumerate(description):
            if not r[0]:
                r[0] = name + str(i)
        return(description)

    def _remediate_dataset_value(self, dataset, description):

        dataset = [ list(row) for row in dataset]
        for row in dataset:
            for i, value in enumerate(row):

                # col_name = description[i][0]
                col_type = description[i][1]

                if col_type == 2 and value is not None:
                    row[i] = '0x{0}'.format(binascii.hexlify(value).decode().upper())

                # convert dates to iso8601
                if self._datetime_to_iso8601 and isinstance(value, datetime.datetime):
                    row[i] = value.isoformat()

                # catchall for oddball column types
                if self._default_to_string and not (isinstance(value, str) or isinstance(value, int) or isinstance(value, float)):
                    row[i] = str(value)

        return dataset

    def _dataset_to_dict(self, dataset, description):

        newdataset = []
        for row in dataset:
            dictrow = {}
            newdataset += [dictrow]
            for i, col in enumerate(row):
                dictrow[description[i][0]] = col

        # cooler to use list comprehension, but indecipherable
        # {description[i][0]:col for row in dataset for i, col in enumerate(row)}
        return(newdataset)

    def _description_to_dict(self, description):

        description_labels = ["name", "type_code", "display_size", "internal_size", "precision", "scale", "null_ok"]

        ret = dict()
        for col in description:
            ret[col[0]] = newcol = dict()
            for i, field in enumerate(col):
                if i and field:
                    newcol[description_labels[i]] = field
        return ret

    def _get_query_results(self, action_result):

        summary = { "num_datasets": 0 }

        # dataset_results = {}
        all_datasets = []

        try:

            num_dataset = 0
            while True:
                # description property is from DB-API (PEP249)
                description = self._cursor.description
                if not description:  # For non select queries
                    description = list()
                description = self._remediate_description_names(description)
                dataset = self._cursor.fetchall()
                dataset = self._remediate_dataset_value(dataset, description)
                dataset = self._dataset_to_dict(dataset, description)
                description = self._description_to_dict(description)
                all_datasets += [ {"dataset": dataset, "description": description } ]

                summary["dataset:{}:rows".format(num_dataset)] = len(dataset)
                summary["dataset:{}:columns".format(num_dataset)] = len(dataset[0]) if len(dataset) > 0 else 0
                num_dataset += 1
                summary["num_datasets"] = num_dataset

                if not self._cursor.nextset():
                    break
        except OperationalError:  # No rows in results
            return RetVal(phantom.APP_SUCCESS, [])
        except Exception as e:
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Unable to retrieve results from query", e))

        action_result.update_summary(summary)

        if self._add_datasets_as_rows:
            return RetVal(phantom.APP_SUCCESS, all_datasets)
        else:
            # flatten the datasets to a single list of dictionaries
            results = []
            for d in all_datasets:
                for r in d['dataset']:
                    results += [r]
            return RetVal(phantom.APP_SUCCESS, results)

    def _check_for_valid_schema(self, action_result, schema):
        format_vars = (schema,)
        query = "SELECT * FROM sys.schemas WHERE name = %s;"
        try:
            self._cursor.execute(query, format_vars)
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR, "Error searching for schema", e
            )

        results = self._cursor.fetchall()
        if len(results) == 0:
            return action_result.set_status(phantom.APP_ERROR, "The specified schema could not be found")

        return phantom.APP_SUCCESS

    def _check_for_valid_table(self, action_result, table, check_single=False):
        # check_single will ensure there is only one table with this name
        # If more are found, it will throw an error saying a schema is required
        format_vars = (table,)
        query = "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = %s;"
        try:
            self._cursor.execute(query, format_vars)
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR, "Error searching for table", e
            )

        results = self._cursor.fetchall()
        if len(results) == 0:
            return action_result.set_status(phantom.APP_ERROR, "The specified table could not be found")
        elif check_single and len(results) > 1:  # There is more than 1 table
            return action_result.set_status(
                phantom.APP_ERROR, "More than 1 table has that name, specify a table schema"
            )

        return phantom.APP_SUCCESS

    def _get_format_vars(self, param):
        format_vars = param.get('format_vars')
        if format_vars:
            format_vars = tuple(next(csv.reader([format_vars], quotechar='"', skipinitialspace=True, escapechar='\\')))
        return format_vars

    def _handle_test_connectivity(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        query = "SELECT @@version;"
        try:
            self._cursor.execute(query)
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR, "Test Connectivity Failed", e
            )

        for row in self._cursor:
            self.save_progress("{}".format(row[0]))

        self.save_progress("Test Connectivity Passed")
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_list_columns(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        table_name = param['table_name']
        dbname = param['database']
        table_schema = param.get('table_schema')

        if phantom.is_fail(self._check_for_valid_table(action_result, table_name, not bool(table_schema))):
            return phantom.APP_ERROR

        query = "SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %s AND TABLE_CATALOG = %s"

        if table_schema:
            if phantom.is_fail(self._check_for_valid_schema(action_result, table_schema)):
                return phantom.APP_ERROR
            query += " AND TABLE_SCHEMA = %s"
            format_vars = (table_name, dbname, table_schema)
        else:
            format_vars = (table_name, dbname)

        try:
            self._cursor.execute(query, format_vars)
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR, "Error listing columns", e
            )

        ret_val, results = self._get_query_results(action_result)
        if phantom.is_fail(ret_val):
            return ret_val

        for row in results:
            action_result.add_data(row)

        summary = action_result.update_summary({})
        summary['num_columns'] = len(results)

        return action_result.set_status(phantom.APP_SUCCESS, "Successfully listed columns")

    def _handle_list_tables(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        dbname = param['database']
        table_schema = param.get('table_schema')

        query = "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = %s AND TABLE_CATALOG = %s"

        if table_schema:
            if phantom.is_fail(self._check_for_valid_schema(action_result, table_schema)):
                return phantom.APP_ERROR
            query += " AND TABLE_SCHEMA = %s"
            format_vars = ('BASE TABLE', dbname, table_schema)
        else:
            format_vars = ('BASE TABLE', dbname)

        try:
            self._cursor.execute(query, format_vars)
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR, "Error listing tables", e
            )

        ret_val, results = self._get_query_results(action_result)
        if phantom.is_fail(ret_val):
            return ret_val

        for row in results:
            action_result.add_data(row)

        summary = action_result.update_summary({})
        summary['num_tables'] = len(results)

        return action_result.set_status(phantom.APP_SUCCESS, "Successfully listed tables")

    def _handle_run_query(self, param):

        self._default_to_string = param.get("default_to_string", False)
        self._datetime_to_iso8601 = param.get("datetime_to_iso8601", False)
        self._add_datasets_as_rows = param.get('add_datasets_as_rows', self._add_datasets_as_rows)

        action_result = self.add_action_result(ActionResult(dict(param)))
        query = param['query']
        format_vars = self._get_format_vars(param)
        non_query = param.get('non_query', False)

        try:
            if non_query:
                self._connection._conn.execute_non_query('ROLLBACK TRAN')
                self._connection._conn.execute_non_query(query, format_vars)
            else:
                self._cursor.execute(query, format_vars)
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR, "Error running query", e
            )

        if non_query:
            action_result.update_summary({'num_rows': 0})
            return action_result.set_status(phantom.APP_SUCCESS, "Successfully ran non-query")

        ret_val, results = self._get_query_results(action_result)
        if phantom.is_fail(ret_val):
            return ret_val

        if not param.get('no_commit', False):
            try:
                self._connection.commit()
            except Exception as e:
                return action_result.set_status(
                    phantom.APP_ERROR, "unable to commit changes", e
                )

        for row in results:
            action_result.add_data(row)

        summary = action_result.update_summary({})
        summary['num_rows'] = len(results)

        return action_result.set_status(phantom.APP_SUCCESS, "Successfully ran query")

    def handle_action(self, param):

        ret_val = phantom.APP_SUCCESS

        # To make this app work in a targeted mode where you can specify the
        # host with each action, the code to connect to the database was moved
        # from initialize to here.
        if phantom.is_fail(self._connect_sql(param)):
            action_result = self.add_action_result(ActionResult(dict(param)))
            action_result.set_status(phantom.APP_ERROR, "Unable to connect to host: {0}".format(param['host']))
            return phantom.APP_ERROR

        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())

        if action_id == 'test_connectivity':
            ret_val = self._handle_test_connectivity(param)

        elif action_id == 'list_columns':
            ret_val = self._handle_list_columns(param)

        elif action_id == 'list_tables':
            ret_val = self._handle_list_tables(param)

        elif action_id == 'run_query':
            ret_val = self._handle_run_query(param)

        return ret_val

    def _connect_sql(self, param):
        self._default_to_string = False
        self._datetime_to_iso8601 = False
        self._add_datasets_as_rows = False
        self._state = self.load_state()

        config = self.get_config()
        param = self.get_current_param()
        username = config['username']
        password = config['password']
        port = config.get('port', 1433)
        host = param.get('host', config['host'])
        database = param.get('database', config['database'])
        param['host'] = host
        param['database'] = database

        if not host:
            return self._initialize_error("host not provided or configured")
        if not database:
            return self._initialize_error("database not provided or configured")

        self._cursor = None
        try:
            self._connection = pymssql.connect(
                host, username, password, database, port=port
            )
            self._cursor = self._connection.cursor()
        except Exception as e:
            return self._initialize_error("Error authenticating with database", e)

        # check for the connection to the host
        if self._cursor is None:
            return self._initialize_error("Error connecting to host: {}".format(host))

        self.save_progress("Database connection established")
        return True

    def initialize(self):
        return phantom.APP_SUCCESS

    def finalize(self):
        self.save_state(self._state)
        return phantom.APP_SUCCESS


if __name__ == '__main__':

    import sys
    import pudb
    import argparse

    pudb.set_trace()

    argparser = argparse.ArgumentParser()

    argparser.add_argument('input_test_json', help='Input Test JSON file')
    argparser.add_argument('-u', '--username', help='username', required=False)
    argparser.add_argument('-p', '--password', help='password', required=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password

    if username is not None and password is None:

        # User specified a username but not a password, so ask
        import getpass
        password = getpass.getpass("Password: ")

    if username and password:
        try:
            login_url = BaseConnector._get_phantom_base_url() + "login"
            print("Accessing the Login page")
            r = requests.get(login_url, verify=False)
            csrftoken = r.cookies['csrftoken']

            data = dict()
            data['username'] = username
            data['password'] = password
            data['csrfmiddlewaretoken'] = csrftoken

            headers = dict()
            headers['Cookie'] = 'csrftoken=' + csrftoken
            headers['Referer'] = login_url

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=False, data=data, headers=headers)
            session_id = r2.cookies['sessionid']
        except Exception as e:
            print("Unable to get session id from the platfrom. Error: " + str(e))
            exit(1)

    if len(sys.argv) < 2:
        print("No test json specified as input")
        exit(0)

    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = MicrosoftSqlServerConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json['user_session_token'] = session_id

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    exit(0)
