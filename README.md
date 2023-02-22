# Fetch Rewards Assessment
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

### Once connected to database, you can run sql queries to interact with the data inside the databases.


## Code

* The script begins by importing the necessary libraries: json, subprocess, localstack_client.session, hashlib, pandas, psycopg2, datetime, and configparser.

* The path to the config.properties file is then set. This file contains the configuration for the SQS queue and database.

* The script then fetches data from the AWS SQS Queue via a custom localstack image. It uses the awslocal command to receive messages from the SQS queue.

* The received data is then transformed using pandas. The ip and device_id data is masked by hashing the values in the respective columns and storing them in the new ip_masked and device_id_masked columns. Duplicate ip and device_id values are also handled.

* Finally, the transformed data is loaded into a PostgreSQL database. The script creates two tables: masked_values_info and user_logins. The masked_values_info table stores the unmasked and masked values of ip and device_id. The user_logins table stores the flattened and masked data.

_Note: The app version in the received data is checked to determine if it is in the appropriate integer format. If not, it is converted to an appropriate integer value before being loaded into the database._

## Questions Part 1 (Implementation Questions):
* How will you read messages from the queue?
#### This script fetches data from AWS SQS Queue via custom localstack image, performs data transformations on the data, and finally loads the transformed data into a PostgreSQL database. The script first imports required libraries such as json, subprocess, localstack_client.session from boto3, hashlib, pandas, psycopg2, datetime, and configparser. It then reads the credentials for the AWS client and SQS queue name from the config.properties file and creates an AWS SQS client using the boto3 library. It then creates an SQS queue URL and uses the awslocal command to receive messages from the SQS queue. The received data is stored in a list.

* What type of data structures should be used?
#### The data structures used are python dictionaries since it is compatible to parse json data. The script then also uses pandas to normalize the received data and creates new columns called ip_masked and device_id_masked.
* How will you mask the PII data so that duplicate values can be identified?
#### To mask the PII data, the hashlib library is used. It hashes the values in the ip and device_id columns and stores them in the respective masked columns. It also finds duplicates in the ip and device_id columns and updates the corresponding masked columns.
* What will be your strategy for connecting and writing to Postgres?
#### The script then creates a database connection using the psycopg2 library and retrieves the database credentials from the config.properties file. It creates a table called masked_values_info to store corresponding unmasked and masked values of the IP address and device ID. It then loops through the masked dataframe and inserts each row into the table. It then creates a table called user_logins to hold the flattened and masked data. It inserts the flattened and masked data into the table by looping through the dataframe using to_dict() method. The script has a function called checkVersionValue(ver) that checks the value of the app version and converts it to an appropriate integer value if it has a non-integer value such as 2.3.5.
* Where and how will your application run?
#### The application can run on any server or cloud environment that supports Python and the necessary libraries used in the solution. The application can be deployed as a standalone process or as a containerized application using a containerization technology such as Docker. In addition, the solution can be run on a serverless environment, such as AWS Lambda or Google Cloud Functions, where the code can be triggered by an event from the message queue. The choice of deployment method will depend on various factors such as the organization's infrastructure, budget, and scalability requirements.

## Questions Part 2 (General):
* How would you deploy this application in production?
#### 1. Set up a production environment: We would need to set up a production environment with the required infrastructure to run the application, including the web server, database, and any other services that the application requires. 
#### 2. Configure the application: We would need to configure the application with the appropriate environment variables and settings for the production environment.
#### 3. Build and package the application: We would need to build and package the application for deployment to the production environment.
#### 4. Deploy the application: We would then deploy the application to the production environment and configure it to run with the appropriate resources and settings.
* What other components would you want to add to make this production ready?
#### Components to Make the Application Production Ready:
#### To make the application production-ready, we would want to add the following components:

#### 1. Load balancer: A load balancer would distribute incoming traffic across multiple instances of the application to improve performance and availability.
#### 2. Caching layer: Adding a caching layer would reduce the load on the database and improve the application's performance.
#### 3. Monitoring and logging: We would want to add monitoring and logging to track application performance, identify issues, and troubleshoot problems.
#### 4. Security: We would want to implement security measures to protect the application and user data, including SSL/TLS encryption, firewalls, and access control measures.
* How can this application scale with a growing dataset?
#### To scale the application with a growing dataset, we would need to consider horizontal and vertical scaling. Horizontal scaling involves adding more instances of the application to handle the increased load, while vertical scaling involves increasing the resources available to the application instances. Additionally, we may want to consider sharding the database to distribute the load across multiple database servers.
* How can PII be recovered later on?
#### For this purpose, we have created a new postgres table named masked_values_info which stores masked and corresponding unmasked values which can be kept as restricted to access. The values can be easily fetched from the table for PII recovery.
* What are the assumptions you made?
#### There are several assumptions made in the code provided, including:

1. The application is only handling a small number of records.
2. The database connection settings are hard-coded in the application code.
3. The database schema is already set up with the required tables and columns.
4. The input data is properly formatted and validated before being stored in the database.