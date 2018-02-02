import time, uuid
from PIL import Image
import boto3

ACCESS_KEY = 'FOOBAR'
SECRET_KEY = 'FOOBAR'
     
def resize_image(image_path, resized_path):
    with Image.open(image_path) as image:
        image.thumbnail(tuple(x / 2 for x in image.size))
        image.save(resized_path)
     
def handler(conn, event):
    start = time.time()
    s3_client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )

    queue = []

    # download
    start = time.time()
    for record in event['Records']:
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
        s3_client.upload_file(upload_path, upload_bucket, upload_key)
    upload_t = time.time()-start

    return {'download': download_t*1000, 'compute': compute_t*1000, 'upload': upload_t*1000}
