import unittest
import time
from S3TextFromLambdaEvent import *
import boto3


class TestMethods(unittest.TestCase):

	def test_get_file_text_from_s3_file_urls__one_file__one_file_text_returned(self):
		# Arrange
		s3 = boto3.resource('s3')
		bucket = "aws-s3-to-es"
		key = "integration_test_1.txt"
		file_text = "test_1.txt file contents"
		file_text_binary = bytes(file_text, 'utf-8')
		object = s3.Object(bucket, key)
		object.put(Body=file_text_binary)

		s3_list = {}
		s3_url = "https://s3.amazonaws.com/" + bucket + "/" + key
		s3_list[s3_url] = {"bucket" : bucket, "key" : key}
				
		# Act
		result = get_file_text_from_s3_file_urls(s3_list, s3)
		print(result)

		# Assert
		self.assertEqual(len(result), 1)
		self.assertEqual(result[s3_url], file_text)

if __name__ == '__main__':
	unittest.main()		


