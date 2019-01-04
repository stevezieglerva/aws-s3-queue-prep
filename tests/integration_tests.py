import unittest
import time
from S3TextFromLambdaEvent import *
import boto3
from lambda_function import *
import json

event_one_file = {
	"Records": [
		{
		"eventVersion": "2.0",
		"eventTime": "1970-01-01T00:00:00.000Z",
		"requestParameters": {
			"sourceIPAddress": "127.0.0.1"
		},
		"s3": {
			"configurationId": "testConfigRule",
			"object": {
			"eTag": "0123456789abcdef0123456789abcdef",
			"sequencer": "0A1B2C3D4E5F678901",
			"key": "prep-input/ProjectX/integration_test_2.txt",
			"size": 1024
			},
			"bucket": {
			"arn": "arn:aws:s3:::code-index",
			"name": "sourcebucket",
			"ownerIdentity": {
				"principalId": "EXAMPLE"
			}
			},
			"s3SchemaVersion": "1.0"
		},
		"responseElements": {
			"x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH",
			"x-amz-request-id": "EXAMPLE123456789"
		},
		"awsRegion": "us-east-1",
		"eventName": "ObjectCreated:Put",
		"userIdentity": {
			"principalId": "EXAMPLE"
		},
		"eventSource": "aws:s3"
		}
	]
	}

class TestMethods(unittest.TestCase):

	def test_lambda_function__one_file_event__successful_results(self):
		# Arrange
		s3 = boto3.resource('s3')
		bucket = "code-index"
		key = "prep-input/ProjectX/integration_test_2.txt"
		file_text = "import java;\nprint('Hello world'); \n if x <> 5\n-;-"
		file_text_binary = bytes(file_text, 'utf-8')
		object = s3.Object(bucket, key)
		object.put(Body=file_text_binary)

		s3_list = {}
		s3_url = "https://s3.amazonaws.com/" + bucket + "/" + key
		s3_list[s3_url] = {"bucket" : bucket, "key" : key}

		os.environ["regex_1"] = "[^a-zA-Z0-9\\n \\(\\);\'_\-+\n\t\{\}\*]+-;-"
		os.environ["regex_2"] = "\n-;-     "

		# Act
		result = lambda_handler(event_one_file, None)
		print(json.dumps(result, indent=3))

		# Assert
		self.assertEqual(result["msg"], "Success")




if __name__ == '__main__':
	unittest.main()		


