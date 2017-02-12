from django.db import models
from arrow import Arrow
from dateutil.parser import parse
import pandas as pd
import numpy as np
from dateutil.tz import tzutc
import datetime
from django.core.exceptions import ValidationError

NAME_CHOICES = (
    ('temp', 'temperature'),
    ('hum', 'Humidity')
)


def get_date(date, _format, tzinfo=tzutc()):
    if isinstance(date, datetime.datetime):
        measure_date = date.replace(tzinfo=tzinfo)
    elif isinstance(date, int) or _format == 'timestamp':
        measure_date = Arrow.fromtimestamp(date).naive.replace(tzinfo=tzinfo)
    else:
        measure_date = parse(date).replace(tzinfo=tzinfo)
    return measure_date


class Measure(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField()
    name = models.CharField(
        max_length=300,
        choices=NAME_CHOICES)
    value = models.FloatField()

    class Meta:
        unique_together = ('name', 'date',)

    @classmethod
    def insert(cls, name, value, date, _format='string', tzinfo=tzutc()):
        return cls(
            name=name,
            value=value,
            date=get_date(date, _format, tzinfo)
        ).save()

    @classmethod
    def update(cls, name, date, value, _format='string', tzinfo=tzutc()):
        qset = cls.objects.filter(
            name=name, date=get_date(date, _format, tzinfo))
        if len(qset) == 1:
            measure = qset[0]
            measure.value = value
            measure.save()
        elif len(qset) == 0:
            measure = Measure(
                name=name, value=value, date=get_date(date, _format, tzinfo))
            measure.save()

    @classmethod
    def between(cls,
                gte=Arrow.now().replace(months=-1).naive,
                lte=Arrow.now().naive,
                name=None,
                _format='datetime',
                tzinfo=tzutc()):
        query = {
            'date__gte': get_date(gte, _format, tzinfo),
            'date__lte': get_date(lte, _format, tzinfo)
        }
        if name:
            query['name'] = name
        return cls.objects.filter(**query).values()

    @classmethod
    def agg(cls, gte=None, lte=None, name=None, interval='year', function=np.average):
        if gte and lte:
            _l = list(cls.between(gte=gte, lte=lte, name=name))
        else:
            _l = list(cls.objects.all().values())

        def f(x):
            return x.values.tolist() if len(x.values.tolist()) > 0 else False

        def a(pd_date, format):
            return Arrow.fromdatetime(pd_date).format(format)

        def b(ids):
            _list = list(df[df['id'].isin(ids)]['value'].to_dict().values())
            return function(_list)

        options = {
            'minute': ('T', 'DD-MM-YYYY HH:mm'),
            'hour': ('H', 'DD-MM-YYYY HH'),
            'day': ('D', 'DD-MM-YYYY'),
            'year': ('D', 'YYYY')
        }
        df = pd.DataFrame(_l)
        df_idx = df.set_index('date')
        g = df_idx.resample(options[interval][0]).apply(f)
        as_dict = g[g['id'] != False].to_dict()['id']

        return {
            a(date.to_pydatetime(), options[interval][1]): b(ids)
            for date, ids in as_dict.items()
        }

    def save(self, *args, **kwargs):
        choices = [i[0] for i in NAME_CHOICES]
        if (self.name not in choices):
            raise ValidationError('Name mus be in {}'.format(choices))
        else:
            super(Measure, self).save(*args, **kwargs)

    def _update(self, value):
        self.value = value
        self.date = self.date
        self.save()
