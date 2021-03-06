import sys, time, json, base64, requests, argparse, os
import subprocess as sp

WSK_CLI = '/home/ubuntu/incubator-openwhisk/bin/wsk'
WSK_PROPS = '/home/ubuntu/.wskprops'

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
    elif args.service == 'ow':
        ow(args)
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

ow_record = json.loads('''
{
  "s3": {
    "bucket": {
      "name": "lambda-resize-image-ow"
    },
    "object": {
      "key": "texture.tiff"
    }
  }
}
''')

def upload_ow_webaction(num):
    with open(os.devnull, 'w') as dnull:
        action = 'ow-resize%d' % num
        sp.call("%s action delete %s --insecure" % (WSK_CLI, action), shell=True, stdout=dnull, stderr=dnull)
        sp.call("%s action create %s --kind python:2 --insecure --web true ow-resize/ow-resize.zip" % (WSK_CLI, action), shell=True,  stdout=dnull, stderr=dnull)
        webaction_result_b = sp.check_output("%s api create /root /%s post %s --response-type json --insecure" % (WSK_CLI, action, action), stderr=sp.STDOUT, shell=True)
        second_half =  str(webaction_result_b).split("api")[1]
        endpoint = 'http://%s@%s:9001/api%s' % (AUTH, APIHOST, second_half)
        return endpoint.strip()

def ow(args):
    global AUTH
    global APIHOST
    with open(WSK_PROPS, 'r') as f:
        lines = f.readlines()
        for l in lines:
            ls = l.split('=')
            if ls[0] == 'AUTH':
                AUTH = ls[1].strip()
            if ls[0] == 'APIHOST':
                APIHOST = ls[1].strip()

    payload = json.dumps({'Records': [ow_record for _ in range(args.num_images)]})
    
    if not args.cold:
        ow_endpoint = upload_ow_webaction(0)

    for i in xrange(args.num_requests):
        if args.cold:
            ow_endpoint = upload_ow_webaction(i)
        start = time.time()
        r = requests.post(ow_endpoint, data={'payload': "".join(payload.split())})
        elapsed = (time.time() - start) * 1000
        print('%.3f %.3f %.3f %.3f' % (elapsed, r.json()['download'], r.json()['compute'], r.json()['upload']))
        time.sleep(1)

if __name__ == '__main__':
    main(parser.parse_args())
