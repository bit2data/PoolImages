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


for src in ['test', 'train']:
  print(find_small(src)['300'])

