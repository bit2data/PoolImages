from flask import Flask, render_template, redirect, url_for, request
import os, json, glob
from collections import deque

app = Flask('app', static_url_path='/static')

@app.route('/')
def home():
  return imgdata()

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