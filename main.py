#!/usr/bin/python3
from __future__ import print_function
import time
import boto3
import botocore
import requests
import json
import argparse
from config import *


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


def file2bucket(filename, bucket):
    # Upload a new file
    data = open(filename, 'rb')
    s3.Bucket(bucket).put_object(Key=filename, Body=data)


def speech2text(filename, bucket):
    transcribe = session.client('transcribe')
    job_name = "1jobname12{}".format(filename)
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
    # result = result['results']['transcripts'][0]['transcript']
    print(result)

    return result


def json2ssml(json):
    words = json
    ssml = ''

    for i in range(len(words)):
        word_type = words[i]['type']

        if word_type == 'pronunciation':

            start = float(words[i]['start_time'])
            end = float(words[i]['end_time'])
            pause = end - start
            # ssml += '<break time="{}ms" />'.format(pause)
            # ssml += '<amazon:breath duration="short" volume="x-loud" />'

        content = words[i]['alternatives'][0]['content']

        ssml += content + ' '

    ssml = '<speak><prosody rate="85%"><amazon:auto-breaths>{}</amazon:auto-breaths></prosody></speak>'.format(ssml)
    print(ssml)

    return ssml


def text2speech(text):
    polly = session.client('polly')

    response = polly.synthesize_speech(
        VoiceId='Joanna',
        OutputFormat='mp3',
        Text=text,
        TextType='ssml'
    )

    file = open('speech.mp3', 'wb')
    file.write(response['AudioStream'].read())
    file.close()


def remove_accent(filename):
    bucket = create_bucket('mlhack')

    # uploading file to aws bucket
    file2bucket(filename, bucket)

    # getting result of speech2text
    speech2text_result = speech2text(filename, bucket)
    ssml = json2ssml(speech2text_result)
    text2speech_result = text2speech(ssml)


if __name__ == "__main__":
    session = boto3.Session(
        aws_access_key_id=CONFIG['aws_access_key_id'],
        aws_secret_access_key=CONFIG['aws_secret_access_key'],
        region_name=CONFIG['region_name']
    )

    s3 = session.resource('s3')

    ssml = json2ssml('')
    text2speech(ssml)

    parser = argparse.ArgumentParser(description='Write path to file')
    parser.add_argument('filename', type=str)
    filename = vars(parser.parse_args())['filename']
    remove_accent(filename)
