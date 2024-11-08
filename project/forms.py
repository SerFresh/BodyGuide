from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

class UploadFrom(forms.Form):
    file = forms.ImageField(required=False)  # ไม่บังคับให้กรอกไฟล์ใหม่ทุกครั้ง
    shape_choices = [
        ('', '-- เลือกรูปร่างของคุณ --'),
        ('Pear', 'รูปร่างลูกแพร์'),
        ('Apple', 'รูปร่างแอปเปิ้ล'),
        ('Inverted triangle', 'รูปร่างสามเหลี่ยมกลับหัว'),
    ]
    shape = forms.ChoiceField(choices=shape_choices, required=True, label="เลือกประเภทของรูปร่าง")
