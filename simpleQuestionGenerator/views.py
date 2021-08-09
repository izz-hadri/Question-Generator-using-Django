from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .decorators import unauthenticated_Creator, allowed_Creator
from .functions import *


@unauthenticated_Creator
def index(request):
    objPlans = Plan.objects.all()
    if request.method == "GET":
        context = {'objPlans': objPlans}
        return render(request, 'views/index.html', context)
    elif request.method == 'POST':
        text = request.POST.get('text')
        if len(text) > 100:
            messages = "Characters cannot be more than 100, subscribe plan for unlimited characters."
            context = {
                'objPlans': objPlans,
                'messages': messages
            }
            return render(request, 'views/index.html', context)
        results = generateQuestion(text, "0")  # 0 = Free
        context = {
            'objPlans': objPlans,
            'results': results,
        }
        return render(request, 'views/index.html', context)


@unauthenticated_Creator
def signIn(request):
    if request.method == 'GET':
        return render(request, 'views/signIn.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('creatorPage')
        else:
            messages = 'Username OR password is incorrect.'
            context = {'messages': messages}
            return render(request, 'views/signIn.html', context)


@unauthenticated_Creator
def signUp(request):
    objPlans = Plan.objects.all()

    if request.method == 'GET':
        context = {
            'objPlans': objPlans,
        }
        return render(request, 'views/signUp.html', context)
    elif request.method == 'POST':
        # Auth
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        if password != cpassword:
            message = 'Password mismatch'
            context = {
                'objPlans': objPlans,
                'message': message
            }
            return render(request, 'views/signUp.html', context)

        if len(password) < 8:
            message = 'Password length must be more than 8 characters'
            context = {
                'objPlans': objPlans,
                'message': message
            }
            return render(request, 'views/signUp.html', context)

        if User.objects.filter(username=username).exists():
            message = 'Username already taken'
            context = {
                'objPlans': objPlans,
                'message': message
            }
            return render(request, 'views/signUp.html', context)

        user = User.objects.create_user(
            username, email, password)
        user.save()

        group = Group.objects.get(name='Creator')
        group.user_set.add(user)

        print("USER:", user)

        # Personal Details
        name = request.POST.get('name')
        age = request.POST.get('age')
        occupation = request.POST.get('occupation')
        planId = request.POST.get('plan')
        objPlan = Plan.objects.get(id=planId)

        objCreator = Creator.objects.create(
            creatorUsername=username,
            creatorName=name,
            creatorAge=age,
            creatorOccupation=occupation,
            planName=objPlan
        )
        objCreator.save()
        user = authenticate(
            username=username,
            password=password)
        login(request, user)
        return redirect('confirmation')


@login_required(login_url='signIn')
@allowed_Creator(allowed_roles=['Creator'])
def confirmation(request):
    userName = request.user.username
    userEmail = request.user.email
    objCreator = Creator.objects.get(creatorUsername=userName)
    objPlan = Plan.objects.get(id=str(objCreator.planName))
    context = {
        'userName': userName,
        'userEmail': userEmail,
        'objCreator': objCreator,
        'objPlan': objPlan
    }
    return render(request, 'views/confirmation.html', context)


@login_required(login_url='signIn')
@allowed_Creator(allowed_roles=['Creator'])
def deleteCreator(request):
    userName = request.user.username
    objCreator = Creator.objects.get(creatorUsername=userName)
    if objCreator is not None:
        objCreator.delete()
        user = User.objects.filter(username=userName)
        user.delete()
        logout(request)
        print(userName, "has been deleted.")
    return redirect('signUp')


@login_required(login_url='signIn')
@allowed_Creator(allowed_roles=['Creator'])
def creatorPage(request):
    userName = request.user.username
    objCreator = Creator.objects.get(creatorUsername=userName)
    objPlan = Plan.objects.get(id=str(objCreator.planName))
    name = str(objCreator.creatorName).split()[0]
    planName = objPlan.planName

    if request.method == 'POST':
        text = request.POST.get('text')
        # 1 = Standard; 2 = Premium
        results = generateQuestion(text, objPlan.planStatus)
        context = {
            'userName': userName,
            'objCreator': objCreator,
            'objPlan': objPlan,
            'name': name,
            'planName': planName,
            'results': results,
            'plan': objPlan.planStatus
        }
        return render(request, 'views/creatorPage.html', context)

    context = {
        'userName': userName,
        'objCreator': objCreator,
        'objPlan': objPlan,
        'name': name,
        'planName': planName
    }
    return render(request, 'views/creatorPage.html', context)


def signOut(request):
    logout(request)
    return redirect('index')
