# Importing required libraries
import json
import subprocess
import localstack_client.session as boto3
import hashlib
import pandas as pd
import psycopg2
import datetime
import configparser

# Update the path below. It needs a path for config.properties file.
path = '/Users/mayurdeshmukh/Desktop/Fetch_DataEngineering_Assessment'

# Using configparser library to parse the configurations credentials stored in config.properties file.
config = configparser.ConfigParser()
config.read('{}/config.properties'.format(path))

###### Objective 1 - Fetch data from AWS SQS Queue via custom localstack image
###### DataPrep Step

# Retrieving AWS client and queue name from the config file
client = config.get('aws','client')
queuename = config.get('aws','queuename')

# Creating an AWS SQS client
sqs = boto3.client(client)

# Creating an SQS queue URL
queue_url = sqs.create_queue(QueueName=queuename)["QueueUrl"]
# print(queue_url)

# Using awslocal command to receive message from SQS queue
op = subprocess.check_output(['awslocal','sqs','receive-message','--queue-url', queue_url])
msgs = json.loads(op.decode('utf-8'))['Messages']

# Creating a list to store the received data
data = []
for m in msgs:
    body = json.loads(m['Body'])
    data.append(body)


###### Objective 2 - Data Transformation Step

# Using pandas to normalize the received data
df = pd.json_normalize(data)

# masking device_id and ip address data

# Creating new columns called 'ip_masked' and 'device_id_masked'
df['ip_masked'] = ''
df['device_id_masked'] = ''

# Hashing the values in 'ip' and 'device_id' columns and storing in respective masked columns
for index, row in df.iterrows():
    ip_hashed_value = hashlib.sha256(row['ip'].encode('utf-8')).hexdigest()
    df.loc[index, 'ip_masked'] = ip_hashed_value

    device_id_hashed_value = hashlib.sha256(row['device_id'].encode('utf-8')).hexdigest()
    df.loc[index, 'device_id_masked'] = device_id_hashed_value

# Finding duplicates in 'ip' column and updating 'ip_masked' column
duplicates_ip = df[df.duplicated(['ip'], keep=False)]
for index, row in duplicates_ip.iterrows():
    hashed_value = hashlib.sha256(row['ip'].encode('utf-8')).hexdigest()
    df.loc[index, 'ip_masked'] = 'DUP_' + hashed_value

# Finding duplicates in 'device_id' column and updating 'device_id_masked' column
duplicates_device_id = df[df.duplicated(['device_id'], keep=False)]
for index, row in duplicates_device_id.iterrows():
    hashed_value = hashlib.sha256(row['device_id'].encode('utf-8')).hexdigest()
    df.loc[index, 'device_id_masked'] = 'DUP_' + hashed_value

# print(df)

###### Objective 3 - Data Load Step

# The below function checks the value of app version and check whether it has non integer value as (2.3.5). 
# If so then convert it to an appropriate integer value. It is done because according to our DDL the column app version is integer.
# Also there is nan check, since there are some app version values corresponding to nan.
def checkVersionValue(ver):
    if ver == "nan" or not ver:
        return 0
    if isinstance(ver, str):
        try:
            version_int = int(ver.replace(".", ""))
        except ValueError:
            version_int = 0
    else:
        version_int = 0
    return version_int

# Retrieving database credentials from the config file
username = config.get('database','username')
password = config.get('database', 'password')
hostname = config.get('database', 'hostname')
dbname = config.get('database', 'dbname')

conn = psycopg2.connect(host=hostname, dbname=dbname, user=username, password=password)

cur = conn.cursor()

# Create the table in the database if it doesn't exist
# The reason to create this table is to store corresponding unmasked and masked values of ip address and device id
# The table can only be accessed by priveledged personnels only
cur.execute('CREATE TABLE IF NOT EXISTS masked_values_info (id SERIAL PRIMARY KEY, ip TEXT, ip_masked TEXT, device_id TEXT, device_id_masked TEXT)')

# Loop through the masked dataframe and insert each row into the table
for index, row in df.iterrows():
    cur.execute("INSERT INTO masked_values_info (ip, ip_masked, device_id, device_id_masked) VALUES (%s, %s, %s, %s)", (row['ip'], row['ip_masked'], row['device_id'], row['device_id_masked']))

# Create a table to hold the flattened and masked data
cur.execute('CREATE TABLE IF NOT EXISTS user_logins (user_id VARCHAR(128), device_type VARCHAR(32), masked_ip VARCHAR(256), masked_device_id VARCHAR(256), locale VARCHAR(32), app_version INTEGER, create_date DATE)')

# Get the current date
current_date = datetime.date.today()
# print(current_date)

# Insert the flattened and masked data into the table
for row in df.to_dict('records'):
    # Need to check whether the app version is in integer format, if not then it will convert to integer and store into db
    version_val = checkVersionValue(row['app_version'])
    cur.execute("INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date) VALUES (%s, %s, %s, %s, %s, %s, %s)", (row['user_id'], row['device_type'], row['ip_masked'], row['device_id_masked'], row['locale'], version_val, current_date))

# Commits the commands to db 
conn.commit()

# Close all connection objects
cur.close()
conn.close()