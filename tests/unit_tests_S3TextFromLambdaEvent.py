import unittest
import time
from S3TextFromLambdaEvent import *
import boto3
import json


class TestMethods(unittest.TestCase):

	def test_get_bucket_name_from_url__valid_url__returns_correct_parts(self):
		# Arrange
		subject = "https://s3.amazonaws.com/code-index/prep-input/USTIF/2018-05-27-235740.txt"

		# Act
		result = get_bucket_name_from_url(subject)

		# Assert
		print(result)
		self.assertEqual(result, "code-index")

	def test_get_key_from_url__valid_url__returns_correct_parts(self):
		# Arrange
		subject = "https://s3.amazonaws.com/code-index/prep-input/USTIF/2018-05-27-235740.txt"

		# Act
		result = get_key_from_url(subject)

		# Assert
		print(result)
		self.assertEqual(result, "prep-input/USTIF/2018-05-27-235740.txt")


		
if __name__ == '__main__':
	unittest.main()		


