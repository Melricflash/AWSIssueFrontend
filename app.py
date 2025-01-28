import os

import boto3
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

aws_access_key = os.getenv('AWS_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_SECRET_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION')
p1Url = os.getenv('p1Queue_URL')

sqs = boto3.client('sqs',
                   aws_access_key_id = aws_access_key,
                   aws_secret_access_key = aws_secret_key,
                   region_name = aws_region # Move to environment later
                   )

'''
{
    "title": "hello",
    "description": "Test description",
    "priority": 1
}
'''
# allow methods GET and POST, if GET show the form, if POST start sending to queue
@app.route("/", methods = ["GET", "POST"])
def send_to_queue():
    # Check if function accessed from a POST
    if request.method == "POST":
        # Parse JSON response
        data = request.get_json()
        print(data)
        title = data["title"]
        description = data["description"]
        priority = data["priority"]

        queue_url = p1Url

        message = {
            "title": title,
            "description": description,
        }

        try:
            sqs.send_message(QueueUrl = queue_url, MessageBody = str(message))
            return jsonify({'message': 'Successfully sent message to AWS SQS!'}), 200
        except Exception as err:
            print(f"Failed to send to SQS: {err}")
            # Return an error if an issue occurred when sending to queue
            return jsonify({'message': f'Failed to send to SQS: {err}'}, 500)

    # Create and setup up queue body
    # Send to correct queue according to priority

    # If request is GET
    return "<h1> Test </h1>"