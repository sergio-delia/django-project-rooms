from django.forms import ModelForm
from .models import Room
from django.contrib.auth.models import User 

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        #Aggiungendo exclude si indica i campi che non voglio mostrare nel form
        exclude = ['host', 'participants']
        
        
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']