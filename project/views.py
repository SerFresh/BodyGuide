from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadFrom
from inference_sdk import InferenceHTTPClient
import os
import random
import pandas as pd

def index(request):
    return render(request, 'index.html')

def delete_old_file(dir, file_extension):
    # วนลูปค้นหาไฟล์ใน directory ที่มีนามสกุลตามที่ระบุ เช่น .jpg หรือ .png
    for filename in os.listdir(dir):
        if filename.endswith(file_extension):
            file_path = os.path.join(dir, filename)
            try:
                os.remove(file_path)  # ลบไฟล์
                #print(f"Deleted: {file_path}")
            #except Exception as e:
                #print(f"Error deleting file {file_path}: {e}")

def upload_basic(request):
    if request.method == 'POST':
        form = UploadFrom(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            save_file('media/upload/', file)

            # ตรวจสอบว่าผู้ใช้เลือกรูปร่างแล้วหรือยัง
            user_shape = request.POST.get('shape')  # รับรูปร่างจากฟอร์ม

            # ทำการทำนายภาพ
            if user_shape:
                shape_suitability = predict_image('media/upload/', file, user_shape)
            else:
                shape_suitability = None
        else:
            file = None
            shape_suitability = None
    else:
        form = UploadFrom()
        file = None
        shape_suitability = None

    return render(request, 'upload-basic.html', {
        'form': form,
        'file': file,
        'shape_suitability': shape_suitability
    })

# ฟังก์ชันสำหรับการทำนายภาพ
def predict_image(dir, file, user_shape):
    picture_file = f'{dir}{file.name}'

    # Initialize the client
    CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key="WKJ8dPUdiWFISFezVm7W"
    )

    # ผลลัพธ์จาก classification โดยโมเดล
    result = CLIENT.infer(picture_file, model_id="getdress-egfii/1")

    # Extract predictions
    predictions = result['predictions']

    # เลือกการทำนายที่มีความมั่นใจสูงที่สุด
    highest_confidence_prediction = max(predictions, key=lambda x: x['confidence'])
    class_name = highest_confidence_prediction['class']
    confidence = highest_confidence_prediction['confidence']

    # แสดงผลลัพธ์การทำนาย
    #print(f"Class: {class_name}, Confidence: {confidence:.2f}")

    # ตรวจสอบว่าเสื้อผ้านี้เหมาะสมกับรูปร่างแบบไหน
    shape_list = []

    # โหลดไฟล์ CSV
    df = pd.read_csv('ClothesClassWithShape.csv')
    
    # ค้นหาชื่อคลาสที่ตรงกัน
    matching_rows = df[df['Class'] == class_name]

    # ดึงข้อมูลรูปร่างที่เหมาะสม
    for value in matching_rows['Shape']:
            shape_list = value.split(",")
        
    # ตรวจสอบว่ารูปร่างของผู้ใช้เหมาะสมกับเสื้อผ้าหรือไม่
    if user_shape in shape_list:
        return f"{class_name} is suitable for your shape" #{class_name} is suitable for your shape
    else:
        return f"{class_name} is NOT suitable for your shape" #{class_name} is NOT suitable for your shape

# ฟังก์ชันสำหรับบันทึกไฟล์
def save_file(dir, file):
    delete_old_file(dir, ".jpg")
    if not dir.endswith('/'):
        dir += '/'
        
    with open(f'{dir}{file.name}', 'wb+') as target:
        for chunk in file.chunks():
            target.write(chunk)
