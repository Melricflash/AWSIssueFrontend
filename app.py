import os

import boto3
from flask import Flask, jsonify, request, render_template, url_for, redirect
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Reading from environmental variables
aws_access_key = os.getenv('AWS_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_SECRET_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION')

p1Url = os.getenv('p1Queue_URL')
p2Url = os.getenv('p2Queue_URL')
p3Url = os.getenv('p3Queue_URL')

# AWS SQS Setup
sqs = boto3.client('sqs',
                   aws_access_key_id = aws_access_key,
                   aws_secret_access_key = aws_secret_key,
                   region_name = aws_region # Move to environment later
                   )

# Dictionary to map priority to a queue URL
priorityMapper = {
    "1": p1Url,
    "2": p2Url,
    "3": p3Url
}


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
        # data = request.get_json()
        # print(data)
        # title = data["title"]
        # description = data["description"]
        # priority = data["priority"]

        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']

        if not title or not description or priority not in priorityMapper:
            return jsonify({'message': 'Form invalid, please try again!'}), 500

        print(title, description, priority)

        # Get the right queue according to the priority
        queue_url = priorityMapper[str(priority)]

        message = {
            "title": title,
            "description": description,
        }

        try:
            sqs.send_message(QueueUrl = queue_url, MessageBody = str(message))
            #return jsonify({'message': 'Successfully sent message to AWS SQS!'}), 200
            print("Successfully sent to AWS SQS!")
            return redirect(url_for("send_to_queue"))
        except Exception as err:
            print(f"Failed to send to SQS: {err}")
            # Return an error if an issue occurred when sending to queue
            return jsonify({'message': f'Failed to send to SQS: {err}'}, 500)

    # Create and setup up queue body
    # Send to correct queue according to priority

    # If request is GET
    return render_template('index.html')