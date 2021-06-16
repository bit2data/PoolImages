import requests
import json


# -> {}
def test_data():
  resp = requests.get('http://localhost:5000/data/')
  return resp.json()


# -> [{x y w h}]
def test_detect_direct():
  from PIL import Image
  from main import detect_on_img

  pth = 'static/pools/images/test/0.jpg'
  img = Image.open(pth)
  pred = detect_on_img(img)
  for xywh in pred['rects']:
      assert isinstance(xywh['x'], int)
      assert isinstance(xywh['y'], int)
      assert isinstance(xywh['w'], int)
      assert isinstance(xywh['h'], int)

  return pred


def test_detect():
    import base64
    
    pth = 'static/pools/images/test/0.jpg'
    with open(pth, 'rb') as fin:
        img_str = base64.b64encode(fin.read()).decode('utf-8')
        #print(img_str)
    payload = {
        'imgData': 'data:image/jpeg;base64,{}'.format(img_str)
    }
    resp = requests.post('http://localhost:5000/detect/', json=payload) # json=payload takes care of headers automatically

    return resp.json(), payload


def test_new(rects, payload):
  payload['rects'] = rects
  resp = requests.get('http://localhost:5000/new/', json=payload)
  return resp.json()




if __name__ == '__main__':
    print('test_data() =>', test_data()[:1])
    #pred = test_detect_direct()
    #print('test_detect_direct() =>', pred)
    pred, payload = test_detect()
    print('test_detect()', pred)
    print('test_new() =>', test_new(pred['rects'], payload))