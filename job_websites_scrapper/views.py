from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
import requests
import bs4
import threading
import pprint

from job_sites.models import JobSite, Crawler, JOB_FIELDS, JobData, Qualification, Attribute

def job_sites(request):
	job_sites = JobSite.objects.all()
	return render(request, "main/job-sites.html", {'job_sites': job_sites})


def add_job_site(request):
	# Check if data is from a Form
	if request.method == 'POST':
		# Create JOB SITE
		new_site = JobSite(name=request.POST['name'], link=request.POST['link'], tag=request.POST['tag'])
		new_site.save() 
		# redirect to job-sites
		return redirect('job-sites')
	else:
		# If data is not from a form return the add site form view
		return render(request, "main/add-job-site.html")


def job_site(request, slug, site_id):
	# Get site data
	job_site = JobSite.objects.get(id=int(site_id))
	return render(request, "main/job-site.html", {"job_site": job_site, "job_fields": JOB_FIELDS})


def edit_job_site(request, slug, site_id):
	# Get site data
	job_site = JobSite.objects.get(id=int(site_id))
	# Check if data is from a POST form
	if request.method == 'POST':
		# Update Job Site
		job_site.name = request.POST['name'] 
		job_site.link = request.POST['link']
		job_site.tag = request.POST['tag']
		job_site.save()
		# Redirect to job site
		return redirect('job-site', slug, site_id)
	else:
		# If data is not from a form return edit site view
		return render(request, "main/add-job-site.html", {"job_site": job_site, 'state': 'EDIT'})


def edit_job_crawler(request, slug, site_id):
	# Get site data
	job_site = JobSite.objects.get(id=int(site_id))
	# Check if request is from a POST Form
	if request.method == 'POST':
		# job_site, sub_link, tag, job_field
		for name, option in JOB_FIELDS:
			field = name+'-job_field'
			tag = name+'-tag'
			crawler_id = name+'-id'
			# Check if its an create or update OBJECT
			if request.POST.get(crawler_id, 0) not in [0, '', ' ']:
				# Update OBJECT
				crawler = Crawler.objects.get(id=int(request.POST.get(crawler_id)))
				crawler.tag=request.POST[tag]
				crawler.save()
				# except ObjectDoesNotExist:
			else:
				# Create Object
				crawler = Crawler(job_site=job_site, sub_link=request.POST['sub_link'], tag=request.POST[tag], 
					job_field=request.POST[field])
				crawler.save()
		# Redirect to job-site
		return redirect('job-site', slug, site_id)
	else:
		# If data is not from a form, return the data crawler form view  
		return render(request, "main/edit-job-crawler.html", {"job_site": job_site, "job_fields": JOB_FIELDS})


def job(request, slug, job_id):
	# Get job data
	job_profile = JobData.objects.get(id=int(job_id))
	return render(request, "main/job.html", {'job_profile': job_profile})


def scrap_job_site(request, slug, site_id):
	# Get site data
	job_site = JobSite.objects.get(id=int(site_id))
	# Check if job detail tags Exists
	if job_site.crawlers().count() > 0:
		# Request HTML data
		res = requests.get(job_site.link)
		# Check if request was successful
		if res.status_code == 200:
			# Extract job detail links if request is successful 
			jobSoup = bs4.BeautifulSoup(res.text)
			link_tags = jobSoup.select(job_site.tag)
			for link_tag in link_tags:
				link = link_tag.attrs['href']
				src = ''
				# check if link is relative or absolute
				if not link.startswith('http'):
					# If relative join it with the main link
					protocol = 'https://'
					domain = job_site.link_domain()
					src = protocol+domain+link
				else:
					src =  link
				# Request job detail HTML site data
				res1 = requests.get(src)
				# Check if request was successful
				if res1.status_code == 200:
					# Extract job data if request is successful
					crawl_page(job_site, res1, src)
					#job_thread = threading.Thread(target=crawl_page, args=(job_site, res1, src))
					#job_thread.start()

			return redirect('job-site', slug, site_id)
		else:
			return HttpResponse("Error Accessing Site.")
	else:
		return HttpResponse("Add Job Details Tag to scrap data")	


def crawl_page(job_site, res1, url):
	jobDetailSoup = bs4.BeautifulSoup(res1.text)
	job_data = {}
	for crawler in job_site.crawlers():
		data = jobDetailSoup.select(crawler.tag)
		if len(data)>0:
			if crawler.job_field in ['attribute', 'qualification']:
				keywords = []
				for keyword in data:
					keywords += [keyword.getText()]
				job_data.setdefault(crawler.job_field, keywords)
			else:
				job_data.setdefault(crawler.job_field, data[0].getText())
		else:
			job_data.setdefault(crawler.job_field, 'NULL')

	pprint.pprint(job_data)
	print("\n")

	# Create JobData 
	job = JobData(job_site=job_site, name=job_data['name'], experience=job_data['experience'], 
		description=job_data['description'], organization=job_data['organization'], 
		address=job_data['address'], status='NOT_APPLIED', deadline=job_data['deadline'], link=url)
	job.save()

	# Create Qualification
	if job_data['qualification'] != 'NULL':
		for key in job_data['qualification']:
			qualificaton = Qualification(job=job, name=key) 
			qualificaton.save()

	# Create Attribute
	if job_data['attribute'] != 'NULL':
		for key in job_data['attribute']:
			attribute = Attribute(job=job, name=key)
			attribute.save()

