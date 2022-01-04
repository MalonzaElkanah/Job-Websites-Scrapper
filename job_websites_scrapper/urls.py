from django.urls import path

from . import views

urlpatterns = [
    path('', views.job_sites, name='job-sites'),
    path('add/job-site/', views.add_job_site, name='add-job-site'),
    path('edit/job-site/<slug:slug>/<int:site_id>/', views.edit_job_site, name='edit-job-site'),
    path('job-site/<slug:slug>/<int:site_id>/', views.job_site, name='job-site'),
    path('edit/job-crawler/<slug:slug>/<int:site_id>/', views.edit_job_crawler, name='edit-job-crawler'),
    path('job/<slug:slug>/<int:job_id>/', views.job, name='job'),
    path('scrap/job-site/<slug:slug>/<int:site_id>/', views.scrap_job_site, name='scrap-job-site'),
]
