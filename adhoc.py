import os, json, glob
from PIL import Image

def fix_width_height(src):
  where = './static/pools/images/{}/*.json'.format(src)
  for pth in glob.glob(where):
    print(pth)
    with open(pth, 'r+') as f:
      content = json.load(f)
      img_path = pth.replace('json', 'jpg')
      img = Image.open(img_path)
      width, height = img.size
      content['w'] = width
      content['h'] = height
      f.seek(0)
      json.dump(content, f)


for src in ['test', 'train']:
  fix_width_height(src)