#-*- coding:utf-8 -*-
import pandas as pd
from flask import Flask, request, jsonify
import os
import cv2
import numpy as np
import base64
import json
from flask_cors import CORS

#한국말 깨짐 방지
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')



app = Flask(__name__)
#cors 허용
CORS(app, resources={r'*': {'origins': '*'}})

@app.route('/save_image', methods=['POST', 'GET'])
def save_image():

    data = request.get_json()
    img = data['image']
    name = data['name']

    img = base64.b64decode(img)
    #만약 data.csv가 없다면 생성
    if not os.path.isfile('data.csv'):
        with open('data.csv', 'w') as f:
            f.write('index,name,path')
    #data.csv 읽기
    with open('data.csv', 'r',encoding='UTF8') as f:
        data = f.read()
        data = data.split('\n')
        data = data[1:]
        data = [i.split(',') for i in data]
        data = [i for i in data if len(i) == 2]

    data = pd.read_csv('data.csv')
    file_name = len(data)
    #file_name to string
    file_name = str(file_name)
    path = 'data/'+file_name + '.jpg'
    #데이터프레임에 index, name, path 값 추가
    data = data.append({'index': len(data), 'name': name, 'path': path}, ignore_index=True)
    #data to csv
    data.to_csv('data.csv', index=False)

    img = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(img, 1)
    #파일명을 file_name.jpg로 저장
    cv2.imwrite(path, img)
    return jsonify({'result': 'success'})

#비교용 사진을 위한 저장 api
@app.route('/save_image_detect', methods=['POST', 'GET'])
def save_image_detect():
    #만약 compare.jpg가 있다면 삭제
    if os.path.isfile('compare.jpg'):
        os.remove('compare.jpg')

    data = request.get_json()
    img = data['image']

    img = base64.b64decode(img)
    #print(img)
    img = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(img, 1)
    #파일명을 file_name.jpg로 저장
    cv2.imwrite("compare.jpg", img)
    return jsonify({'result': 'success'})


@app.route('/home', methods=['GET'])
def home():
    return "hello world"

@app.route('/load_compare_image', methods=['GET', 'POST'])
def load_compare_image():
    data = request.get_json()
    img_2 = data['image']
    print(img_2)
    with open('compare.jpg', 'rb') as img:
        base64_string = base64.b64encode(img.read())
    base64_string = base64_string.decode('utf-8')
    print(base64_string)
    return jsonify({'image': base64_string})

@app.route('/detect_face', methods=['GET', 'POST'])
def detect_face():
    #image를 받아서 저장
    receive_data = request.get_json()
    receive_type = receive_data['data_type']

    #data 폴더에 저장된 사진들을 base64로 인코딩
    data = pd.read_csv('data.csv')

    #dataframe 생성
    df_new = pd.DataFrame(columns=['name', 'path', 'image'])

    #data의 길이 만큼 반복
    for i in range(len(data)):
        #만약 data['name']이 비어있다면 data['name'] = 'unknown'
        if data['name'][i] == '' or None:
            data['name'][i] = 'unknown'

        #dataframe data에서 path 값을 하나씩 가져오기
        path = data['path'][i]
        #path에 있는 이미지를 읽어서 base64로 인코딩
        with open(path, 'rb') as img:
            base64_string = base64.b64encode(img.read())
        #df_new에 name, path, image를 추가
        df_new = df_new.append({'name': data['name'][i], 'path': data['path'][i], 'image': base64_string}, ignore_index=True)

    #df_new를 csv로 저장
    #df_new.to_csv('data_base64.csv', index=False)
    #df_new의 name과 image만 추출
    df_new = df_new[['name', 'image']]
    if receive_type == 'name':
        df_new = df_new[['name']]
        #df_new를 list로 변환
        df_new = df_new.values.tolist()


        return jsonify({'data': df_new})
    else:
        df_new = df_new[['image']]

        df_new = df_new.values.tolist()
        #df_new의 value decode
        df_new = [i[0].decode('utf-8') for i in df_new]

        #df_new[0]을 txt로 저장
        with open('data.txt', 'w') as f:
            f.write(df_new[0])


        return jsonify({'data': df_new})




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15027, debug=True)
