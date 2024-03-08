# from django.http import JsonResponse

# Abbiamo installare Django rest framework che aggiunge una semplice interfaccia alle api create
from rest_framework.decorators import api_view
from rest_framework.response import Response
# Importiamo ciò che ci serve per creare l'interfaccia

from base.models import Room

from .serializers import RoomSerializer


# È necessario anche installare django cors headers (aggiungere in settings.py anche la configurazione e i middleware)

# Questo decoratore accetta come input tutti i metodi per cui quella API è valida
@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id',
    ]
    # return JsonResponse(routes, safe=False)
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    
    # Per passare ad api il risultato di una query è necessario prima serializzare il tutto. Per farlo passiamo prima dal serializer. Il parametro many indica se deve serializzare solo uno o tutto
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id = pk)
    
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)