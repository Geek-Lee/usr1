from django.db import models
from django.contrib import admin


# Create your models here.
class sql_record(models.Model):
    user = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    ip_address = models.IPAddressField()
    creat_at = models.DateTimeField()
    query_time = models.FloatField()
    lock_time = models.FloatField()
    rows_sent = models.BigIntegerField()
    rows_examined = models.BigIntegerField()
    query_table = models.TextField()
    date = models.CharField(max_length=150, default=None)


class match_result(models.Model):
    ip_address = models.IPAddressField()
    user_id = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    action_time = models.DateTimeField()
    api = models.CharField(max_length=100)
    user_action = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    GeoCoordX = models.FloatField(max_length=100)
    GeoCoordY = models.FloatField(max_length=100)


class user_info(models.Model):
    ip_address = models.IPAddressField()
    company = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    GeoCoordX = models.FloatField(max_length=100)
    GeoCoordY = models.FloatField(max_length=100)
    province = models.CharField(max_length=100)

class sql_record_admin(admin.ModelAdmin):
    list_display = (
    'user', 'company', 'ip_address', 'creat_at', 'query_time', 'lock_time', 'rows_sent', 'rows_examined', 'query_table')


class Meta:
    ordering = ('-creat_at', 'user')


admin.site.register(sql_record, sql_record_admin)
