from flask import Flask, render_template, redirect, url_for, request, send_file, abort, Response
import os, json, glob, io, base64
from collections import deque
import requests as req

app = Flask('app', static_url_path='/static')

@app.route('/')
def home():
  return imgdata()


# from /staticmap?lat=43.35975&lng=-79.77&zoom=18&width=400&height=400
@app.route('/staticmap')
def staticmap():
  from security import map_api_key
  CHUNK_SIZE = 1024
  d = {
    "lat": request.args.get("lat", '43.0'),
    "lng": request.args.get("lng", '-79.0'),
    "width": request.args.get("width", '400'),
    "height": request.args.get("height", '400'),
    "zoom": request.args.get("zoom", '18A'),
    "key": map_api_key
  }
  url = "https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom={zoom}&size={width}x{height}&maptype=satellite&key={key}".format(**d)

  r = get_source_rsp(url)
  headers = dict(r.headers)

  def generate():
    for chunk in r.iter_content(CHUNK_SIZE):
      yield chunk
      
  return Response(generate(), headers = headers)


def get_source_rsp(url):
    # Pass original Referer for subsequent resource requests
    proxy_ref = proxy_ref_info(request)
    headers = { "Referer" : "http://%s/%s" % (proxy_ref[0], proxy_ref[1])} if proxy_ref else {}
    # Fetch the URL, and stream it back
    return req.get(url, stream=True , params = request.args, headers=headers)


#URL => (protocol, host, uri)
def split_url(url):
  proto, rest = url.split(':', 1)
  rest = rest[2:].split('/', 1)
  host, uri = (rest[0], rest[1]) if len(rest) == 2 else (rest[0], "")
  return (proto, host, uri)

# Request -> (String, String)
def proxy_ref_info(request):
  """Parses out Referer info indicating the request    is from a previously proxied page.
     For example, 
      if:
        Referer: http://localhost:8080/p/google.com/search?q=foo
      then the result is:
       ("google.com", "search?q=foo")
  """
  ref = request.headers.get('referer')
  if ref:
    _, _, uri = split_url(ref)
    if uri.find("/") < 0:
      return None
    first, rest = uri.split("/", 1)
    if first in "pd":
      parts = rest.split("/", 1)
      r = (parts[0], parts[1]) if len(parts) == 2 else (parts[0], "")
      LOG.info("Referred by proxy host, uri: %s, %s", r[0], r[1])
      return r
  return None


@app.route('/imgdata/')
def imgdata():
  data = []
  srcs = ['test', 'train']
  for src in srcs:
    basedir = 'static/pools/images/{}'.format(src)
    print(basedir)
    for pth in glob.glob(os.path.join(app.root_path, basedir+'/*.json')):
      print(pth)
      filename = pth.split('/')[-1] # -> 123.json
      name = filename.split('.')[0] # -> 123
      with app.open_resource(pth) as fin:
        obj = json.load(fin)
        obj['image_path'] = '/static/pools/images/{}/{}.jpg'.format(src, name)
        obj['json_path'] = '/static/pools/images/{}/{}.json'.format(src, name)
        data.append(obj)
  return json.dumps(data)

#@app.route('/predictions/')
#def prediction():
#  img_path = request.args.get('img_path')
#  print(img_path)
#  json_path = img_path.replace('images', 'predictions').replace('jpg', 'json')
#  with app.open_resource(json_path) as fin:
#    pred = json.load(fin)
#  return json.dumps(pred)

#changeme: need to run Pytorch model here but 
#repl.it limits disk space
@app.route('/detect/')
def detect():
  pred = [
    {'x':100, 'y':100, 'w':20, 'h':20}
  ]
  return json.dumps(pred)

@app.route('/save/', methods = ['POST'])
def save_page():
  content = request.json
  print(content)
  print(content['json_path'])
  where = record_as_json(content, '.'+content['json_path'])
  with app.open_resource(where) as fin:
    page = json.load(fin)
  return json.dumps(page)

# {} Path -> IO -> Path
def record_as_json(obj, relpath):
  where = os.path.join(app.root_path, relpath)
  with open(where, 'w') as fout:
    json.dump(obj, fout)
  return where

@app.route('/edit/')
def edit():
    return render_template('pool_edit.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)