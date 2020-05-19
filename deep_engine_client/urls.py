"""deep_engine_client URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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

from deep_engine_client import view
from django.urls import path, include

BASE_URL = r'covid19/'
PREDICTION_BASE_URL = r'prediction/'
SEARCH_BASE_URL = r'search/'

urlpatterns = [
    path(r'', view.tempRoot),
    path(BASE_URL, include([
        path(r'', view.index),
        path(r'admin/', admin.site.urls),
        path(PREDICTION_BASE_URL, include([
            path(r'', view.predictIndex, name="prediction"),
            path(r'prediction/ligand/smiles', view.inputSmilesOrNames, name="inputSmilesOrNames"),
            # path(r'prediction/file', view.uploadFile, name="uploadFile"),
            path(r'prediction/structure/pdbFile', view.uploadFile, name="pdbFile"),
            path(r'prediction/structure/smiles', view.inputStructureSmiles, name="structureSmilesForm")
            ])
        )
        ])
    )
]
