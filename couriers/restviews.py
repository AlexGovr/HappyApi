from rest_framework import viewsets
from .serializers import CourierSerializer
from .models import Courier


class CourierViewset(viewsets.ModelViewSet):

    serializer_class = CourierSerializer
    queryset = Courier.objects.all()