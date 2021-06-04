import os, json, glob

def fix_width_height(src):
  where = './static/pools/images/{}/*.json'.format(src)
  for pth in glob.glob(where):
    print(pth)
    with open(pth, 'r+') as f:
      content = json.load(f)
      content['w'] = 300
      content['h'] = 300
      f.seek(0)
      json.dump(content, f)


#for src in ['test', 'train']:
#  fix_width_height(src)