from django.contrib import admin
from django.urls import path
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    #------------------------Tareas sin completar--------------------------------------------
    path('tasks/', views.tasks, name='tasks'),
    path('tasks_last/', views.tasks_last, name='tasks_last'),
    path('tasks_recent/', views.tasks_recent, name='tasks_recent'),
    path('tasks_important/', views.tasks_important, name='tasks_important_completed'),
    #------------------------Tareas completadas--------------------------------------------
    path('tasks_completed/', views.tasks_completed, name='tasks_completed'),
    path('tasks_last_completed/', views.tasks_last_completed, name='tasks_last'),
    path('tasks_recent_completed/', views.tasks_recent_completed, name='tasks_recen_completedt'),
    path('tasks_important_completed/', views.tasks_important_completed, name='tasks_important_completed'),
    #-----------------------------------------------------------------------------------------
    path('stats/', views.stats, name='stats'),
    path('stats/data/', views.stats_data, name='stats_data'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/complete', views.complete_task, name='complete_task'),
    path('tasks/<int:task_id>/delete', views.delete_task, name='delete_task'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
]
