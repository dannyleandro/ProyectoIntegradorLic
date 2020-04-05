from django.db import models
from django.contrib.auth.models import User
from datetime import datetime 

# Create your models here.
class Product (models.Model):
    SegmentCode = models.IntegerField()
    SegmentName = models.CharField(max_length=255)
    FamilyCode = models.IntegerField()
    FamilyName = models.CharField(max_length=255)
    ClassCode = models.IntegerField()
    ClassName = models.CharField(max_length=255)
    ProductCode = models.IntegerField(primary_key=True)
    ProductName = models.CharField(max_length=255)


class Profile(models.Model):
    IdProfile = models.AutoField(primary_key=True)
    User = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    Description = models.CharField(max_length=255)
    City = models.CharField(max_length=255)
    State = models.CharField(max_length=255)
    ProductCode = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)


class Process (models.Model):
    IdProcess = models.AutoField(primary_key=True)
    EntityCode = models.IntegerField(null=True)
    EntityName = models.CharField(max_length=255, null=True)
    EntityNIT = models.CharField(max_length=15, null=True)
    ProcessNumber = models.CharField(max_length=15)
    ProcessState = models.IntegerField(null=True)
    ProcessStateName = models.CharField(max_length=255, null=True)
    ExecutionCity = models.TextField(null=True)
    IdProcessType = models.IntegerField(null=True)
    ProcessTypeName = models.CharField(max_length=255, null=True)
    SegmentCode = models.IntegerField(null=True)
    FamilyCode = models.IntegerField(null=True)
    ClassCode = models.IntegerField(null=True)
    Description = models.TextField(null=True)
    ContractType = models.CharField(max_length=255, null=True)
    LoadDate = models.DateField(null=True)
    SystemLoadDate = models.DateTimeField(default=datetime.now)
    Amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.0, null=True)
    DefinitiveAmount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
