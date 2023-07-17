from rest_framework import serializers
from .models import FaceSource
from face.utils import faceRecognize
import time
      
        
class FaceSourceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FaceSource
        fields = ['facesourceId', 'AppCode', 'empId', 'branchId', 'companyName', 'empName','empImage', 'encodedCode']
        read_only_fields = ['facesourceId',]

    def validate(self, attrs):
        emp_image = attrs.get('empImage')
        emp_name = attrs.get('empName')
        app_code = attrs.get('AppCode')

        starttime = time.time()
        # get cropped image from full size image 
        cropped_face_img = faceRecognize.crop_RecognizedFace(emp_image, emp_name)
        endtime = time.time()
        print('--runtime--',endtime-starttime)
        
        # change assighed value data
        attrs['empImage'] = cropped_face_img
        attrs['encodedCode'] = faceRecognize.encoded_face(emp_image, app_code).tolist()


        return super().validate(attrs)



        
class GetFaceSourceFromDBSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = FaceSource
        fields = ['facesourceId', 'AppCode', 'empId', 'companyName', 'empName','empImage']
