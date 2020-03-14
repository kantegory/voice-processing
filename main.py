from __future__ import print_function
import time
import boto3

s3 = boto3.resource('s3')


def speech2text():
    transcribe = boto3.client('transcribe')
    job_name = "job name"
    job_uri = "https://S3 endpoint/test-transcribe/answer2.wav"

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='wav',
        LanguageCode='en-US'
    )

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)

    print(status)


def file2bucket(filename, bucket):
    # Upload a new file
    data = open(filename, 'rb')
    s3.Bucket(bucket).put_object(Key=filename, Body=data)
