# Fetch Rewards
The repo contains code which was required for data engineering intern assessment.

## Overview

This script fetches data from an AWS SQS Queue via a custom localstack image. It then applies data transformations to the received data and loads the transformed data into a PostgreSQL database.

## Requirements

Python 3.x
Pandas
Psycopg2
configparser
localstack-client
AWS CLI

## Installation

Install Python 3.x from https://www.python.org/downloads/

Install Pandas, Psycopg2, configparser, localstack-client, and AWS CLI using pip:
```
pip install pandas psycopg2 configparser localstack-client awscli
```

## Usage

Modify the path in the code to point to the config.properties file.
Modify the values in the config.properties file to reflect the configuration for the SQS queue and database.

Run the script using the following command:
```
python ETL.py
```

## Code

The script begins by importing the necessary libraries: json, subprocess, localstack_client.session, hashlib, pandas, psycopg2, datetime, and configparser.

The path to the config.properties file is then set. This file contains the configuration for the SQS queue and database.

The script then fetches data from the AWS SQS Queue via a custom localstack image. It uses the awslocal command to receive messages from the SQS queue.

The received data is then transformed using pandas. The ip and device_id data is masked by hashing the values in the respective columns and storing them in the new ip_masked and device_id_masked columns. Duplicate ip and device_id values are also handled.

Finally, the transformed data is loaded into a PostgreSQL database. The script creates two tables: masked_values_info and user_logins. The masked_values_info table stores the unmasked and masked values of ip and device_id. The user_logins table stores the flattened and masked data.

_Note: The app version in the received data is checked to determine if it is in the appropriate integer format. If not, it is converted to an appropriate integer value before being loaded into the database._