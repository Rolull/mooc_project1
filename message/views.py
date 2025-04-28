from django.utils.timezone import now
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Message
import logging

logger = logging.getLogger('django')

def message_list(request):
    if request.method == "POST":
        if "message_text" in request.POST and request.user.is_authenticated:
            # Check if the user has posted in the last 10 seconds
            last_message = Message.objects.filter(user=request.user).order_by("-created_at").first()
            if last_message and (now() - last_message.created_at) < timedelta(seconds=10):
            # FIX FLAW 5: Insecure Design 
            #if last_message and (now() - last_message.created_at) < timedelta(seconds=300):
                # If the user has posted recently, show an error message
                messages = Message.objects.select_related("user").order_by("-created_at")[:20]
                error = "You can only post once every 10 seconds."
                # FIX FLAW 5: Insecure Design
                #error = "You can only post once every 5 minutes."
                logger.info(f"User '{request.user.username}' attempted to post too soon.")
                return render(request, "messages/message_list.html", {"messages": messages, "error": error})

            # Create the new message
            message_text = request.POST.get("message_text")
            if message_text:
                Message.objects.create(user=request.user, text=message_text)
                logger.info(f"User '{request.user.username}' posted a new message: {message_text}")

        #FIX FLAW 4: Broken Access Control
        elif "delete_message_id" in request.POST and request.user.is_authenticated:
            message_id = request.POST.get("delete_message_id")
            Message.objects.filter(id=message_id).delete()
            logger.info(f"User '{request.user.username}' deleted a message with ID: {message_id}")
        return redirect("home")
    
        #FIX FLAW 4: Broken Access Control     
        #elif "delete_message_id" in request.POST and request.user.is_authenticated:
        #   message_id = request.POST.get("delete_message_id")
        #   message = Message.objects.filter(id=message_id, user=request.user).first()
        #   if message:
        #       logger.info(f"User '{request.user.username}' deleted a message with ID: {message_id}")
        #       message.delete()
        #return redirect("home")

    messages = Message.objects.select_related("user").order_by("-created_at")[:20]
    return render(request, "messages/message_list.html", {"messages": messages})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            logger.info(f"New user registered: {user.username}")
            return redirect("home")  
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})
