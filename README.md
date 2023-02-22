# Fetch Rewards
The repo contains code which was required for data engineering intern assessment.

## Overview

This script fetches data from an AWS SQS Queue via a custom localstack image. It then applies data transformations to the received data and loads the transformed data into a PostgreSQL database.

## Requirements

* Python 3.x
* Pandas
* Psycopg2
* configparser
* localstack-client
* AWS CLI
* Docker
* Postgres
* psql terminal

## Installation

Install Python 3.x from https://www.python.org/downloads/

Install Docker from https://docs.docker.com/get-docker/

Install Pandas, Psycopg2, configparser, localstack-client, and AWS CLI using pip:
```
pip install pandas psycopg2 configparser localstack-client awscli
```

## Usage

To pull the Localstack image from Docker use the following command:
```
docker pull fetchdocker/data-takehome-localstack
```

To start the Localstack container in Docker, use following command
```
docker run -it -p 4566:4566 fetchdocker/data-takehome-localstack:latest
```

Modify the path in the code to point to the config.properties file.
Modify the values in the config.properties file to reflect the configuration for the SQS queue and database.

Run the script using the following command:
```
python ETL.py
```

To check the data in postgres database, use following commands:
To start the docker:
```
docker start
```
To Check containers run the below command:
```
docker ps -a
```
If there is no container running for postgres, then run the below command (if already running then skip this step):
```
docker run -d --name fetchdocker/data-takehome-postgres -p 5432:5432 -e POSTGRES_PASSWORD=your_password postgres:latest
```
After container is created, run the below command to start the container:
```
docker start fetchdocker/data-takehome-postgres
```
Now to connect to postgres database running inside the container, use PostgreSQL client such as psql.
Connect to Postgres database using command:
```
psql -h localhost -p 5432 -U postgres
```

## Once connected to database, you can run sql queries to interact with the data inside the databases;


## Code

* The script begins by importing the necessary libraries: json, subprocess, localstack_client.session, hashlib, pandas, psycopg2, datetime, and configparser.

* The path to the config.properties file is then set. This file contains the configuration for the SQS queue and database.

* The script then fetches data from the AWS SQS Queue via a custom localstack image. It uses the awslocal command to receive messages from the SQS queue.

* The received data is then transformed using pandas. The ip and device_id data is masked by hashing the values in the respective columns and storing them in the new ip_masked and device_id_masked columns. Duplicate ip and device_id values are also handled.

* Finally, the transformed data is loaded into a PostgreSQL database. The script creates two tables: masked_values_info and user_logins. The masked_values_info table stores the unmasked and masked values of ip and device_id. The user_logins table stores the flattened and masked data.

_Note: The app version in the received data is checked to determine if it is in the appropriate integer format. If not, it is converted to an appropriate integer value before being loaded into the database._