[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2017-2023 Splunk Inc."
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
