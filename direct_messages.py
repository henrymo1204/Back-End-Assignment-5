import sys
import textwrap
import logging.config
import sqlite3

import bottle
import bottle_sqlite
from bottle import get, post, delete, error, abort, request, response, HTTPResponse

import boto3
from botocore.exceptions import ClientError
import uuid

import time


# conn = sqlite3.connect('users.db')
# conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username string UNIQUE NOT NULL, password string NOT NULL, emailAddress string UNIQUE)")
# conn.execute("CREATE TABLE followers (id INTEGER PRIMARY KEY, user_id string NOT NULL, user_idToFollow string NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(user_idTOFOllow) REFERENCES users(id))")

app = bottle.default_app()
app.config.load_config('./etc/users.ini')

plugin = bottle_sqlite.Plugin(app.config['sqlite.users'])
app.install(plugin)

logging.config.fileConfig(app.config['logging.config'])


dynamodb = boto3.client('dynamodb', endpoint_url="http://localhost:8000")


def json_error_handler(res):
    if res.content_type == 'application/json':
          return res.body
    res.content_type = 'application/json'
    if res.body == 'Unknown Error.':
          res.body = bottle.HTTP_CODES[res.status_code]
    return bottle.json_dumps({'errors': res.body})


app.default_error_handler = json_error_handler


if not sys.warnoptions:
    import warnings
    for warning in [DeprecationWarning, ResourceWarning]:
          warnings.simplefilter('ignore', warning)


@post('/directMessages')
def sentDirectMessage():
    data = request.json
    posted_fields = data.keys()
    required_fields = {'to', 'from', 'message'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')
        
    f = '%Y-%m-%d %H:%M:%S'
    now = time.localtime()
    now = time.strftime(f, now)
    
    mid = str(uuid.uuid4())
        
    dynamodb.put_item(TableName='direct_messages', Item={'message_id': {'S': mid}, 'time': {'S': now}, 'to_username': {'S': data['to']}, 'from_username': {'S': data['from']}, 'messages': {'L': [{'S': data['message']}]}})
    
    try:
    	dynamodb.put_item(TableName='users', Item={'username': {'S': data['to']}, 'direct_messages': {'L': [{'S': mid}]}}, ConditionExpression = "attribute_not_exists(username)")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            dynamodb.update_item(TableName='users', Key={'username': {'S': data['to']}}, UpdateExpression="SET direct_messages = list_append(direct_messages, :attrValue)", ExpressionAttributeValues={':attrValue': {'L': [{'S': mid}]}})
            
    try:
    	dynamodb.put_item(TableName='users', Item={'username': {'S': data['from']}, 'direct_messages': {'L': [{'S': mid}]}}, ConditionExpression = "attribute_not_exists(username)")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            dynamodb.update_item(TableName='users', Key={'username': {'S': data['from']}}, UpdateExpression="SET direct_messages = list_append(direct_messages, :attrValue)", ExpressionAttributeValues={':attrValue': {'L': [{'S': mid}]}})
           
    
    return {'message': 'success'}
    
@post('/directMessages/<message_id>')
def replyToDirectMessage(message_id):
    data = request.json
    posted_fields = data.keys()
    required_fields = {'message'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')
    
        
    message = dynamodb.update_item(TableName='direct_messages', Key={'message_id': {'S': message_id}}, UpdateExpression="SET messages = list_append(messages, :attrValue)", ExpressionAttributeValues={':attrValue': {'L': [{'S': data['message']}]}})
    
    return {'message': 'success'}

@get('/directMessages/replies/<message_id>')
def listRepliesTo(message_id):
    messages = dynamodb.get_item(TableName='direct_messages', Key={'message_id': {'S': message_id}})
    msg = messages['Item']['messages']
    return msg
    

@get('/directMessages/replies/<message_id>')
def listDirectMessage(message_id):
    messages = dynamodb.get_item(TableName='direct_messages', Key={'message_id': {'S': message_id}})
    msg = messages['Item']['messages']
    return msg
