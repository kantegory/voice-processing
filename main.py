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
    job_name = "132jobnamefd12{}".format(filename)
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
    words = [{'start_time': '0.34', 'end_time': '0.62', 'alternatives': [{'confidence': '0.8605', 'content': 'please'}],
              'type': 'pronunciation'},
             {'start_time': '0.62', 'end_time': '0.82', 'alternatives': [{'confidence': '0.7072', 'content': 'call'}],
              'type': 'pronunciation'},
             {'start_time': '0.82', 'end_time': '1.25', 'alternatives': [{'confidence': '0.9922', 'content': 'Stella'}],
              'type': 'pronunciation'},
             {'start_time': '1.61', 'end_time': '1.93', 'alternatives': [{'confidence': '0.909', 'content': 'asked'}],
              'type': 'pronunciation'},
             {'start_time': '1.93', 'end_time': '2.06', 'alternatives': [{'confidence': '1.0', 'content': 'her'}],
              'type': 'pronunciation'},
             {'start_time': '2.06', 'end_time': '2.19', 'alternatives': [{'confidence': '0.9951', 'content': 'to'}],
              'type': 'pronunciation'},
             {'start_time': '2.19', 'end_time': '2.49', 'alternatives': [{'confidence': '1.0', 'content': 'bring'}],
              'type': 'pronunciation'},
             {'start_time': '2.49', 'end_time': '2.7', 'alternatives': [{'confidence': '1.0', 'content': 'these'}],
              'type': 'pronunciation'},
             {'start_time': '2.7', 'end_time': '3.23', 'alternatives': [{'confidence': '1.0', 'content': 'things'}],
              'type': 'pronunciation'},
             {'start_time': '3.24', 'end_time': '3.42', 'alternatives': [{'confidence': '0.7587', 'content': 'with'}],
              'type': 'pronunciation'},
             {'start_time': '3.42', 'end_time': '3.69', 'alternatives': [{'confidence': '0.9976', 'content': 'her'}],
              'type': 'pronunciation'},
             {'start_time': '3.82', 'end_time': '4.26', 'alternatives': [{'confidence': '1.0', 'content': 'from'}],
              'type': 'pronunciation'},
             {'start_time': '4.26', 'end_time': '4.39', 'alternatives': [{'confidence': '1.0', 'content': 'the'}],
              'type': 'pronunciation'},
             {'start_time': '4.39', 'end_time': '4.84', 'alternatives': [{'confidence': '1.0', 'content': 'store'}],
              'type': 'pronunciation'},
             {'alternatives': [{'confidence': '0.0', 'content': '.'}], 'type': 'punctuation'},
             {'start_time': '5.08', 'end_time': '5.46', 'alternatives': [{'confidence': '0.9975', 'content': 'Six'}],
              'type': 'pronunciation'},
             {'start_time': '5.46', 'end_time': '5.83', 'alternatives': [{'confidence': '0.9523', 'content': 'spoons'}],
              'type': 'pronunciation'},
             {'start_time': '5.83', 'end_time': '5.96', 'alternatives': [{'confidence': '0.7256', 'content': 'off'}],
              'type': 'pronunciation'},
             {'alternatives': [{'confidence': '0.0', 'content': ','}], 'type': 'punctuation'},
             {'start_time': '5.96', 'end_time': '6.39', 'alternatives': [{'confidence': '1.0', 'content': 'fresh'}],
              'type': 'pronunciation'},
             {'start_time': '6.4', 'end_time': '6.63', 'alternatives': [{'confidence': '0.8277', 'content': 'snow'}],
              'type': 'pronunciation'},
             {'start_time': '6.63', 'end_time': '7.16', 'alternatives': [{'confidence': '0.9211', 'content': 'peas'}],
              'type': 'pronunciation'},
             {'alternatives': [{'confidence': '0.0', 'content': ','}], 'type': 'punctuation'},
             {'start_time': '7.36', 'end_time': '8.0', 'alternatives': [{'confidence': '0.99985', 'content': '56'}],
              'type': 'pronunciation'},
             {'start_time': '8.0', 'end_time': '8.27', 'alternatives': [{'confidence': '0.9456', 'content': 'laps'}],
              'type': 'pronunciation'},
             {'start_time': '8.27', 'end_time': '8.4', 'alternatives': [{'confidence': '0.5778', 'content': 'of'}],
              'type': 'pronunciation'},
             {'start_time': '8.4', 'end_time': '8.61', 'alternatives': [{'confidence': '0.9612', 'content': 'blue'}],
              'type': 'pronunciation'},
             {'start_time': '8.61', 'end_time': '9.07', 'alternatives': [{'confidence': '0.9998', 'content': 'cheese'}],
              'type': 'pronunciation'},
             {'start_time': '9.83', 'end_time': '10.01', 'alternatives': [{'confidence': '1.0', 'content': 'and'}],
              'type': 'pronunciation'},
             {'start_time': '10.01', 'end_time': '10.3', 'alternatives': [{'confidence': '0.9859', 'content': 'maybe'}],
              'type': 'pronunciation'},
             {'start_time': '10.3', 'end_time': '10.36', 'alternatives': [{'confidence': '1.0', 'content': 'a'}],
              'type': 'pronunciation'},
             {'start_time': '10.36', 'end_time': '10.8', 'alternatives': [{'confidence': '0.9952', 'content': 'stack'}],
              'type': 'pronunciation'},
             {'start_time': '10.81', 'end_time': '11.26', 'alternatives': [{'confidence': '0.9974', 'content': 'off'}],
              'type': 'pronunciation'}, {'start_time': '11.27', 'end_time': '11.63',
                                         'alternatives': [{'confidence': '0.9984', 'content': 'snack'}],
                                         'type': 'pronunciation'},
             {'start_time': '11.63', 'end_time': '11.84', 'alternatives': [{'confidence': '0.9944', 'content': 'for'}],
              'type': 'pronunciation'},
             {'start_time': '11.84', 'end_time': '12.05', 'alternatives': [{'confidence': '0.9573', 'content': 'her'}],
              'type': 'pronunciation'}, {'start_time': '12.05', 'end_time': '12.33',
                                         'alternatives': [{'confidence': '0.9862', 'content': 'brother'}],
                                         'type': 'pronunciation'},
             {'start_time': '12.33', 'end_time': '12.66', 'alternatives': [{'confidence': '0.4526', 'content': 'book'}],
              'type': 'pronunciation'},
             {'alternatives': [{'confidence': '0.0', 'content': '.'}], 'type': 'punctuation'},
             {'start_time': '13.79', 'end_time': '13.91', 'alternatives': [{'confidence': '0.9795', 'content': 'We'}],
              'type': 'pronunciation'},
             {'start_time': '13.91', 'end_time': '14.15', 'alternatives': [{'confidence': '1.0', 'content': 'also'}],
              'type': 'pronunciation'},
             {'start_time': '14.15', 'end_time': '14.35', 'alternatives': [{'confidence': '1.0', 'content': 'need'}],
              'type': 'pronunciation'},
             {'start_time': '14.35', 'end_time': '14.41', 'alternatives': [{'confidence': '1.0', 'content': 'a'}],
              'type': 'pronunciation'}, {'start_time': '14.41', 'end_time': '14.71',
                                         'alternatives': [{'confidence': '0.9995', 'content': 'small'}],
                                         'type': 'pronunciation'}, {'start_time': '14.71', 'end_time': '15.11',
                                                                    'alternatives': [
                                                                        {'confidence': '0.9988', 'content': 'plastic'}],
                                                                    'type': 'pronunciation'},
             {'start_time': '15.11', 'end_time': '15.41',
              'alternatives': [{'confidence': '0.9408', 'content': 'snake'}], 'type': 'pronunciation'},
             {'start_time': '15.88', 'end_time': '16.07', 'alternatives': [{'confidence': '1.0', 'content': 'and'}],
              'type': 'pronunciation'},
             {'start_time': '16.07', 'end_time': '16.11', 'alternatives': [{'confidence': '1.0', 'content': 'a'}],
              'type': 'pronunciation'},
             {'start_time': '16.11', 'end_time': '16.35', 'alternatives': [{'confidence': '1.0', 'content': 'big'}],
              'type': 'pronunciation'},
             {'start_time': '16.35', 'end_time': '16.53', 'alternatives': [{'confidence': '0.99', 'content': 'toy'}],
              'type': 'pronunciation'},
             {'start_time': '16.53', 'end_time': '16.85', 'alternatives': [{'confidence': '0.8798', 'content': 'folk'}],
              'type': 'pronunciation'},
             {'start_time': '16.85', 'end_time': '17.02', 'alternatives': [{'confidence': '1.0', 'content': 'for'}],
              'type': 'pronunciation'},
             {'start_time': '17.02', 'end_time': '17.11', 'alternatives': [{'confidence': '1.0', 'content': 'the'}],
              'type': 'pronunciation'},
             {'start_time': '17.11', 'end_time': '17.6', 'alternatives': [{'confidence': '0.9965', 'content': 'kids'}],
              'type': 'pronunciation'},
             {'alternatives': [{'confidence': '0.0', 'content': '.'}], 'type': 'punctuation'},
             {'start_time': '18.59', 'end_time': '18.79', 'alternatives': [{'confidence': '1.0', 'content': 'She'}],
              'type': 'pronunciation'},
             {'start_time': '18.79', 'end_time': '18.98', 'alternatives': [{'confidence': '0.9982', 'content': 'can'}],
              'type': 'pronunciation'}, {'start_time': '18.98', 'end_time': '19.35',
                                         'alternatives': [{'confidence': '0.6397', 'content': 'school'}],
                                         'type': 'pronunciation'},
             {'start_time': '19.36', 'end_time': '19.58', 'alternatives': [{'confidence': '1.0', 'content': 'these'}],
              'type': 'pronunciation'},
             {'start_time': '19.58', 'end_time': '19.87', 'alternatives': [{'confidence': '1.0', 'content': 'things'}],
              'type': 'pronunciation'},
             {'start_time': '19.88', 'end_time': '20.01', 'alternatives': [{'confidence': '1.0', 'content': 'in'}],
              'type': 'pronunciation'},
             {'start_time': '20.01', 'end_time': '20.42', 'alternatives': [{'confidence': '1.0', 'content': 'tow'}],
              'type': 'pronunciation'},
             {'start_time': '20.43', 'end_time': '20.75', 'alternatives': [{'confidence': '1.0', 'content': 'three'}],
              'type': 'pronunciation'},
             {'start_time': '20.75', 'end_time': '20.95', 'alternatives': [{'confidence': '0.8351', 'content': 'red'}],
              'type': 'pronunciation'},
             {'start_time': '20.95', 'end_time': '21.45', 'alternatives': [{'confidence': '0.8097', 'content': 'bags'}],
              'type': 'pronunciation'},
             {'start_time': '22.01', 'end_time': '22.22', 'alternatives': [{'confidence': '1.0', 'content': 'and'}],
              'type': 'pronunciation'},
             {'start_time': '22.22', 'end_time': '22.33', 'alternatives': [{'confidence': '1.0', 'content': 'we'}],
              'type': 'pronunciation'},
             {'start_time': '22.33', 'end_time': '22.46', 'alternatives': [{'confidence': '1.0', 'content': 'will'}],
              'type': 'pronunciation'},
             {'start_time': '22.46', 'end_time': '22.75', 'alternatives': [{'confidence': '1.0', 'content': 'go'}],
              'type': 'pronunciation'}, {'start_time': '22.75', 'end_time': '23.25',
                                         'alternatives': [{'confidence': '0.9202', 'content': 'meter'}],
                                         'type': 'pronunciation'}, {'start_time': '23.8', 'end_time': '24.37',
                                                                    'alternatives': [{'confidence': '0.9964',
                                                                                      'content': 'Wednesday'}],
                                                                    'type': 'pronunciation'},
             {'start_time': '24.48', 'end_time': '24.67', 'alternatives': [{'confidence': '1.0', 'content': 'at'}],
              'type': 'pronunciation'},
             {'start_time': '24.67', 'end_time': '24.86', 'alternatives': [{'confidence': '1.0', 'content': 'the'}],
              'type': 'pronunciation'},
             {'start_time': '25.13', 'end_time': '25.35', 'alternatives': [{'confidence': '1.0', 'content': 'train'}],
              'type': 'pronunciation'}, {'start_time': '25.35', 'end_time': '25.75',
                                         'alternatives': [{'confidence': '0.9999', 'content': 'station'}],
                                         'type': 'pronunciation'},
             {'alternatives': [{'confidence': '0.0', 'content': '.'}], 'type': 'punctuation'}]
    words = json
    ssml = ''

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
            ssml += '<break time="{}s" />'.format(pause)

            const = 0.28
            duration = end_time - start_time
            speed = 100 * duration / const

            content = words[i]['alternatives'][0]['content']
            ssml += '<prosody rate="{}%">{}</prosody>'.format(speed, content)

    ssml = '<speak>{}</speak>'.format(ssml)
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

    file = open('speech6.mp3', 'wb')
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
    # return result


if __name__ == "__main__":
    session = boto3.Session(
        aws_access_key_id=CONFIG['aws_access_key_id'],
        aws_secret_access_key=CONFIG['aws_secret_access_key'],
        region_name=CONFIG['region_name']
    )

    s3 = session.resource('s3')

    # ssml = json2ssml('')
    # text2speech(ssml)

    # text = '<speak>police call, Stella <break time="5s"/>asked her to bring these things from her with her from the store, six spoons of fresh snow peas, five thick slabs of blue cheese and maybe a snack for her brother Bob. We also need a small plastic snake in a big toy frog for the kids. She can scoop these things into three red bags. We will go meet her Wednesday at the train station.</speak>'

    # text2speech(text)

    parser = argparse.ArgumentParser(description='Write path to file')
    parser.add_argument('filename', type=str)
    filename = vars(parser.parse_args())['filename']
    remove_accent(filename)
