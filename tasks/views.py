from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required 
from django.db import IntegrityError 
from .forms import TaskForm, StatsFilterForm
from django.http import JsonResponse
from django.db.models.functions import TruncDate
from django.db.models import Count
from .models import Task
from django.utils import timezone
from django.db.models import Q
import datetime

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            #register user
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': 'El nombre de usuario ya existe'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm(),
            'error': 'Las contraseñas no coinciden'
        })

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {'form': TaskForm()})
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm(),
                'error': 'Por favor proporciona datos válidos'
            })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task,
                'form': form,
                'error': 'Por favor proporciona datos válidos'
            })  

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm(),
                'error': 'El nombre de usuario o la contraseña son incorrectos'
            })
        else:
            login(request, user)
            return redirect('tasks')

@login_required
def tasks(request):
    today = timezone.now().date()
    tasks = Task.objects.filter(
        user=request.user,
        datecompleted__isnull=True
    ).filter(Q(scheduled_date__isnull=True) | Q(scheduled_date__lte=today))
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_last(request):
    today = timezone.now().date()
    tasks = Task.objects.filter(
        user=request.user,
        datecompleted__isnull=True
    ).filter(Q(scheduled_date__isnull=True) | Q(scheduled_date__lte=today)).order_by('-id')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_recent(request):
    today = timezone.now().date()
    tasks = Task.objects.filter(
        user=request.user,
        datecompleted__isnull=True
    ).filter(Q(scheduled_date__isnull=True) | Q(scheduled_date__lte=today)).order_by('id')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_important(request):
    today = timezone.now().date()
    tasks = Task.objects.filter(
        important=True,
        user=request.user,
        datecompleted__isnull=True
    ).filter(Q(scheduled_date__isnull=True) | Q(scheduled_date__lte=today)).order_by('id')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user = request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_last_completed(request):
    tasks = Task.objects.filter(user = request.user, datecompleted__isnull=False).order_by('-id')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_recent_completed(request):
    tasks = Task.objects.filter(user = request.user, datecompleted__isnull=False).order_by('id')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_important_completed(request):
    tasks = Task.objects.filter(important=True, user = request.user, datecompleted__isnull=False).order_by('id')
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def stats(request):
    form = StatsFilterForm(request.GET or None)
    completed_qs = Task.objects.filter(user=request.user, datecompleted__isnull=False)
    pending_qs = Task.objects.filter(user=request.user, datecompleted__isnull=True)

    if form.is_valid():
        start = form.cleaned_data.get('start_date')
        end = form.cleaned_data.get('end_date')
        if start:
            completed_qs = completed_qs.filter(datecompleted__date__gte=start)
        if end:
            completed_qs = completed_qs.filter(datecompleted__date__lte=end)

    completed_tasks = completed_qs.count()
    pending_tasks = pending_qs.count()
    total = completed_tasks + pending_tasks
    completion_percentage = int((completed_tasks / total) * 100) if total > 0 else 0

    return render(request, 'stats.html', {
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_percentage': completion_percentage,
        'form': form,
    })


@login_required
def stats_data(request):
    # Return JSON with labels (dates) and data (counts) for completed tasks
    form = StatsFilterForm(request.GET or None)
    # Determine date range (use form or default to last 7 days)
    if form.is_valid():
        start = form.cleaned_data.get('start_date')
        end = form.cleaned_data.get('end_date')
    else:
        start = None
        end = None

    today = timezone.now().date()
    if not end:
        end = today
    if not start:
        start = end - datetime.timedelta(days=6)

    # Build list of dates between start and end inclusive
    num_days = (end - start).days + 1
    labels_dates = [start + datetime.timedelta(days=i) for i in range(num_days)]

    completed_data = []
    created_pending_data = []
    scheduled_data = []

    completed_titles = []
    created_titles = []
    scheduled_titles = []

    for d in labels_dates:
        completed_qs = Task.objects.filter(user=request.user, datecompleted__date=d)
        completed_count = completed_qs.count()
        completed_titles.append(list(completed_qs.values_list('title', flat=True)))

        # Tareas creadas ese día y aún pendientes (no programadas)
        created_qs = Task.objects.filter(user=request.user, created_at__date=d, datecompleted__isnull=True, scheduled_date__isnull=True)
        created_pending_data.append(created_qs.count())
        created_titles.append(list(created_qs.values_list('title', flat=True)))

        # Tareas programadas para esa fecha y aún pendientes
        scheduled_qs = Task.objects.filter(user=request.user, scheduled_date=d, datecompleted__isnull=True)
        scheduled_data.append(scheduled_qs.count())
        scheduled_titles.append(list(scheduled_qs.values_list('title', flat=True)))

        completed_data.append(completed_count)

    labels = [d.isoformat() for d in labels_dates]
    return JsonResponse({
        'labels': labels,
        'completed_data': completed_data,
        'created_pending_data': created_pending_data,
        'scheduled_data': scheduled_data,
        'completed_titles': completed_titles,
        'created_titles': created_titles,
        'scheduled_titles': scheduled_titles,
    })