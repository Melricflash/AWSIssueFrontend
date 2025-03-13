import json
import os

import boto3
from flask import Flask, jsonify, request, render_template, url_for, redirect, flash
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)

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

# Bedrock client for LLM stuff, note that its region locked
bedrock_client = boto3.client("bedrock-runtime", region_name = "us-east-1")

# Set the model
model_id = "amazon.titan-text-express-v1"

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

# Function to invoke an LLM for a quick fix suggestion
def ask_llm(prompt):
    # Invoke the LLM
    native_request = {
        "inputText": "You are acting as a professional software engineer, responding to issues from a user. You are not allowed to ask for extra information but must give a suggested solution for other IT engineers. Here is your prompt. "+ prompt,
        "textGenerationConfig": {
            "maxTokenCount": 512,
            "temperature": 0.5
        }
    }

    # Convert to JSON
    llm_request = json.dumps(native_request)

    llm_response = None

    try:
        llm_response = bedrock_client.invoke_model(modelId=model_id, body=llm_request)

    except Exception as err:
        print(f"Failed to invoke model: {err}")

    # Decode and retrieve the model response
    model_response = json.loads(llm_response["body"].read())
    response_text = model_response["results"][0]["outputText"]

    print(response_text)

    return response_text


# allow methods GET and POST, if GET show the form, if POST start sending to queue
@app.route("/", methods = ["GET", "POST"])
def send_to_queue():
    # Check if function accessed from a POST
    if request.method == "POST":
        if request.is_json:
            # Parse JSON response from API
            data = request.get_json()
            title = data.get("title")
            description = data.get("description")
            priority = data.get("priority")
            # Ensure that the priority is a string to be able to be mapped to
            priority = str(priority)

        else:
            # Parse form response if not sent using JSON
            title = request.form['title']
            description = request.form['description']
            priority = request.form['priority']

        # print(title)
        # print(description)
        # print(type(priority))

        if not title or not description or priority not in priorityMapper:
            return jsonify({'message': 'Invalid Form / Invalid JSON Request, please try again!'}), 500

        # Get the right queue according to the priority
        queue_url = priorityMapper[str(priority)]

        # Invoke LLM
        response_text = ask_llm(title + ": " + description)

        message = {
            "title": title,
            "description": description + "\nSuggestion from evil LLM:\n" + response_text
        }

        try:
            sqs.send_message(QueueUrl = queue_url, MessageBody = str(message))
            print("Successfully sent to AWS SQS!")
            #return jsonify({'message': 'Successfully sent message to AWS SQS!'}), 200
            flash('Successfully sent message!', 'success')  # Flash a success message
            return redirect(url_for("send_to_queue"))

        except Exception as err:
            print(f"Failed to send to SQS: {err}")
            # Return an error if an issue occurred when sending to queue
            return jsonify({'message': f'Failed to send to SQS: {err}'}, 500)

    # Create and setup up queue body
    # Send to correct queue according to priority

    # If request is GET
    return render_template('index.html')