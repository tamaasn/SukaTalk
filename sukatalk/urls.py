"""
URL configuration for sukatalk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from talk import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login),
    path('account_handler/',views.account_handler),
    path('logout/',views.logout),
    path('send_contact/',views.send_contact),
    path('send_message/',views.send_message),
    path('get_chat/',views.get_chat),
    path('get_list_chat/',views.get_contact_lists),
    path('seen_message/',views.seen_message),
    path('update_profile/',views.update_profile),
    path('delete_chat/',views.delete_chat),
    path('delete_message/',views.delete_message)
]
