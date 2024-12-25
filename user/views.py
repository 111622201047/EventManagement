from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse,JsonResponse,FileResponse
from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from .models import *
from .forms import CreateUserForm
from django.contrib import messages
from .models import User,UserEvents
from django.core.mail import send_mail


def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

            user = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            messages.success(request, user + ' Created Account Successfully')
            subject = "Evento Registration"
            email = form.cleaned_data.get('email')  # to whom you want to send
            request.session['email'] = email
            email = EmailMessage(subject, " Hello 👋" + user+", You Successfully  Registered for Evento Website here is the link :    ",to=[email])  # to will take list of email IDs
            #email.send()
            messages.success(request,'Email Has been Sent to User '+user)
            response = HttpResponse("Cookie Demo")
            response.set_cookie('username', user)
            response.set_cookie('password', password)
            return redirect('login')


    context = {'form':form}
    return render(request, "register.html",context)


def loginpage(request):
    if request.user.is_authenticated:
        return redirect('userhome')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request,username = username ,password = password)

            if user is not None:
                login(request,user)
                request.session['username'] = username
                messages.success(request, username + ' Logged In Successfully')
                return redirect('userhome')
            else:
                messages.info(request , 'Username Or Password is Incorrect')

        context = {}
        return render(request, "login.html",context);

def adminlogin(request):
    if request.user.is_authenticated:
        return redirect('adminhome')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                request.session['username'] = username
                messages.success(request, username + ' Logged In Successfully')
                return redirect('adminhome')
            else:
                messages.info(request, 'Username Or Password is Incorrect')

        context = {}
        return render(request, "login.html", context);

def adminhome(request):
    bookedevents = UserEvents.objects.all()
    count = UserEvents.objects.all().count()
    return render(request,"adminhome.html",{ 'bookedevents':bookedevents,'count':count})

def myaccount(request):
    username = request.session['username']
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        mobile = request.POST['mobile']
        address = request.POST['address']

        user = User()
        user.fname = fname
        user.lname = lname
        user.email = email
        user.mobile = mobile
        user.address = address

        user.save()
        messages.success(request, ' Account Details Updated  Successfully ')
    return render(request,"myaccount.html",{'username':username })

def bookevent(request):
    username = request.session['username']
    #semail = request.session['email']
    if request.method == 'POST':
        name = request.POST.get('name')
        eventname = request.POST.get('eventname', False);
        email = request.POST.get('email', False);
        date = request.POST.get('date', False);
        mobile = request.POST.get('mobile', False);
        altmobile = request.POST.get('altmobile', False);
        amount = request.POST.get('amount',False);
        description = request.POST.get('description', False);
        print(name,eventname)
        eventbook = UserEvents()

        toname = eventbook.name = name
        toeventname = eventbook.eventname = eventname
        toemail = eventbook.email = email
        todate = eventbook.date = date
        tomobile = eventbook.mobile = mobile
        toaltmobile = eventbook.altmobile = altmobile
        toamount = eventbook.amount = amount
        todescription = eventbook.description = description

        eventbook.save()
        subject = "Event Booking"
        email = toemail  # to whom you want to send
        eventname = toeventname
        email = EmailMessage(subject,
                             " Hello " + username + ", You Successfully  Booked for a "+ eventname +" Event Our Event Managers Will Contact You Soon through mobile "
                                                                                                 " ### Booking Details ### "
                                                                                                 " Full Name : " + toname  +
                             " Event Name : " + toeventname +" Event Date : " + todate  +" Mobile : " + tomobile  + " Alt Mobile : " + toaltmobile  +
                             " Efforded Amount : " + toamount + " Description : " + todescription  +
                            "   Stay Tune to More Updates Have a Great Day 😊    ",
                             to=[email])  # to will take list of email IDs
        email.send()
        messages.success(request, ' Event Booked Successfully we will Contact You soon through mail Stay Tuned :)')

    return render(request,"bookevent.html",{'username':username}  )


def deleteevent(request,name,eventname):
    username = request.session["username"]
    UserEvents.objects.filter(name=name,eventname=eventname).delete()
    messages.success(request, ' Event Deleted Successfully ')
    return redirect('adminhome')

def updateevent(request,name,eventname):
    username = request.session["username"]
    request.session["name"]= name
    request.session["eventname"] = eventname
    userevents = UserEvents.objects.filter(name=name, eventname=eventname)
    return render(request,'updateeventdetails.html',{'name':name , 'eventname' : eventname , })

from django.core.exceptions import MultipleObjectsReturned

def updateeventdetails(request):
    name = request.session.get("name")
    eventname = request.session.get("eventname")

    # Check if session variables are set
    if not name or not eventname:
        messages.error(request, "Session variables are not set correctly.")
        return redirect('adminhome')

    if request.method == 'POST':
        # Get form data
        semail = request.POST.get('email')
        date = request.POST.get('date')
        mobile = request.POST.get('mobile')
        altmobile = request.POST.get('altmobile')
        amount = request.POST.get('amount')
        description = request.POST.get('description')

        # Debug: Print the form data
        print(f"Form Data: email={semail}, date={date}, mobile={mobile}, amount={amount}, description={description}")

        # Validate form data
        if not semail or not date or not mobile or not amount or not description:
            messages.error(request, "All fields are required!")
            return redirect('updateeventdetails')  # Replace with the correct view name

        try:
            # Retrieve the event(s) and check if they exist
            events = UserEvents.objects.filter(name=name, eventname=eventname)

            if not events.exists():
                messages.error(request, 'Event not found.')
                return redirect('updateeventdetails')

            # Update the latest event or all matching events
            for event in events:
                event.email = semail
                event.date = date
                event.mobile = mobile
                event.altmobile = altmobile
                event.amount = amount
                event.description = description
                event.save()  # Save the updated event

            print(f"Updated Events: {events}")  # Debug: Verify the events are updated

            # Send email notification
            subject = "Event Booking Updated"
            message_body = f"Hello {name}, Your booked event '{eventname}' has been updated by the admin. Please check the details."
            email = EmailMessage(subject, message_body, to=[semail])
            email.send()

            messages.success(request, 'Event updated successfully! Check your email for updates.')
            return redirect('adminhome')  # Redirect to the admin home page

        except MultipleObjectsReturned:
            messages.error(request, 'Multiple events found with the same details. Please refine your search.')
            return redirect('updateeventdetails')

    return render(request, "adminhome.html", {'username': name})

def open_email_form(request, email):
    """Display the email form for the selected user."""
    context = {'email': email}
    return render(request, 'email_form.html', context)
    
def send_email(request, email):
    """Send an email to the user with the details entered by the admin."""
    if request.method == 'POST':
        appointment_date = request.POST['date']
        appointment_time = request.POST['time']
        message_content = request.POST['message']

        # Email subject and message
        subject = f"Appointment Scheduled on {appointment_date} at {appointment_time}"
        message = f"""
        Dear User,

        You have an appointment scheduled on {appointment_date} at {appointment_time}.

        Message:
        {message_content}

        Thank you!

        Best regards,  
        Your Event Team
        """

        from_email = settings.EMAIL_HOST_USER  # Your email address
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, f"Email successfully sent to {email}!")
        except Exception as e:
            messages.error(request, f"Error sending email: {str(e)}")
        
        return redirect('adminhome')  # Redirect to the admin home page