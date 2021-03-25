from django.db import models


class Courier(models.Model):
    type_choices = [('foot', 'foot'), ('bike', 'bike'), ('car', 'car'),]
    courier_id = models.IntegerField(primary_key=True)
    courier_type = models.CharField(max_length=20, choices=type_choices)
    regions = models.CharField(max_length=120, default='')
    working_hours = models.CharField(max_length=240, default='')

    payload_dict = {
        'foot': 10,
        'bike': 15,
        'car': 50,
    }

    @property
    def payload(self):
        return __class__.payload_dict[self.courier_type]