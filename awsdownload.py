import boto3

BUCKET_NAME = 'lipchat-word-embeddings' # replace with your bucket name
KEY = 'UEXescIMZh79tyCAMFUwr6tvH59VTrJkQvgpNrnR' # replace with your object key
ID = 'AKIAJLHO7L2GJ3R4GLPQ'

session = boto3.Session(region_name = 'eu-central-1', aws_access_key_id=ID, aws_secret_access_key=KEY)

print(session)

myclient = session.resource('s3')
myclient.Bucket(BUCKET_NAME).download_file('GoogleNews-vectors-negative300.bin', 'GoogleNews-vectors-negative300.bin')
