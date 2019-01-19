import boto3
import json
import datetime
import time
from ESLambdaLog import *
from LocalTime import *
from S3TextFromLambdaEvent import *
import sys
import os
import traceback
import logging
import structlog
from urllib.parse import urlparse
import re
from firehose_helpers import *
from urllib.parse import urlparse
import os.path

def lambda_handler(event, context):
	try:
		if "text_logging" in os.environ:
			log = structlog.get_logger()
		else:
			log = setup_logging()
			log = log.bind(aws_request_id=context.aws_request_id)
			log = log.bind(lambda_name=context.function_name)
		log.critical("started", input_events=json.dumps(event, indent=3))

		env_vars = get_environment_variables_with_defaults(os.environ)
		print()
		print("Environment Variables:")
		print(env_vars)
		files_found = {}
		s3 = boto3.resource("s3")

		if "Records" not in event:
			return_message = get_return_message("Error: No key 'Records' in the event", files_found)
			log.error("invalid_event", return_message=return_message)
			return return_message

		file_refs = get_files_from_s3_lambda_event(event)
		file_text = get_file_text_from_s3_file_urls(file_refs, s3)
		print("Found files:")
		count = 0
		bytes_processed = 0
		for file in file_text:
			count = count + 1 
			print(str(count) + ". " + file)
			log = log.bind(processing_file=file)
			text = file_text[file]
			bytes_processed = len(text)
			for env_variable in ["regex_1", "regex_2", "regex_3"]:
				if env_vars[env_variable] != "":
					regex_parts = env_vars[env_variable].split("-;-")
					regex_find = regex_parts[0]
					regex_replace = regex_parts[1]
					text = re.sub(regex_find, regex_replace, text)
			dest_file = get_destination_file_url(env_vars["file_path_regex"] , file)
			create_updated_file_in_destination(s3, dest_file, text)
			move_processed_file(s3, file)
		print("finished")
		return_message = get_return_message("Success", file_refs)
		print("")
		log.critical("process_results", input_file_count=len(file_refs), processed_file_count=count, bytes_processed=bytes_processed)
		log.critical("finished", return_message=json.dumps(return_message, indent=3))
		return return_message
	except Exception as e:
		exception_name = type(e).__name__
		print("Exception occurred: " + exception_name + "=" + str(e))
		log.exception("exception", exception_name=exception_name)
		return_message = get_return_message("Exception occurred", {})
		return return_message


def get_destination_file_url(file_path_regex, source_file):
	destination_file_url = ""
	if file_path_regex != "":
		regex_parts = file_path_regex.split("-;-")
		regex_find = regex_parts[0]
		regex_replace = regex_parts[1]
		destination_file_url = re.sub(regex_find, regex_replace, source_file)
	return destination_file_url


def get_environment_variables_with_defaults(environ):
	env_variables_set = {}
	for env_variable in ["regex_1", "regex_2", "regex_3", "file_path_regex", "exclude_file_filters"]:
		env_variables_set[env_variable] = ""
		if env_variable in environ:
			if "-;-" not in environ[env_variable]:
				raise ValueError("Expected " + env_variable + " environment variable to have a -;- separating the find clause from the replace clause.")
			env_variables_set[env_variable] = environ[env_variable]
	if env_variables_set["file_path_regex"] == "":
		env_variables_set["file_path_regex"] = "prep-input-;-prep-output"
	if env_variables_set["exclude_file_filters"] == "":
		env_variables_set["exclude_file_filters"] = ".*\.zip|.*\.jar"

	return env_variables_set


def create_updated_file_in_destination(s3, dest_file_url, text):
	print("\tWriting to: " + dest_file_url)
	dest_bucket = get_bucket_name_from_url(dest_file_url)
	dest_key = get_key_from_url(dest_file_url)
	s3.meta.client.put_object(Bucket=dest_bucket, Key=dest_key, Body=text)


def move_processed_file(s3, source_file_url):
	print("\tDeleting from: " + source_file_url)
	source_bucket = get_bucket_name_from_url(source_file_url)
	source_key = get_key_from_url(source_file_url)
	s3.meta.client.delete_object(Bucket=source_bucket, Key=source_key)


def create_es_file_to_index(filename, file_text):
	data = {}
	data["filename"] = filename
	data["file_text"] = file_text
	create_es_event(index="code-index", id=filename, data=data)


def get_return_message(msg, files_found):
	return_message = {}
	return_message["msg"] = msg
	return_message["files_found"] = files_found
	return return_message
	
def setup_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO
    )
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()




