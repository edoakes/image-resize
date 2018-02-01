import boto3

client = boto3.client('lambda')

with open('resize.zip', 'rb') as f:
    print client.update_function_code(FunctionName='resize',
            ZipFile=f.read(),
            )
