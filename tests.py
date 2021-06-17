import requests
import json


# -> [{}]
def test_data():
  resp = requests.get('http://localhost:5000/data/')
  return resp.json()


# {json_path: } -> {json_path: }
def test_save(payload):
  resp = requests.post('http://localhost:5000/save/', json=payload)
  assert payload == resp.json()
  return payload, resp.json() 


# -> {rects:[{x:Int y:Int w:Int h:Int}] scores:[Int]}
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


# -> {} {} 
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


# -> {}
def test_new(rects, payload):
  payload['rects'] = rects
  resp = requests.get('http://localhost:5000/new/', json=payload)
  data = resp.json()
  assert rects == data['rects']
  return data




if __name__ == '__main__':
    data = test_data()
    print('test_data() =>', data[0])
    print('test_save()', test_save(data[0])) 
    #pred = test_detect_direct()
    #print('test_detect_direct() =>', pred)
    pred, payload = test_detect()
    print('test_detect()', pred)
    print('test_new() =>', test_new(pred['rects'], payload))