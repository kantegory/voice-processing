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
    job_name = "13333223113231211232jobnamefd12{}".format(filename)
    job_uri = "https://s3.{}.amazonaws.com/{}/{}".format(CONFIG['region_name'], bucket, filename)

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp3',
        LanguageCode='en-IN'
    )

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)

    link = status['TranscriptionJob']['Transcript']['TranscriptFileUri']

    r = requests.get(link)
    result = json.loads(r.text)
    result = result['results']['items']
    print(result)

    return result


def get_const(words):
    arr = []
    for word in words:
        if word['type'] == 'pronunciation':
            duration = float(word['end_time']) - float(word['start_time'])
            arr.append(duration)

    const = sum(arr) / len(arr)

    return const


def json2ssml(json):
    words = json
    ssml = ''

    const = get_const(words)

    for i in range(len(words)):
        word_type = words[i]['type']

        if word_type == 'pronunciation':

            next_step = float(words[i]['start_time'])
            prev_step = 0
            pause = next_step - prev_step
            start_time = float(words[i]['start_time'])
            end_time = float(words[i]['end_time'])


            if i > 0:
                prev_word_type = words[i - 1]['type']

                if prev_word_type == 'pronunciation':
                    prev_step = float(words[i - 1]['end_time'])
                    pause = (next_step - prev_step)

                elif words[i - 1]['type'] == 'punctuation':
                    pause = 0

            print(pause)
            ssml += '<break time="{}s" />'.format(pause) if pause != 0 else ' '

            duration = end_time - start_time
            speed = 100 * duration / const

            content = words[i]['alternatives'][0]['content']
            ssml += '{}'.format(content)

    ssml = '<speak><prosody rate="112%">{}</prosody></speak>'.format(ssml)
    print(ssml)

    return ssml


def text2speech(text):
    polly = session.client('polly')

    response = polly.synthesize_speech(
        VoiceId='Joey',
        OutputFormat='mp3',
        Text=text,
        TextType='ssml'
    )

    file = open('with_face__transcribe2.mp3', 'wb')
    file.write(response['AudioStream'].read())
    file.close()


def remove_accent(filename):
    bucket = create_bucket('mlhack')

    # uploading file to aws bucket
    file2bucket(filename, bucket)

    # getting result of speech2text
    speech2text_result = speech2text(filename, bucket)
    ssml = json2ssml(speech2text_result)
    text2speech(ssml)

    return 1


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
    remove_accent(filename)
