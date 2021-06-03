from flask import Flask, render_template, redirect, url_for
import os, json, glob
from collections import deque
from pool_spotter import PoolSpotter

app = Flask('app', static_url_path='/static')

@app.route('/')
def home():
  return imgdata()

@app.route('/imgdata/')
def imgdata():
  data = []
  for pth in glob.glob(os.path.join(app.root_path, "static/pools/images/*.json")):
    filename = pth.split('/')[-1] # -> 123.json
    name = filename.split('.')[0] # -> 123
    with app.open_resource('static/pools/images/{}'.format(filename)) as fin:
      obj = json.load(fin)
      obj['image_path'] = '/static/pools/images/{}.jpg'.format(name)
      obj['json_path'] = '/static/pools/images/{}.json'.format(name)
      data.append(obj)
  return json.dumps(data)

# {} Path -> IO
def record_as_json(obj, relpath):
   with open(os.path.join(app.root_path, relpath), 'w') as fout:
    return json.dump(obj, fout)

@app.route('/edit/')
def edit():
    return render_template('pool_edit.html')


app.run(host='0.0.0.0', port=8080)