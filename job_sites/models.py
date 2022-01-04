from django.db import models

# Create your models here.
from urllib.parse import urlparse

class JobSite(models.Model):
	name = models.CharField('Site Name', max_length=200)
	link = models.URLField('Site Link')
	tag = models.CharField('Selector Tag', max_length=500)
	date_created = models.DateTimeField('Date Created', auto_now_add=True)
	# name, link, tag

	def crawlers(self):
		return Crawler.objects.filter(job_site=self.id)

	def job_data(self):
		return JobData.objects.filter(job_site=self.id)


	def job_data_count(self):
		jobs = JobData.objects.filter(job_site=self.id)
		return jobs.count()


	def link_domain(self):
		url = self.link
		return urlparse(url).netloc

JOB_FIELDS = (
	('name', 'name'),
	('experience', 'experience'),
	('description', 'description'),
	('organization', 'organization'),
	('address', 'address'),
	('qualification', 'qualification'),
	('attribute', 'attribute'),
	('deadline', 'deadline'),
)


class Crawler(models.Model):
	job_site = models.ForeignKey(JobSite, on_delete=models.CASCADE)
	sub_link = models.URLField('Sub Link', max_length=1000)
	tag = models.CharField('Selector Tag', max_length=500)
	job_field = models.CharField('Job Field', max_length=50, choices=JOB_FIELDS)
	date_created = models.DateTimeField('Date Created', auto_now_add=True)
	# job_site, sub_link, tag, job_field


class JobData(models.Model):
	job_site = models.ForeignKey(JobSite, on_delete=models.CASCADE)
	name = models.CharField('Name', max_length=200)
	experience = models.CharField('Experience', max_length=200)
	description = models.TextField('Description', null=True)
	organization = models.CharField('Organization', max_length=200)
	address = models.TextField('Address')
	status = models.CharField('Status', max_length=200)
	deadline = models.CharField('Deadline', max_length=200)
	link = models.CharField('Link', max_length=1000, null=True)
	date_created = models.DateTimeField('Date Created', auto_now_add=True)
	# job_site, name, experience, description, organization, address, status, deadline, link

	def qualifications(self):
		return Qualification.objects.filter(job=self.id)

	def attributes(self):
		return Attribute.objects.filter(job=self.id)


class Qualification(models.Model):
	job = models.ForeignKey(JobData, on_delete=models.CASCADE)
	name = models.CharField('Qualification', max_length=500)
	date_created = models.DateTimeField('Date Created', auto_now_add=True)
	# job, name


class Attribute(models.Model):
	job = models.ForeignKey(JobData, on_delete=models.CASCADE)
	name = models.CharField('Attribute', max_length=500)
	date_created = models.DateTimeField('Date Created', auto_now_add=True)
	# job, name

