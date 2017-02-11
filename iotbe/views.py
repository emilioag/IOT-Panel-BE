from rest_framework.decorators import api_view
from rest_framework.response import Response
from iotbe.models import Measure
from collections import OrderedDict


@api_view(['GET'])
def measures_between(request, name, from_timestamp, to_timestamp, interval):
    kwargs = {
        'gte': int(from_timestamp),
        'lte': int(to_timestamp),
        'name': name,
        'interval': interval
    }
    return Response(
        OrderedDict(sorted(Measure.agg(**kwargs).items(), key=lambda t: t[0])))
