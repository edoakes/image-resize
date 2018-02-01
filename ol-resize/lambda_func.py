import time, base64
from PIL import Image
from cStringIO import StringIO
     
def resize_image(record):
    decoded = base64.b64decode(record['data'])
    stream = StringIO(decoded)
    with Image.open(stream) as image:
        image.thumbnail(tuple(x / 2 for x in image.size))
        output = StringIO()
        image.save(output, format=record['format'])
        return base64.b64encode(output.getvalue())
     
def handler(conn, event):
    start = time.time()
    output = {'resized': []}
    for record in event['Records']:
        output['resized'].append(resize_image(record))
    output['duration'] = (time.time() - start) * 1000
    return output
