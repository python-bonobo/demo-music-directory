""" URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en//topics/http/urls/
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
from django.urls import path, include

import mused.urls
from django_includes.views import include_view

urlpatterns = [
    path('', include(mused.urls)),
    path('admin/', admin.site.urls),
    path('esi/<token>', include_view, kwargs={'via': 'esi'}, name='esi'),

]

urlpatterns += [
    path('hinclude/<token>', include_view, kwargs={'via': 'hinclude'}, name='hinclude')
]
