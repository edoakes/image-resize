import time, uuid, sys, os, json
sys.path.insert(0, './lib')
os.system('cp ./lib/libjpeg.so.8 /usr/lib')
from PIL import Image
import boto3

ACCESS_KEY = ''
SECRET_KEY = ''
REGION = 'us-west-1'
     
def resize_image(image_path, resized_path):
    with Image.open(image_path) as image:
        image.thumbnail(tuple(x / 2 for x in image.size))
        image.save(resized_path)
     
def main(args):
    start = time.time()
    s3_client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )

    queue = []

    # download
    start = time.time()
    payload = args.get('payload', None)
    payload = json.loads(payload)
    for record in payload['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        upload_path = '/tmp/resized-{}'.format(key)
        s3_client.download_file(bucket, key, download_path)
        queue.append((download_path, upload_path, '{}-resized'.format(bucket), key))
    download_t = time.time()-start

    # compute
    start = time.time()
    for download_path, upload_path, _, _ in queue:
        resize_image(download_path, upload_path)
    compute_t = time.time()-start

    # upload
    start = time.time()
    for _, upload_path, upload_bucket, upload_key in queue:
        print upload_bucket
        s3_client.upload_file(upload_path, upload_bucket, upload_key)
    upload_t = time.time()-start

    return {'download': download_t*1000, 'compute': compute_t*1000, 'upload': upload_t*1000}
