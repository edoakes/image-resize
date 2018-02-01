import sys, time, json, base64, requests, argparse

parser = argparse.ArgumentParser(description='Image processing benchmark.')
parser.add_argument('--num-images', default=1, type=int, help='Number of copies of integer to resize.')
parser.add_argument('--num-requests', default=1, type=int, help='Number of times to send request.')
parser.add_argument('service', type=str, help='{aws,ol,ow}')

record = json.loads('''
{
  "s3": {
    "bucket": {
      "name": "lambda-resize-image"
    },
    "object": {
      "key": "texture.tiff"
    }
  }
}
''')

def main(args):
    payload = json.dumps({'Records': [record for _ in range(args.num_images)]})

    if args.service == 'aws':
        aws(payload, args.num_requests)
    elif args.service == 'ol':
        ol(payload, args.num_requests)
    else:
        print('invalid service: %s' % args.service)
        sys.exit(1)

def aws(payload, n_requests):
    import boto3
    client = boto3.client('lambda')
    print('latency lambda_duration')
    for i in xrange(n_requests):
        start = time.time()
        response = client.invoke(
            FunctionName='resize',
            Payload=payload
        )
        elapsed = (time.time() - start) * 1000
        output = json.loads(response['Payload'].read())
        print('%.3f %.3f' % (elapsed, output['duration']))

def ol(payload, n_requests):
    print('latency lambda_duration')
    for i in xrange(n_requests):
        start = time.time()
        r = requests.post('http://localhost:8080/runLambda/ol-resize', data=payload)
        elapsed = (time.time() - start) * 1000
        print('%.3f %.3f' % (elapsed, r.json()['duration']))

if __name__ == '__main__':
    main(parser.parse_args())
