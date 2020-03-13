from django.db import models
from django.contrib.auth.models import User


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
    EntityCode = models.IntegerField()
    EntityName = models.CharField(max_length=255)
    EntityNIT = models.CharField(max_length=15)
    ProcessType = models.IntegerField()
    ProcessNumber = models.IntegerField()
    ProcessState = models.IntegerField()
    ExecutionCity = models.CharField(max_length=255)
    IdProcessType = models.IntegerField()
    ProcessTypeName = models.CharField(max_length=255)
    SegmentCode = models.IntegerField()
    FamilyCode = models.IntegerField()
    ClassCode = models.IntegerField()
    Description = models.CharField(max_length=255)
    ContractType = models.CharField(max_length=255)
    LoadDate = models.DateField()
    SystemLoadDate = models.DateTimeField()
    Amount = models.DecimalField(max_digits=20, decimal_places=2)
    DefinitiveAmount = models.DecimalField(max_digits=20, decimal_places=2)
