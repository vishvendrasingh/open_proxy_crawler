#################################################################################
# Author:Vishvendra Singh														#
# Date: 27-03-2018																#
# https://www.proxydocker.com/en/proxylist/city/								#								#
#################################################################################

#!/usr/bin/python
import requests
import time
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from datetime import datetime
import ssl
import random
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime	.text import MIMEText
import urllib3
import hashlib
from urlparse import urlparse
import json
import re
import urllib2, socket

socket.setdefaulttimeout(180)

urllib3.disable_warnings()
es = Elasticsearch()
datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M")
datetime_file = datetime.now().strftime("%Y-%m-%d_%H-%M")
filename='./log/proxyengine_'+datetime_file+'.log'

class getClass():
	def __init__(self):
		###START SETTINGS###
		self.Flag=1
		self.Retry=3
		self.city=""
		###END SETTINGS###
		with open(filename, 'a') as f:
			f.write(datetime_str+"  ---Starting--- \n")
			f.write(datetime_str+"  Flag - "+str(self.Flag)+" \n")
			f.write(datetime_str+"  Retry - "+str(self.Retry)+" \n")
			f.write(datetime_str+"  LogFile - "+filename+" \n")
		
	def requestSend(self,url):
		rand1=random.randint(1, 30)
		rand2=random.randint(1, 30)
		user_agent = {'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.14'+str(rand1)+'.90 Safari/537.'+str(rand2)+''}
		for j in range(1,self.Retry+1):
			try:
				reqv=requests.get(url, headers = user_agent)
				break
			except:
				with open(filename, 'a') as f:
					f.write(datetime_str+"  "+url+"  - Request Failed Retry..."+str(j)+" \n")
				if self.Retry==j:
					with open(filename, 'a') as f:
						f.write(datetime_str+"  "+url+" - Retry Failed Skipping \n")
					return
		return reqv
	def requestPost(self, url, params, data):
		rand1=random.randint(1, 30)
		rand2=random.randint(1, 30)
		user_agent = {'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.14'+str(rand1)+'.90 Safari/537.'+str(rand2)+''}
		for j in range(1,self.Retry+1):
			try:
				reqv = requests.post(url, params = params, json = data, headers = user_agent)
				break
			except:
				with open(filename, 'a') as f:
					f.write(datetime_str+"  "+url+"  - Request Failed Retry..."+str(j)+" \n")
				if self.Retry==j:
					with open(filename, 'a') as f:
						f.write(datetime_str+"  "+url+" - Retry Failed Skipping \n")
					return
		return reqv
	###START request the page FUNCTION###
	def get(self):
		proxyList= []
		url="https://www.proxydocker.com/en/proxylist/city/Bangalore"
		data = {"eventType": "AAS_PORTAL_START", "data": {"page": "2"}}
		params = {"page": "2"}

		reqv=self.requestPost(url, params, data)
		reqtextv=reqv.text
		soup = BeautifulSoup(reqtextv,"lxml")
		pagesHtml =  soup.select(".my_title")[0].find("span").text;
		pagesHtml = " ".join(pagesHtml.split())
		matchObj = re.match( r'(.*)/(.[0-9])', pagesHtml, re.M|re.I|re.U)
		reach = int(matchObj.group(2));
		with open(filename, 'a') as f:
			f.write(datetime_str+"  Total pages - "+str(reach+1)+" \n")##log
		if matchObj:
			### for first page ####
			params = {"page": "1"}
			# print i;
			soup = BeautifulSoup(reqtextv, 'html.parser')
			with open(filename, 'a') as f:
				f.write(datetime_str+" page - 1\n")##log
			reqv=self.requestPost(url, params, data)
			reqtextv=reqv.text
			soup = BeautifulSoup(reqtextv,"lxml")
			firstline = True
			for z1 in soup.select(".proxylist_table")[0].find_all("tr"):
				if firstline:    #skip first line
					firstline = False
					continue
				list = z1.find_all("td")
				try:
					# print list[0].text.strip();
					if list[0].text.strip() != "":
						proxyList.append(list[0].text.strip());
				except:
					print ""
					# print list.strip()
			### for first page ####

			### for rest of the pages ###
			for i in range(2,reach+1):
				params = {"page": i}
				# print i;
				with open(filename, 'a') as f:
					f.write(datetime_str+" pages - "+str(i)+" \n")##log
				soup = BeautifulSoup(reqtextv, 'html.parser')
				reqv=self.requestPost(url, params, data)
				reqtextv=reqv.text
				soup = BeautifulSoup(reqtextv,"lxml")
				firstline = True
				for z1 in soup.select(".proxylist_table")[0].find_all("tr"):
					if firstline:    #skip first line
						firstline = False
						continue
					list = z1.find_all("td")
					try:
						# print list[0].text.strip();
						if list[0].text.strip() != "":
							proxyList.append(list[0].text.strip());
							with open(filename, 'a') as f:
								f.write(datetime_str+"  Proxy - "+list[0].text.strip()+" \n")##log
					except:
						print ""
						# print list.strip()
			### for rest of the pages ###
		return proxyList
	###END request the page FUNCTION###
	def is_bad_proxy(self,pip):    
	    try:        
	        proxy_handler = urllib2.ProxyHandler({'http': pip})        
	        opener = urllib2.build_opener(proxy_handler)
	        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	        urllib2.install_opener(opener)        
	        req=urllib2.Request('http://www.google.com')  # change the url address here
	        sock=urllib2.urlopen(req)
	    except urllib2.HTTPError, e:        
	        print 'Error code: ', e.code
	        return e.code
	    except Exception, detail:

	        print "ERROR:", detail
	        return 1
	    return 0
####CLASS END####

getObj=getClass()
proxyList = getObj.get()
# print proxyList;exit()
for item in proxyList:
	if getObj.is_bad_proxy(item):
		print "Bad Proxy", item
	else:
		print item, "is working"
		with open(filename, 'a') as f:
			f.write(datetime_str+" Working Proxy - "+item+" \n")##log
