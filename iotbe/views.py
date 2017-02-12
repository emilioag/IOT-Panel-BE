from rest_framework.decorators import api_view
from rest_framework.response import Response
from iotbe.models import Measure
from collections import OrderedDict
import numpy as np
from rest_framework.exceptions import NotFound


@api_view(['GET'])
def measures_between(
        request, function, name, from_timestamp, to_timestamp, interval):
    functions = {
        'max': np.max, 'min': np.min, 'avg': np.average, 'std': np.std
    }
    f = functions.get(function)
    if not f:
        raise NotFound()
    kwargs = {
        'gte': int(from_timestamp),
        'lte': int(to_timestamp),
        'name': name,
        'interval': interval,
        'function': f
    }
    d = OrderedDict(sorted(Measure.agg(**kwargs).items(), key=lambda t: t[0]))
    return Response({
        'x': d.keys(),
        'y': d.values()
    })
