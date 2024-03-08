from django.db import models

from django.contrib.auth.models import User # Questo è un modello preimpostato di Django


# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) # Null vale per i database, blank vuol dire che anche il form submittato può essere vuoto
    participants = models.ManyToManyField(User, related_name='participants', blank=True) #Il related_name serve per l'accesso inserso. Se ho un istasnza User farò user.participants.all()
    updated = models.DateTimeField(auto_now=True) #Vuol dire che ogni volta che viene salvato si aggiorna
    created = models.DateTimeField(auto_now_add=True) #Data di quando è stata creata
    
    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.name
    
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # Relazione 1 to many
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True) 
    created = models.DateTimeField(auto_now_add=True) 
    
    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.body[0:50] # Mostra i primi 50 caratteri
    
    