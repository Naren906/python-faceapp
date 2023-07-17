from .serializer import  GetFaceSourceFromDBSerializer,FaceSourceSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models  import  FaceSource
from django.db.models import F
from .utils import *

import concurrent.futures
import face_recognition
import numpy as np
import traceback
from django.db import transaction
import time

Media_path = '/mnt/e/Narenthiran/Working/python-faceapp/FaceappAPI/media/'
# Create your views here.


# Runtime 7-8 seconds Type-2
class FaceRecognitionAPI(APIView):
    __slots__ = ['appID', 'branchID', 'snap', 'faceapp_det','image','facerecognize','live_src']
    
    def post(self,request):
        try:
            self.appID = request.query_params.get('appCode')
            self.branchID = request.query_params.get('branchId')
            starttime = time.time()
            self.snap = faceRecognize.crop_RecognizedFace(request.FILES.get('snap'),'snapRecognize')
            endtime = time.time()
            print('--time-01--',endtime-starttime)

            result = list(FaceSource.objects.filter(AppCode=self.appID,branchId=self.branchID).values('empId','empName','empImage','encodedCode').annotate(fullImageUrl=F('empImage')))
            self.facerecognize=False

            #Face Recognition from scanned
            try:
                unknown_image = face_recognition.load_image_file(self.snap)
                unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            except IndexError as e :
                print('--e--',e)
                return Response({"Status":"Face could not be detected Properly. please scan again"},status=status.HTTP_400_BAD_REQUEST)

            results_con = []
            starttime = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(Ana_con, data_itm, unknown_encoding) for data_itm in result]

                # Wait for the tasks to complete
                concurrent.futures.wait(futures)

                print('----',len(futures))
                # Obtain the results
                for future in futures:
                    if future is not None and future.result() is not None:
                        results_con.append(future.result())
            endtime = time.time()
            print('--time-02--',endtime-starttime)
 
            if len(results_con) != 0:      
                min_result = min(results_con, key=lambda result: result['distance'])
                return Response({"Match":min_result},status=status.HTTP_200_OK)
            else:
                errorLogs('FaceRecognitionAPI', {"Match":self.facerecognize} , self.appID, '401') 
                return Response({"Match":self.facerecognize},status=status.HTTP_401_UNAUTHORIZED)
              
        except Exception as e:
            error_msg = {'message':e, 'traceback':traceback.format_exc()}
            print("\033[91m ----{}\033[00m" .format(error_msg))  
            errorLogs('FaceRecognitionAPI', error_msg , self.appID, 400) 
            return Response({"Status":"Face could not be detected Properly. please Register again"} ,status=status.HTTP_400_BAD_REQUEST)

               
def Ana_con(data, snap_encoding):
    
    encodedCode = data['encodedCode']

    verify = face_recognition.compare_faces([encodedCode], snap_encoding)
    distance = face_recognition.face_distance([encodedCode], snap_encoding)
    
    if verify[0]:            
        if distance[0] < 0.50: 
            compare_data={'verified':True, 'distance':distance[0], 'employeeid':data['empId'], 
                        'employeename':data['empName'] ,'src_file': data['empImage'] }
            return compare_data


 
# Runtime 10 seconds  Type-3
class FaceRecognitionType3API(APIView):
    __slots__ = ['appID', 'snap', 'faceapp_det','image','facerecognize','live_src']
    
    def post(self,request):
        try:
            self.appID = request.query_params.get('appID')
            self.snap = request.FILES.get('snap') 
            print('-- snap --', self.snap)
            self.facerecognize = False

            result = list(FaceSource.objects.filter(AppCode=self.appID).values('EmpId','emp_Image_path','EmpName').order_by('EmpId'))

            start_time_con = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                known_image_futures = [executor.submit(face_recognition.load_image_file, Media_path + files['emp_Image_path']) for files in result]
                concurrent.futures.wait(known_image_futures)
                
                known_face_encodings_futures = [executor.submit(face_recognition.face_encodings, futures.result()) for futures in known_image_futures]
                concurrent.futures.wait(known_face_encodings_futures)
                
                # known_face_encodings = list(map(lambda f: f.result()[0], known_face_encodings_futures))
                
            end_time_con = time.time()
            print("\033[96m --1.0.1--{}\033[00m" .format(end_time_con - start_time_con))

            start_time_con = time.time()
            # Load unknown face encoding
            unknown_image = face_recognition.load_image_file(self.snap)
            unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
            end_time_con = time.time()
            print("\033[96m --2--{}\033[00m" .format(end_time_con - start_time_con))

            start_time_con = time.time()
            # Convert face encodings to NumPy arrays
            known_face_encodings = np.array(known_face_encodings)
            unknown_face_encoding = np.array(unknown_face_encoding)
            end_time_con = time.time()
            print("\033[96m --3--{}\033[00m" .format(end_time_con - start_time_con))

            # Calculate Euclidean distances
            start_time_con = time.time()
            distances = face_recognition.face_distance(known_face_encodings, unknown_face_encoding)
            end_time_con = time.time()
            print("\033[96m --4--{}\033[00m" .format(end_time_con - start_time_con))

            # Find the index with the minimum distance
            min_distance_index = np.argmin(distances)

            if distances[min_distance_index]:
                result_det = result[min_distance_index]
                result_data = {'verified': True, 'distance': distances[min_distance_index], 'employeeid': result_det['EmpId'], 
                                'employeename': result_det['EmpName'], 'src_file': Media_path + result_det['emp_Image_path']}
                return Response({"Match": result_data}, status=status.HTTP_200_OK)
            else:
                return Response({"Match": self.facerecognize})
            
        except Exception as e:
            error_msg = {'message':e, 'traceback':traceback.format_exc()}
            print("\033[91m ----{}\033[00m" .format(error_msg))   
            return Response({"Status":"Face could not be detected Properly. please Register again"} ,status=status.HTTP_400_BAD_REQUEST)
               
     
class AddFaceSourceAPI(APIView):
    
    def post(self, request):
        try:
            with transaction.atomic():
                serializer_class = FaceSourceSerializer(data=request.data,context={'request':request})
                if serializer_class.is_valid():                    
                    serializer_class.save()
                    return Response({"Status":"Created Successfully",'data':serializer_class.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"Status":"Created Failed"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            error={"error":e, "traceback":traceback.format_exc()}
            print('----error----',error)
            return Response({"Status":"Created Failed"}, status=status.HTTP_400_BAD_REQUEST)


class GetSourceFromDbAPI(APIView):
    
    def get(self, request):
        app_code = request.query_params.get('app_code')
        try:
            query_set = FaceSource.objects.filter(AppCode=app_code)
            serializer_class = GetFaceSourceFromDBSerializer(query_set, many=True, context={'request':request})
            return Response(serializer_class.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            error={"error":e, "traceback":traceback.format_exc()}
            print('---error---',error)
            return Response(error, status=status.HTTP_400_BAD_REQUEST)