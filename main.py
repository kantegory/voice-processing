#!/usr/bin/python3
from __future__ import print_function
import time
import boto3
import botocore
import requests
import json
import argparse
from config import *


def get_results(filename, bucket):
    transcribe = session.client('transcribe')
    job_name = "jobname{}".format(filename)
    job_uri = "https://s3.{}.amazonaws.com/{}/{}".format(CONFIG['region_name'], bucket, filename)

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)

    # status = transcribe.get_transcription_job(TranscriptionJobName=job_name)

    link = status['TranscriptionJob']['Transcript']['TranscriptFileUri']

    r = requests.get(link)
    result = json.loads(r.text)
    result = result['results']['items']
    print(result)

    return result


def file2bucket(filename, bucket):
    # Upload a new file
    data = open(filename, 'rb')
    s3.Bucket(bucket).put_object(Key=filename, Body=data)


def create_bucket(bucket):
    # all_buckets = s3.buckets.filter().all()
    # return all_buckets[0]
    try:
        s3.meta.client.head_bucket(Bucket=bucket)
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = e.response['Error']['Code']
        if error_code == '404':
            exists = False

    return bucket

    # if (all_buckets) == 0:
    #     s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint': CONFIG['region_name']})
    #     return all_buckets[0]
    #
    # else:
    #     return all_buckets[0]


def speech2text(filename):
    bucket = create_bucket('mlhack')

    # uploading file to aws bucket
    file2bucket(filename, bucket)

    # getting result of speech2text
    result = get_results(filename, bucket)

    return result


if __name__ == "__main__":
    session = boto3.Session(
        aws_access_key_id=CONFIG['aws_access_key_id'],
        aws_secret_access_key=CONFIG['aws_secret_access_key'],
        region_name=CONFIG['region_name']
    )

    s3 = session.resource('s3')

    parser = argparse.ArgumentParser(description='Write path to file')
    parser.add_argument('filename', type=str)
    filename = vars(parser.parse_args())['filename']
    speech2text(filename)
