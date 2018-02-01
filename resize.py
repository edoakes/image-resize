from __future__ import print_function
import base64
from cStringIO import StringIO
import time
import sys
sys.path.insert(0,'./lib')
import boto3
from PIL import Image
     
s3_client = boto3.client('s3')
     
def resize_image(record):
    decoded = base64.b64decode(record['data'])
    stream = StringIO(decoded)
    with Image.open(stream) as image:
        image.thumbnail(tuple(x / 2 for x in image.size))
        output = StringIO()
        image.save(output, format=record['format'])
        return base64.b64encode(output.getvalue())
     
def handler(event, context):
    start = time.time()
    output = {'resized': []}
    for record in event['Records']:
        output['resized'].append(resize_image(record))
    output['duration'] = (time.time() - start) * 1000
    return output
