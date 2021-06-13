from flask import Flask, render_template, redirect, url_for, request, send_file, abort, Response
import os, json, glob, io, base64
from collections import deque
import requests as req

app = Flask('app', static_url_path='/static')


@app.route('/')
def home():
  #return imgdata()
  return preview()


# present BIG Google map such that
# user can choose Area of Interest
# upon clicking such Area
# direct to /preview/
@app.route('/hunt/')
def hunt():
  from security import pub_map_api_key
  return render_template('hunt.html', key = pub_map_api_key)


# from /hunt/ user gets here
# user can try out Prediction and/or
# save to be used as a new data point
@app.route('/preview/', methods=['get', 'post'])
def preview():
  d = {
    "lat": request.args.get("lat", '43.0'),
    "lng": request.args.get("lng", '-79.0'),
    "width": request.args.get("width", '400'),
    "height": request.args.get("height", '400'),
    "zoom": request.args.get("zoom", '18'),
  }
  src = '/staticmap?lat={lat}&lng={lng}&zoom={zoom}&width={width}&height={height}'.format(**d)
  return render_template('preview.html', src=src)

# from /preview/ user sends imgdata to be saved
@app.route('/new/', methods=['GET', 'POST'])
def new():
  payload = request.json
  imgData = payload['imgData']
  #imgData = request.values.get("imgData")
  print('image data size', len(imgData))
  #"data:image/png;base64,iVBORw0KGgo....""
  imgtype, data = imgData.split(',', 1)
  print('imgtype', imgtype) # data:image/png;base64
  print('size after split:', len(data))
  imgdata = base64.b64decode(data)

  import random 
  from datetime import datetime
  random.seed(datetime.now())
 
  alphas = list('ABCDEFGHJKLMNPQRSTVWXYZabcdefghijkmnpqrstvwxyz')
  rchars = ''.join(random.sample(alphas, 7))
  img_path = '/static/pools/images/new/{}.jpg'.format(rchars)
  json_path = '/static/pools/images/new/{}.json'.format(rchars)

  #changeme: fill with actual predictions 
  data = {
    "rect_count": 2, 
    "rects": [
      {"x": 76, "y": 142, "w": 22, "h": 22}, 
      {"x": 171, "y": 270, "w": 25, "h": 17}
    ], 
    "w": 400, 
    "h": 400, 
    "image_path": img_path, 
    "json_path": json_path
  }

  record_as_json(data, '.'+json_path)

  with open('.'+img_path, "wb") as fout:
    fout.write(imgdata)
  
  return "/static/pools/pool_edit.html?p=new/{}.json".format(rchars)

# serve Image Data
# e.g. Input: /staticmap?lat=43.35975&lng=-79.77&zoom=18&width=400&height=400
@app.route('/staticmap')
def staticmap():
  r = fetch_static_map_r()  
  def generate():
    for chunk in r.iter_content(1024):
      yield chunk
  return Response(generate(), headers = dict(r.headers))


def fetch_static_map_r():
  from security import map_api_key
  d = {
    "lat": request.args.get("lat", '43.0'),
    "lng": request.args.get("lng", '-79.0'),
    "width": request.args.get("width", '400'),
    "height": request.args.get("height", '400'),
    "zoom": request.args.get("zoom", '18'),
    "key": map_api_key
  }
  url = "https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom={zoom}&size={width}x{height}&maptype=satellite&key={key}".format(**d)

  return get_source_rsp(url)

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

# -> [{}]
# serve from 3 directories where the images and corresponding .json files reside
@app.route('/imgdata/')
def imgdata():
  data = []
  srcs = ['new', 'test', 'train']
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


#changeme: need to run Pytorch model here but 
#repl.it limits disk space
@app.route('/detect/', methods=['get', 'post'])
def detect():
  from PIL import Image
  from poolspotter import PoolSpotter

  spotter = PoolSpotter()
  
  payload = request.json
  imgData = payload['imgData']
  print('image data size', len(imgData))
  #"data:image/png;base64,iVBORw0KGgo....""
  imgtype, data = imgData.split(',', 1)
  print('imgtype', imgtype) # data:image/png;base64
  print('size after split:', len(data))
  img = Image.open(io.BytesIO( base64.b64decode(data)))

  pred = spotter.predict_pools_on_img(img)
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




if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)