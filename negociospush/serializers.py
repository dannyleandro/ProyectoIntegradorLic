from rest_framework import serializers
from .models import Profile, Process, Product


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'IdProfile',
            'Description',
            'City',
            'State',
            'ProductCode',
            'User',
        )
        model = Profile


class ProductSerializer (serializers.ModelSerializer):
    class Meta:
        fields = (
            'SegmentCode',
            'SegmentName',
            'FamilyCode',
            'FamilyName',
            'ClassCode',
            'ClassName',
            'ProductCode',
            'ProductName'
        )
        model = Product


class ProcessSerializer (serializers.ModelSerializer):
    class Meta:
        fields = (
            'IdProcess',
            'EntityCode',
            'EntityName',
            'EntityNIT',
            'ProcessNumber',
            'ProcessState',
            'ProcessStateName',
            'ExecutionCity',
            'IdProcessType',
            'ProcessTypeName',
            'SegmentCode',
            'FamilyCode',
            'ClassCode',
            'Description',
            'ContractType',
            'LoadDate',
            'SystemLoadDate',
            'Amount',
            'DefinitiveAmount'
        )
        model = Process
