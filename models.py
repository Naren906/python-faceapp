from django.contrib.postgres.fields import ArrayField
from django.db import models
import os
   
class FaceSource(models.Model):
    facesourceId=models.BigAutoField(primary_key=True, editable=False)
    AppCode = models.CharField(max_length=100)
    empId = models.IntegerField()
    branchId = models.IntegerField()
    companyName = models.CharField(max_length=100)
    empName = models.CharField(max_length=100)
    
    def get_upload_path(instance, filename):
        #store file by company name
        return os.path.join('employee', instance.companyName, filename)

    empImage = models.ImageField(upload_to=get_upload_path)
    encodedCode = ArrayField(models.FloatField(), null=True, blank=True, size=128)
    


class Logs(models.Model):
    LogId = models.BigAutoField(primary_key=True, editable=False)
    TransactionName = models.CharField(max_length=250)
    Mode = models.CharField(max_length=100)
    LogMessage = models.TextField()
    status_code = models.CharField(max_length=100, null=True, blank=True)
    SystemName = models.CharField(max_length=100, null=True, blank=True)
    LogDate = models.DateTimeField()
    app_code = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.TransactionName
        