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

from deep_engine_client import views
from django.urls import path, include
import prediction.dashbroad.lbvs

BASE_URL = r'target_fishing/'
PREDICTION_BASE_URL = r'service/prediction/'
urlpatterns = [
    path(BASE_URL, include([
        path(r'', views.index, name='main'),
        path(PREDICTION_BASE_URL, include('prediction.urls')),
        path(r'dash/', include("django_plotly_dash.urls"))
        ])
    )
]
