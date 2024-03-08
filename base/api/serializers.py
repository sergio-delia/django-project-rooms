# Il serialize serve per passare e trasformare in Json response una query_set di Python. Quando recuperiamo tutte le info delle camere per esempio dal db c'è bisogno di serializzarle

from rest_framework.serializers import ModelSerializer
from base.models import Room

class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'