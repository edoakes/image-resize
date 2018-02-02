import subprocess as sp

WSK_CLI = '/home/ubuntu/incubator-openwhisk/bin/wsk'
WSK_PROPS = '/home/ubuntu/.wskprops'
with open(WSK_PROPS, 'r') as f:
  lines = f.readlines()
  for l in lines:
    ls = l.split('=')
    if ls[0] == 'AUTH':
      AUTH = ls[1].strip()
    if ls[0] == 'APIHOST':
      APIHOST = ls[1].strip()

def upload_webaction(num):
  action = 'ow-resize%' % num
  sp.call("%s action delete %s --insecure" % (WSK_CLI, action), shell=True)
  sp.call("%s action create %s --kind python:2 --insecure --web true ow-resize/ow-resize.zip" % (WSK_CLI, action), shell=True)
  webaction_result_b = sp.check_output("%s api create /root /%s post %s --response-type json --insecure" % (WSK_CLI, action, action), stderr=sp.STDOUT, shell=True)
  second_half =  str(webaction_result_b).split("api")[1]
  endpoint = 'http://%s@%s:9001/api%s' % (AUTH, APIHOST, second_half)
  return endpoint.replace("\\n'", '')

upload_webaction(0)
