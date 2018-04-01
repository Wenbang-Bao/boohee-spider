# -*- coding: utf-8 -*-

import re
import requests
import time
import random
import urllib2
from bs4 import BeautifulSoup as bs


HOME_PAGE = 'http://www.boohee.com'
REQ_HEAD = [{'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'},
			{'User-Agent':'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'},
			{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'},
			{'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]
FOOD_INFO = []
CSV_HEAD = '名称| 热量|类别|碳水化合物(g/100mg)|脂肪(g/100mg)|蛋白质(g/100mg)|纤维素(g/100mg)|维生素A(ug/100mg)|维生素C(g/100mg)|维生素E(mg/100mg)|胡萝卜素(ug/100mg)|硫胺素(mg/100mg)|核黄素(mg/100mg)|烟酸(mg/100mg)|胆固醇(mg/100mg)|镁(mg/100mg)|钙(mg/100mg)|铁(mg/100mg)|锌(mg/100mg)|铜(mg/100mg)|猛(mg/100mg)|钾(mg/100mg)|磷(mg/100mg)|钠(mg/100mg)\n'
CSV_FILE = None

def get_html_content(url):
	try:
		req = urllib2.Request(url, headers=REQ_HEAD[random.randint(0, len(REQ_HEAD)-1)])
		html = urllib2.urlopen(req).read()
		return str(html)
	except(urllib2.HTTPError, urllib2.URLError), e:
		print e

def write_info_in_csv(Food_Info):
	if not Food_Info:
		return
	with open('Food_Info.csv', 'a+')as f:
		if not f.readline():
			f.write(CSV_HEAD)
		for info in Food_Info:
			f.write('|'.join(info).encode('utf-8')+'\n')

def get_food_info(url):
	def _get_nutrition_info(soup):
		nutrs_list = []
		nutr_info = soup.find('div', attrs={'class':'nutr-tag margin10'})
		pattern = re.compile(r'(.*\))')
		if nutr_info:
			nutrs = nutr_info.find_all('dd')
			for item in nutrs:
				nutrs_list.append(pattern.sub('', item.get_text()))
			return nutrs_list[2:-1] #drop the nutrition info header

	res = get_html_content(url)
	soup = bs(res, 'html.parser')
	strs = soup.find('h2', 'crumb').get_text()
	name = strs.split('/')[-1].replace('\n', '').strip()
	category = strs.split('/')[-2].replace('\n', '').strip()
	calory = soup.find('span',id='food-calory').get_text()
	nutr_list = _get_nutrition_info(soup)
	return [name, calory, category] + nutr_list
	
def get_food_url(soup):
	food_url = []
	p = re.compile(r'href="([/\?\=\d\w]+)"')
	res = soup.select('li.item.clearfix')
	for r in res:
		m = re.search(p, r.encode('ascii'))
		if m:
			food_url.append(HOME_PAGE + m.group(1))
	return food_url

def get_next_page(soup):
	p = re.compile(r'href="([/\?\=\d\w]+)"')
	res = soup.select('a.next_page')
	for r in res:
		m = re.search(p, r.encode('ascii'))	
		if m:
			return HOME_PAGE + m.group(1)

	
def download_food_info(url):
	res = get_html_content(url)
	soup = bs(res, 'html.parser')
	next_page = get_next_page(soup)
	food_url = get_food_url(soup)
	if food_url:
		for url in food_url:
			food_info = get_food_info(url)
			time.sleep(random.uniform(0, 4))
			FOOD_INFO.append(food_info)
	if not next_page:
		return FOOD_INFO
	else:
		time.sleep(random.uniform(0, 7))
		write_info_in_csv(FOOD_INFO)
		download_food_info(next_page)

def get_food_types_url(home_page):
	type_url = []
	res = get_html_content(home_page)
	soup = bs(res, 'html.parser')
	href = soup.find('a', text='热量查询').get('href')	
	
	res = get_html_content(home_page+href)
	soup = bs(res, 'html.parser')
	
	food_types = soup.findAll('li', 'col-md-4 col-sm-4 col-xs-12 item')	
	for food in food_types:
		type_url.append(food.find('a').get('href'))
	return type_url


def main():
	get_food_types_url(HOME_PAGE)
	Types_Url = get_food_types_url(HOME_PAGE)
	for type_url in Types_Url:
		print "loading the [%-36s] food information....[START]" %(HOME_PAGE+type_url)
		download_food_info(HOME_PAGE+type_url)
		print "loading the [%-36s] food information....[ DONE]" %(HOME_PAGE+type_url)
	


if __name__ == "__main__":	
	main()
