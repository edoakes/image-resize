import subprocess as sp

WSK_CLI = '~/incubator-openwhisk/bin/wsk'
WSK_PROPS = '/users/khouck/.wskprops'
with open(WSK_PROPS, 'r') as f:
  lines = f.readlines()
  for l in lines:
    ls = l.split('=')
    if ls[0] == 'AUTH':
      AUTH = ls[1].strip()
    if ls[0] == 'APIHOST':
      APIHOST = ls[1].strip()

def upload_webaction():
  action = 'ow-resize'
  sp.call("%s action delete ow-resize --insecure" % WSK_CLI, shell=True)
  sp.call("%s action create ow-resize --kind python:2 --insecure --web true ow-resize/ow-resize.zip" % WSK_CLI, shell=True)
  webaction_result_b = sp.check_output("%s api create /root /ow-resize post ow-resize --response-type json --insecure" % WSK_CLI, stderr=sp.STDOUT, shell=True)
  second_half =  str(webaction_result_b).split("api")[1]
  endpoint = 'http://%s@%s:9001/api%s' % (AUTH, APIHOST, second_half)
  print endpoint.replace("\\n'", '')

upload_webaction()
