import boto3

# Get the service resource.
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

# Create the DynamoDB table.
table = dynamodb.create_table(
    TableName='direct_messages',
    KeySchema=[
        {
            'AttributeName': 'message_id',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'to_username',
            'KeyType': 'RANGE',
            'AttributeName': 'from_username',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'message_id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'to_username',
            'AttributeType': 'S',
            'AttributeName': 'from_username',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait until the table exists.
table.meta.client.get_waiter('table_exists').wait(TableName='direct_messages')

