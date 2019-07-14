from django.db import models


class ip_class(models.Model):
    ip = models.CharField(max_length=14)
    tresh_time = models.TimeField(null=True)
    trials = models.IntegerField(default=0)
    def __str__(self):
        return self.ip


