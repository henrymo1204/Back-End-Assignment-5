import boto3

# Get the service resource.
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

# Create the DynamoDB table.
table1 = dynamodb.create_table(
    TableName='direct_messages',
    KeySchema=[
        {
            'AttributeName': 'message_id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'message_id',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait until the table exists.
table1.meta.client.get_waiter('table_exists').wait(TableName='direct_messages')


# Create the DynamoDB table.
table2 = dynamodb.create_table(
    TableName='users',
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'username',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait until the table exists.
table2.meta.client.get_waiter('table_exists').wait(TableName='direct_messages')
