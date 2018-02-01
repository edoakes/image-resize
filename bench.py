import boto3
import base64
import time
import json
import sys

client = boto3.client('lambda')

with open('texture.tiff', 'rb') as img:
    data = base64.b64encode(img.read())
    payload = json.dumps({'Records':[{'data':data, 'format':'tiff'}]})

print('latency lambda_duration')
for i in xrange(int(sys.argv[1])):
    start = time.time()
    response = client.invoke(
            FunctionName='resize',
            Payload=payload
            )
    elapsed = (time.time() - start) * 1000
    output = json.loads(response['Payload'].read())
    print('%.3f %.3f' % (elapsed, output['duration']))
