from django.shortcuts import render, redirect

from django.http import HttpResponse

from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message

from .forms import RoomForm, UserForm

from django.contrib import messages

# Create your views here.
# def home(request):
#     return HttpResponse('Home Page')




# rooms = [
#     {'id': 1, "name": "Lets learn python!"},
#     {'id': 2, "name": "Design with me!"},
#     {'id': 3, "name": "Frontend Dev!"},
#     {'id': 4, "name": "Backend Dev!"},
# ]



def loginPage(request):
    
    page = 'login'
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        print(username)
        print(password)
        try:
          user = User.objects.get(username=username)
        except:
          messages.error(request, 'User does not exist')
          
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')
    
    context = {'page':page}
    return render(request, 'base/login_register.html', context)
 
def logoutUser(request):
    logout(request)
    return redirect('home')   

def registerPage(request):
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # Commit=false ritarda il salvataggio nel database finchè non compare un commit=true
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        
        else:
            messages.error(request, 'An error occurred during registration')
            
    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    
    # rooms = Room.objects.all() # Importiamo il modello e utilizziamo objects.all() per recuperare tutti gli items dal model
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
            Q(topic__name__icontains=q) | # Il doppio __ significa trovami in Room quelle con un topic il cui name contenga q (icontains vuol dire non fa nulla maiuscolo o minuscolo)
            Q(name__icontains=q) | 
            Q(description__icontains=q) # La classe Q di Django consente di creare query più complesse creando per esempio un OR nella query       
        )
    
    room_count = rooms.count()
    
    # room_messages = Message.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    
    topics = Topic.objects.all()[0:5]
    
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html' , context)

def room(request, pk):
    # Il secondo parametro si chiama pk perchè nella route in urls.py abbiamo definito pk come parametro per room/<int: pk>
    
    
    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
        
    room = Room.objects.get(id=pk) # Il metodo get restituisce solo 1 item in base alla condizione inserita. Se ne trova di più da errore (si usa filter negli altri casi)
    
    #room_messages = room.message_set.all().order_by('-created') 
    room_messages = room.message_set.all() #con _set.all() viene utilizzato per recuperare tutti gli oggetti correlati da una relazione 1 a n. Recupera il set di messaggi contenuti in una room
    
    participants = room.participants.all() # Qui non si usa il _set.all() perchè nel modello abbiamo un related_name impostato
    
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room =room,
            body = request.POST.get('body')
        )
        
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
        
    # Per il template da mostrare è importante che la cartella all'interno dell'app si chiami templates/<nome dell'app>
    return render(request,'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms':rooms, 'room_messages': room_message, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name) # Recupera o crea un nuovo valore. Se inseriamo un valore nuovo topic conterrà il valore creato e created sarà TRUE
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')            
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
            # return redirect('home')
        return redirect('home')
    
    context = {'form': form, 'topics':topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')     
        room.save()
        return redirect('home')
        # form = RoomForm(request.POST, instance=room)
        # if(form.is_valid):
        #     form.save()
        #     return redirect('home')
    
    context = {'form': form, 'topics': topics, 'room':room}
    
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj':room})



@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj':message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    context = {'form': form, 'user':user}
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
            
    return render(request, 'base/update-user.html', context)



def topicPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})