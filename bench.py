import sys, time, json, base64, requests, argparse

parser = argparse.ArgumentParser(description='Image processing benchmark.')
parser.add_argument('--num-images', default=1, type=int, help='Number of copies of integer to resize.')
parser.add_argument('--num-requests', default=1, type=int, help='Number of times to send request.')
parser.add_argument('service', type=str, help='{aws,ol,ow}')

if len(sys.argv) != 3 or sys.argv[1] not in ('resize', 'baseline', 'dryrun'):
    print('usage: python bench.py <resize|baseline|dryrun> <count>')
    sys.exit(1)

count = int(sys.argv[2])

if sys.argv[1] == 'resize':
    with open('texture.tiff', 'rb') as img:
        data = base64.b64encode(img.read())
        payload = json.dumps({'Records':[{'data':data, 'format':'tiff'}]})

    print('latency lambda_duration')
    for i in xrange(count):
        start = time.time()
        response = client.invoke(
                FunctionName='resize',
                Payload=payload
                )
        elapsed = (time.time() - start) * 1000
        output = json.loads(response['Payload'].read())
        print('%.3f %.3f' % (elapsed, output['duration']))

elif sys.argv[1] == 'baseline':
    print('latency')
    for i in xrange(count):
        start = time.time()
        response = client.invoke(
                FunctionName='lambda_bench'
                )
        elapsed = (time.time() - start) * 1000
        print('%.3f' % elapsed)

else:
    print('latency')
    for i in xrange(count):
        start = time.time()
        response = client.invoke(
                FunctionName='lambda_bench',
                InvocationType='DryRun'
                )
        elapsed = (time.time() - start) * 1000
        print('%.3f' % elapsed)
