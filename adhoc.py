import os, json, glob
from PIL import Image
from collections import defaultdict

def find_small(src):
  where = './static/pools/images/{}/*.jpg'.format(src)
  #where = '/mnt/chromeos/GoogleDrive/MyDrive/TensorFlow/workspace/pool-data/images/{}/*.jpg'.format(src)
  small = defaultdict(list)
  for pth in glob.glob(where):
    #print(pth)
    img = Image.open(pth)
    width, height = img.size
    if width < 400:
      small[str(width)].append(pth)
  return small

def run_find_small():
  for src in ['test', 'train']:
    print(find_small(src)['300'])
  return 'done'
  
# [dir] Bool -> Int
def correct_img_size(src, for_real=False):
  where = './static/pools/images/{}/*.jpg'.format(src)
  #print(where)
  count = 0
  for pth in glob.glob(where):
    #print(pth)
    img = Image.open(pth)
    width, height = img.size
    need_to_correct = True
    json_path = pth.replace('jpg', 'json')
    with open(json_path, 'r+') as f:
      data = json.load(f)
      if width == data['w'] and height == data['h']:
        need_to_correct = False
      else:
        print('need to correct', data)
      if for_real and need_to_correct:
        data['w'] = width
        data['h'] = height
        f.seek(0)
        json.dump(data, f)
        count += 1
  return count 

def run_correct_img_size():
  for x in ['test', 'train']:
    print(correct_img_size(x, for_real=True), 'files corrected')