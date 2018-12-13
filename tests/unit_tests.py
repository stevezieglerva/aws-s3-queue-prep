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
			"key": "integration_test_2.txt",
			"size": 1024
			},
			"bucket": {
			"arn": "arn:aws:s3:::aws-s3-to-es",
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

	def test_get_environment_variables_with_defaults__os_variables_set__result_set_has_os_variables(self):
		# Arrange
		environ = {}
		environ["dest_bucket"] = "mys3url"
		environ["reg_ex_1"] = ".*"

		# Act
		result = get_environment_variables_with_defaults(environ)
		print(json.dumps(result, indent=3))

		# Assert
		self.assertEqual(result["dest_bucket"], "mys3url")
		self.assertEqual(result["reg_ex_1"], ".*")

	def test_get_environment_variables_with_defaults__empty_os_variables_set__result_set_has_defaults(self):
		# Arrange
		environ = {}

		# Act
		result = get_environment_variables_with_defaults(environ)
		print(json.dumps(result, indent=3))

		# Assert
		self.assertEqual(result["dest_bucket"], "https://s3.amazonaws.com/s3-to-es/bulk")
		self.assertEqual(result["reg_ex_1"], "")
		self.assertEqual(result["reg_ex_2"], "")
		self.assertEqual(result["reg_ex_3"], "")



		
if __name__ == '__main__':
	unittest.main()		


