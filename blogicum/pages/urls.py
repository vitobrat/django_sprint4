from django.urls import path
from django.views.generic import TemplateView

app_name = 'pages'

TV = TemplateView
urlpatterns = [
    path('rules/', TV.as_view(template_name='pages/rules.html'), name='rules'),
    path('about/', TV.as_view(template_name='pages/about.html'), name='about')
]
