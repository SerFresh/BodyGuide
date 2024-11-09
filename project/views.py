import os
import numpy as np
from django.shortcuts import render
from .forms import UploadFrom
import tensorflow as tf
import pandas as pd
import tensorflow_hub as hub
#from tensorflow.keras.models import load_model
model_path = 'model-21-1.32.h5'
train_path = '/media/train'
tf.keras.utils.get_custom_objects().update({'KerasLayer': hub.KerasLayer})

model = tf.keras.models.load_model(model_path)

# Define image dimensions
BATCH_SIZE = 64
image_height, image_width = 600, 600

# Define class names based on your training data
train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

# Define training generator
train_generator = train_datagen.flow_from_directory(
    train_path,  # training data directory
    target_size=(image_height, image_width),  # Set dimensions as a tuple
    batch_size=BATCH_SIZE,
    class_mode='categorical',  # multi-class classification
    shuffle=True               # Shuffle the data to avoid order bias
)
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
def predict_image(dir, img_path, user_shape):
    # Load the class shape data
    df = pd.read_csv('ClassWithShape.csv')

    # Load and preprocess the image
    picture = os.path.join(dir, img_path)
    img = tf.keras.preprocessing.image.load_img(picture, target_size=(600, 600))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, 0) / 255.0
    
    # Load the trained model
    predictions = model.predict(img_array)
    
    class_labels = list(train_generator.class_indices.keys())  # Example: Assuming df has a 'Class' column
    
    # Get predicted class and confidence
    #predicted_class = tf.argmax(predictions, axis=1).numpy()[0]
    #confidence = tf.reduce_max(predictions).numpy()
    predicted_class_index = np.argmax(predictions, axis=1)[0]  # Class index with highest probability
    predicted_class_name = class_labels[predicted_class_index]
    confidence = np.max(predictions)
    # Get class labels (ensure you have these labels saved during training)
    
    
    # Extract the shape list for the predicted class
    shape_list = df[df['Class'] == predicted_class_name]['Shape'].values[0].split(",")

    # Check if predicted class matches the user's shape
    if predicted_class_name == "other":
        return user_shape, "Please upload a valid image of clothing.", confidence
    elif user_shape in shape_list:
        return user_shape, f"Predicted Class: {predicted_class_name} is suitable for your shape.", confidence
    else:
        return user_shape, f"Predicted Class: {predicted_class_name} is NOT suitable for your shape.", confidence

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
