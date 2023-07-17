from datetime import datetime, timezone, date, timedelta
from django.utils.timezone import localtime
import face_recognition
from PIL import Image

from face.models import *
import traceback
import socket
import os

def FolderCreation(path):
    if not os.path.exists(path):
        os.makedirs(path)
        
        
def Tempfile_delete(path):    
    os.remove(path)


def errorLogs(Transactionname, msg, app_code, status_code):
    """
        Summary or Description:
            When error occurs the error will store into log database model.
    """
    dt = localtime(datetime.now(timezone.utc))
    HOSTNAME = socket.gethostname()
    Logs.objects.create(TransactionName=Transactionname, Mode='POST', LogMessage=str(msg), LogDate=dt,  SystemName=HOSTNAME, app_code=app_code, status_code=status_code)



from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image
import time 

class faceRecognize:

    @classmethod        
    def crop_RecognizedFace(cls, emp_image, emp_name):
        try:
            starttime = time.time()
            unknown_image = face_recognition.load_image_file(emp_image)
            face_locations = face_recognition.face_locations(unknown_image)
            endtime = time.time()
            print('--time-crop--',endtime-starttime)

            top, right, bottom, left = face_locations[0]
            face_image_pil = Image.fromarray(unknown_image[top:bottom, left:right])
            face_image_pil.save('media/data_001.jpg')

            buffer = BytesIO()
            face_image_pil.save(buffer, format='JPEG')
            face_image_file = InMemoryUploadedFile(buffer, None, f"cropped_{emp_name}.jpg", 'image/jpeg', buffer.tell(), None)

            return face_image_file
        
        except IndexError as e :
                raise Exception({"Status":"Face could not be detected Properly. please Register again"})


    @classmethod  
    def encoded_face(cls, emp_image, app_code):
        try:
            new_image = face_recognition.load_image_file(emp_image)
            new_encoding = face_recognition.face_encodings(new_image)[0]
            return new_encoding
        
        except IndexError as e :
            error_msg = {'message':e, 'traceback':traceback.format_exc()}
            print('--error_msg--',error_msg)
            errorLogs('FaceRecognitionAPI', error_msg , app_code, 400) 
            raise Exception({"Status":"Face could not be detected Properly. please Register again"})