import os
from django.shortcuts import render
from .forms import UploadFrom
import pandas as pd
from inference_sdk import InferenceHTTPClient #for roboflow connection
#from tensorflow.keras.models import load_model

###############
 #ส่วน url!!!
def index(request):
    return render(request, 'index.html')
def detail(request):
    return render(request, 'detail.html')
def members(request):
    return render(request, 'members.html')
###############
def delete_old_file(dir, file_extension):
    for filename in os.listdir(dir):
        if filename.endswith(file_extension):
            file_path = os.path.join(dir, filename)
            os.remove(file_path)

def generate_unique_filename(dir, filename):
    # ตรวจสอบชื่อไฟล์ที่ซ้ำกันและเปลี่ยนชื่อไฟล์ให้ไม่ซ้ำ
    basename, ext = os.path.splitext(filename)
    new_filename = f"{basename}{ext}"
    counter = 1
    while os.path.exists(os.path.join(dir, new_filename)):
        new_filename = f"{basename}({counter}){ext}"
        counter += 1
    return new_filename

def upload_basic(request):
    if request.method == 'POST':
        form = UploadFrom(request.POST, request.FILES)
        
        if form.is_valid():
            # ตรวจสอบว่ามีการอัปโหลดไฟล์ใหม่หรือไม่
            if 'file' in request.FILES:
                file = request.FILES['file']
                # เก็บไฟล์ในเซสชัน
                saved_filename = save_file('media/upload/', file)
                request.session['file_name'] = saved_filename  # เก็บชื่อไฟล์ที่อัปโหลดในเซสชัน

            else:
                # ใช้ไฟล์เดิมจากเซสชัน
                saved_filename = request.session.get('file_name')
                if saved_filename:
                    file = None  # ไม่ต้องรับไฟล์ใหม่ แต่ใช้ไฟล์เดิม

            # รับรูปร่างที่ผู้ใช้เลือก
            user_shape = request.POST.get('shape')

            # ทำการทำนายรูปภาพ
            if saved_filename and user_shape:
                shape, shape_suitability, confidence = predict_image('media/upload/', saved_filename, user_shape)
                confidence = round(confidence * 100, 2)
            else:
                shape_suitability = None
                confidence = None
                shape = None
        else:
            form = UploadFrom()
            file = None
            shape_suitability = None
            saved_filename = None
            confidence = None
            shape = None
    else:
        form = UploadFrom()
        file = None
        shape_suitability = None
        saved_filename = None
        confidence = None
        shape = None
   
    return render(request, 'upload-basic.html', {
        'form': form,
        'file': saved_filename,  # แสดงชื่อไฟล์ที่อัปโหลด
        'shape_suitability': shape_suitability,
        'shape': shape,
        'confidence': confidence
    })
custom_objects = {
    # 'CustomLayer': CustomLayerClass,
    # 'CustomActivation': custom_activation_function
}
# Prediction function

def predict_image(dir, filename, user_shape):
    picture_file = os.path.join(dir, filename)

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

    # โหลดไฟล์ CSV
    df = pd.read_csv('ClassWithShape.csv')
    
    # ค้นหาชื่อคลาสที่ตรงกัน
    matching_rows = df[df['Class'] == class_name]

    # ดึงข้อมูลรูปร่างที่เหมาะสม
    shape_list = []
    for value in matching_rows['Shape']:
        shape_list = value.split(",")
        
    if user_shape in shape_list:
        return user_shape, f"Predicted Class: {class_name} is suitable for your shape.", confidence
    else:
        return user_shape, f"Predicted Class: {class_name} is NOT suitable for your shape.", confidence

# ฟังก์ชันสำหรับบันทึกไฟล์
def save_file(dir, file):
    delete_old_file(dir, ".jpg")
    if not dir.endswith('/'):
        dir += '/'
        
    # ตรวจสอบชื่อไฟล์ใหม่เพื่อหลีกเลี่ยงการซ้ำ
    unique_filename = generate_unique_filename(dir, file.name)
    
    with open(f'{dir}{unique_filename}', 'wb+') as target:
        for chunk in file.chunks():
            target.write(chunk)
    
    return unique_filename
