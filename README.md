[comment]: # "Auto-generated SOAR connector documentation"
# Microsoft SQL Server

Publisher: Splunk  
Connector Version: 2\.3\.0  
Product Vendor: Microsoft  
Product Name: Microsoft SQL Server  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 5\.3\.5  

This app supports investigative actions against a Microsoft SQL Server

[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2017-2022 Splunk Inc."
[comment]: # ""
[comment]: # "Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "you may not use this file except in compliance with the License."
[comment]: # "You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "    http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "either express or implied. See the License for the specific language governing permissions"
[comment]: # "and limitations under the License."
[comment]: # ""
This app will ignore the HTTP_PROXY and HTTPS_PROXY environment variables, as it does not use HTTP
to connect to the database.  
Below are the default ports used by Microsoft-SQL-Server.

|         Service Name                         | Port | Transport Protocol |
|----------------------------------------------|------|--------------------|
|          **Microsoft-SQL-Server (ms-sql-s)** | 1433 | tcp                |
|          **Microsoft-SQL-Server (ms-sql-s)** | 1433 | udp                |

## LGPL

This app uses the pymssql module, which is licensed under the Free Software Foundation (FSF).


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Microsoft SQL Server asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**host** |  required  | string | Database hostname or IP Address
**database** |  required  | string | Database name
**username** |  required  | string | Username
**password** |  required  | password | Password
**port** |  optional  | numeric | Database Service Port

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration  
[list columns](#action-list-columns) - List all the columns in a table  
[list tables](#action-list-tables) - List all the tables in the database  
[run query](#action-run-query) - Run a query against a table or tables in the database  

## action: 'test connectivity'
Validate the asset configuration for connectivity using supplied configuration

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'list columns'
List all the columns in a table

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**table\_name** |  required  | Table Name | string |  `mssql table name` 
**table\_schema** |  optional  | Table Schema | string |  `mssql table schema` 
**host** |  optional  | Optional database hostname or ip address | string |  `hostname`  `host` 
**database** |  optional  | Optional database name | string |  `mssql database name` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.database | string |  `mssql database name` 
action\_result\.parameter\.host | string |  `hostname`  `host` 
action\_result\.parameter\.table\_name | string |  `mssql table name` 
action\_result\.parameter\.table\_schema | string |  `mssql table schema` 
action\_result\.data\.\*\.CHARACTER\_MAXIMUM\_LENGTH | numeric | 
action\_result\.data\.\*\.CHARACTER\_OCTET\_LENGTH | numeric | 
action\_result\.data\.\*\.CHARACTER\_SET\_CATALOG | string | 
action\_result\.data\.\*\.CHARACTER\_SET\_NAME | string | 
action\_result\.data\.\*\.CHARACTER\_SET\_SCHEMA | string | 
action\_result\.data\.\*\.COLLATION\_CATALOG | string | 
action\_result\.data\.\*\.COLLATION\_NAME | string | 
action\_result\.data\.\*\.COLLATION\_SCHEMA | string | 
action\_result\.data\.\*\.COLUMN\_DEFAULT | string | 
action\_result\.data\.\*\.COLUMN\_NAME | string | 
action\_result\.data\.\*\.DATA\_TYPE | string | 
action\_result\.data\.\*\.DATETIME\_PRECISION | numeric | 
action\_result\.data\.\*\.DOMAIN\_CATALOG | string |  `domain` 
action\_result\.data\.\*\.DOMAIN\_NAME | string |  `domain` 
action\_result\.data\.\*\.DOMAIN\_SCHEMA | string |  `domain` 
action\_result\.data\.\*\.IS\_NULLABLE | string | 
action\_result\.data\.\*\.NUMERIC\_PRECISION | numeric | 
action\_result\.data\.\*\.NUMERIC\_PRECISION\_RADIX | numeric | 
action\_result\.data\.\*\.NUMERIC\_SCALE | numeric | 
action\_result\.data\.\*\.ORDINAL\_POSITION | numeric | 
action\_result\.data\.\*\.TABLE\_CATALOG | string | 
action\_result\.data\.\*\.TABLE\_NAME | string |  `mssql table schema` 
action\_result\.data\.\*\.TABLE\_SCHEMA | string |  `mssql table schema` 
action\_result\.summary\.dataset\:0\:columns | numeric | 
action\_result\.summary\.dataset\:0\:rows | numeric | 
action\_result\.summary\.num\_columns | numeric | 
action\_result\.summary\.num\_datasets | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'list tables'
List all the tables in the database

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**table\_schema** |  optional  | Table Schema | string |  `mssql table schema` 
**host** |  optional  | Optional database hostname or ip address | string |  `hostname`  `host` 
**database** |  optional  | Optional database name | string |  `mssql database name` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.database | string |  `mssql database name` 
action\_result\.parameter\.host | string |  `hostname`  `host` 
action\_result\.parameter\.table\_schema | string |  `mssql table schema` 
action\_result\.data\.\*\.TABLE\_CATALOG | string | 
action\_result\.data\.\*\.TABLE\_NAME | string |  `mssql table name` 
action\_result\.data\.\*\.TABLE\_SCHEMA | string |  `mssql table schema` 
action\_result\.data\.\*\.TABLE\_TYPE | string | 
action\_result\.summary\.dataset\:0\:columns | numeric | 
action\_result\.summary\.dataset\:0\:rows | numeric | 
action\_result\.summary\.num\_datasets | numeric | 
action\_result\.summary\.num\_tables | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'run query'
Run a query against a table or tables in the database

Type: **investigate**  
Read only: **False**

It is recommended to use the <b>format\_vars</b> parameter when applicable\. For example, if you wanted to find a specific IP, you could set <b>query</b> to a formatted string, like "select \* from my\_hosts where ip = %s" \(note the use of %s\), and set <b>format\_vars</b> to the IP address\. This will ensure the inputs are safely sanitized and avoid SQL injection attacks\. Regardless of the type of input it's expecting, the only format specifier which should be used is %s\.<br>Setting <b>no\_commit</b> will make it so the App does not commit any changes made to the database \(so you can ensure it's a read only query\)\.<br><br>The <b>format\_vars</b> parameter accepts a comma seperated list\. You can escape commas by surrounding them in double quotes, and escape double quotes with a backslash\. Assuming you have a list of values for the format vars, you can employ this code in your playbooks to properly format it into a string\:<br> <code>format\_vars\_str = ','\.join\(\['"\{\}"'\.format\(str\(x\)\.replace\('\\\\', '\\\\\\\\'\)\.replace\('"', '\\\\"'\)\) for x in format\_vars\_list\]\)</code>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**query** |  required  | Query string | string |  `sql query` 
**format\_vars** |  optional  | Comma separated list of variables | string | 
**no\_commit** |  optional  | Do not commit changes to the Database | boolean | 
**non\_query** |  optional  | Do not run this command in a transaction | boolean | 
**datetime\_to\_iso8601** |  optional  | Convert column types of datetime to iso8601 | boolean | 
**default\_to\_string** |  optional  | Convert any non\-standard column types to string; ie\. datetime | boolean | 
**add\_datasets\_as\_rows** |  optional  | Run query will return each dataset as a separate row in the action result | boolean | 
**host** |  optional  | Optional database hostname or ip address | string |  `hostname`  `host` 
**database** |  optional  | Optional database name | string |  `mssql database name` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.add\_datasets\_as\_rows | boolean | 
action\_result\.parameter\.database | string |  `mssql database name` 
action\_result\.parameter\.datetime\_to\_iso8601 | boolean | 
action\_result\.parameter\.default\_to\_string | boolean | 
action\_result\.parameter\.format\_vars | string | 
action\_result\.parameter\.host | string |  `hostname`  `host` 
action\_result\.parameter\.no\_commit | boolean | 
action\_result\.parameter\.non\_query | boolean | 
action\_result\.parameter\.query | string |  `sql query` 
action\_result\.data\.\*\.\_\_name\_not\_provided\_\_0 | string | 
action\_result\.data\.\*\.age | numeric | 
action\_result\.data\.\*\.baz | string | 
action\_result\.data\.\*\.bod | numeric | 
action\_result\.data\.\*\.created\_at | string | 
action\_result\.data\.\*\.dataset | string | 
action\_result\.data\.\*\.dataset\.\*\.age | numeric | 
action\_result\.data\.\*\.dataset\.\*\.bod | numeric | 
action\_result\.data\.\*\.dataset\.\*\.created\_at | string | 
action\_result\.data\.\*\.dataset\.\*\.float\_column | string | 
action\_result\.data\.\*\.dataset\.\*\.name | string | 
action\_result\.data\.\*\.dataset\.\*\.petname | string | 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.description\.age\.type\_code | numeric | 
action\_result\.data\.\*\.description\.bod\.type\_code | numeric | 
action\_result\.data\.\*\.description\.created\_at\.type\_code | numeric | 
action\_result\.data\.\*\.description\.float\_column\.type\_code | numeric | 
action\_result\.data\.\*\.description\.mydate\.type\_code | numeric | 
action\_result\.data\.\*\.description\.name\.type\_code | numeric | 
action\_result\.data\.\*\.description\.petname\.type\_code | numeric | 
action\_result\.data\.\*\.float\_column | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.petname | string | 
action\_result\.summary\.dataset\:0\:columns | numeric | 
action\_result\.summary\.dataset\:0\:rows | numeric | 
action\_result\.summary\.num\_datasets | numeric | 
action\_result\.summary\.num\_rows | numeric | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 