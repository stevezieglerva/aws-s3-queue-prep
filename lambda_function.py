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


def lambda_handler(event, context):
	if "text_logging" in os.environ:
		log = structlog.get_logger()
	else:
		log = setup_logging()
	log = log.bind(lambda_name="aws-s3-to-es")
	log.critical("started", input_events=json.dumps(event, indent=3))

	files_found = {}
	s3 = boto3.resource('s3')

	if "Records" not in event:
		return_message = get_return_message("Error: No key 'Records' in the event", files_found)
		log.error("invalid_event", return_message=return_message)
		return return_message

	file_refs = get_files_from_s3_lambda_event(event)
	log.critical("got_file_refs", file_refs=file_refs)
	file_text = get_file_text_from_s3_file_urls(file_refs, s3)

	for file in file_text:
		get_index_from_path(file)
		text = file_text[file]
		index_name_from_s3_path = get_index_from_path(file)
		es = ESLambdaLog(index_name_from_s3_path)
		for document_line in text.splitlines():
			log.critical("prepping_to_index_in_ES", file=file, text=document_line, index=index_name_from_s3_path)
			text_json = json.loads(document_line)
			es.log_event(text_json)

	return_message = get_return_message("Success", file_text)
	log.critical("finished", return_message=json.dumps(return_message, indent=3))
	return return_message


def get_index_from_path(path):
	#https://s3.amazonaws.com/aws-s3-to-es/index_name_dir/test.txt
	urlparts = urlparse(path)
	if urlparts.netloc != "s3.amazonaws.com":
		raise ValueError("Expected netloc of '" + path + "' to be 's3.amazonaws.com'") 
	urlpath = urlparts.path
	log = structlog.get_logger()
	log.info("get_index_from_path", path=urlpath)
	path_parts = urlpath.split("/")
	if len(path_parts) < 2:
		raise ValueError("Expected '" + path + "' to have at least two items in the path") 
	if path_parts[1] != "aws-s3-to-es":
		raise ValueError("Expected '" + path + "' to use the aws-s3-to-es bucket.") 
	index_name = ""
	if len(path_parts) == 3:
		index_name = "general"
	if len(path_parts) == 4:
		index_name = path_parts[2]
	return index_name


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


