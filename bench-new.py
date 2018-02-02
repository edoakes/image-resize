import sys, time, json, base64, requests, argparse

parser = argparse.ArgumentParser(description='Image processing benchmark.')
parser.add_argument('--num-images', default=1, type=int, help='Number of copies of integer to resize.')
parser.add_argument('--num-requests', default=1, type=int, help='Number of times to send request.')
parser.add_argument('--ol-address', default='localhost', type=str, help='IP address of OpenLambda worker.')
parser.add_argument('service', type=str, help='{aws,ol,ow}')
parser.add_argument('--cold', required=False, action='store_true')

def main(args):
    if args.service == 'aws':
        aws(args)
    elif args.service == 'ol':
        ol(args)
    else:
        print('invalid service: %s' % args.service)
        sys.exit(1)

aws_record = json.loads('''
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

def aws(args):
    payload = json.dumps({'Records': [aws_record for _ in range(args.num_images)]})

    import boto3
    client = boto3.client('lambda')
    if not args.cold:
        with open('resize.zip', 'rb') as f:
            client.update_function_code(FunctionName='resize',
                    ZipFile=f.read())
        client.invoke(FunctionName='resize',
                Payload=payload)
    for i in xrange(args.num_requests):
        if args.cold:
            with open('resize.zip', 'rb') as f:
                client.update_function_code(FunctionName='resize',
                        ZipFile=f.read())
        start = time.time()
        response = client.invoke(
            FunctionName='resize',
            Payload=payload
        )
        elapsed = (time.time() - start) * 1000
        output = json.loads(response['Payload'].read())
        print('%.3f %.3f %.3f %.3f' % (elapsed, output['download'], output['compute'], output['upload']))
        time.sleep(1)

ol_record = json.loads('''
{
  "s3": {
    "bucket": {
      "name": "lambda-resize-image-west"
    },
    "object": {
      "key": "texture.tiff"
    }
  }
}
''')

def ol(args):
    payload = json.dumps({'Records': [ol_record for _ in range(args.num_images)]})

    for i in xrange(args.num_requests):
        start = time.time()
        r = requests.post('http://{ip}:8080/runLambda/ol-resize'.format(ip=args.ol_address), data=payload)
        elapsed = (time.time() - start) * 1000
        print('%.3f %.3f %.3f %.3f' % (elapsed, r.json()['download'], r.json()['compute'], r.json()['upload']))
        time.sleep(1)

if __name__ == '__main__':
    main(parser.parse_args())
