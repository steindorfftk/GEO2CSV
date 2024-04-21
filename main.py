from bs4 import BeautifulSoup
import requests
from time import time, sleep
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import re 
import argparse
import datetime

def getAccession(file):
	accessionCodes = []
	with open(file,'r') as texto:
		html_doc = texto
		soup = BeautifulSoup(html_doc,'lxml')
		lista = soup.find_all('dd')
		for value in lista:
			if '<dd>GSE' in str(value):
				accessionCodes.append(str(value).replace('<dd>','').replace('</dd>',''))
	return accessionCodes

def experimentTyper(target):
	last_line = False
	experiment = 'Two or more types'
	experiment_types = ['Expression profiling by MPSS','Expression profiling by RT-PCR','Expression profiling by SAGE','Expression profiling by SNP array','Expression profiling by array','Expression profiling by genome tiling array','Expression profiling by high throughput sequencing','Genome binding/occupancy profiling by SNP array','Genome binding/occupancy profiling by array','Genome binding/occupancy profiling by genome tiling array','Genome binding/occupancy profiling by high throughput sequencing','Genome variation profiling by SNP array','Genome variation profiling by array','Genome variation profiling by genome tiling array','Genome variation profiling by high throughput sequencing','Methylation profiling by SNP array','Methylation profiling by array','Methylation profiling by genome tiling array','Methylation profiling by high throughput sequencing','Non-coding RNA profiling by array','Non-coding RNA profiling by genome tiling array','Non-coding RNA profiling by high throughput sequencing','Other','Protein profiling by Mass Spec','Protein profiling by protein array','SNP genotyping by SNP array','Third-party reanalysis']
	experiment_a = []
	for line in target:
		if last_line == True:
			for value in experiment_types:
				if value in line:
					experiment_a.append(value)
			last_line = False		
		if '>Experiment type<' in line:
			last_line = True
	experiment = ''		
	for value in experiment_a:
		if value == experiment_a[-1]:
			experiment += value
		else:
			experiment += value + ' / '
	if verbose == True:
		print('Experiment type: ' + experiment)	
	return experiment

def platformFinder(target):
	platform = ''
	platform_n = ''
	platforms = []
	for line in target:
		if 'GPL' in line:
			linha = line.replace('</a>',' ').replace('</td>',' ').replace('>',' ')
			linha = linha.split()
			platforms.append(linha[-1])
	for value in platforms:
		if value[:3] != 'GPL':
			platforms.remove(value)		
	for value in platforms:
		if value == platforms[-1]:
			platform += value
		else:
			platform += value + ' / '		
	if verbose == True:
		print('Platform: ' + platform)
	return platform
	
def organismFinder(target):
	last_line = False
	organism = ''
	organisms = []
	for line in target:
		if last_line == True:
			line = line.replace(' ','_')
			line = line.replace('">',' ')
			line = line.replace('</a>',' ')
			linha = line.split()
			for value in linha:
				if '<' not in value:
					organisms.append(value.replace('_',' '))
			last_line = False				
		if 'nowrap>Organism</' in line or '>Organisms<' in line:
			last_line = True
	for value in organisms:
		if value == organisms[-1]:
			organism += value
		else:
			organism += value + ' / '		
	if verbose == True:
		print('Organism: ' + organism)
	return organism	


def sampleFinder(target):
	samples = ''
	for line in target:
		if 'Samples (' in line:
			line = line.replace(' ','_').replace('<td>',' ').replace('<div',' ').replace('</td',' ').split()
			for value in line:
				if 'Sample' in value:
					samples = value[9:-1]
	if verbose == True:
		print('Samples: ' + samples)	
	return samples	

def sraChecker(target):
	sra = 'No'
	if 'array' in data_for_studies[value]['Experiment_Type']:
		sra = 'No (Array)'
	for line in target:
		if '/Traces/' in line:
			sra = 'Yes'
	if verbose == True:
		print('SRA: ' + sra)	
	return sra		

def sralinkFinder(target):
	for line in target:
		if '/Traces/' in line:
			line = line.replace(' ','_').replace('href="',' ').replace('">SRA',' ').split()
			for value in line:
				if 'Traces' in value:
					sra_link = 'www.ncbi.nlm.nih.gov' + value	
	return sra_link
	
def getTitle(target):
	last_line = False
	for line in target:
		if last_line == True:
			line = line.replace('<td style="text-align: justify">','').replace('</td>','')
			title = line[:-1]
			last_line = False
		if '>Title' in line:
			last_line = True
	if verbose == True:
		print('Title: ' + title)		
	return title	

def citationFinder():
	driver = webdriver.Firefox(options=firefox_options)
	driver.get(geo_path)
	try:
		element = WebDriverWait(driver, 10).until(
	    	EC.presence_of_element_located((By.CLASS_NAME, "PubmedCitation"))
		)
		authors_text = re.search(r'<span class="authors">(.*?)</span><span', element.get_attribute('outerHTML')).group(1)
		title_text = re.search(r'<span class="title">(.*?)</span><span', element.get_attribute('outerHTML')).group(1)
		source_text = re.search(r'<span class="source">(.*?)PMID:&nbsp', element.get_attribute('outerHTML')).group(1).replace('</span>','').replace(';',',')
		citation = authors_text + ' ' + title_text + ' ' + source_text
		
	except:
		citation = 'Citation missing'
	if verbose == True:
		print('Citation: ' + citation)	
	driver.quit()
	citation = citation.replace(';',',')
	return citation

def sampledetailFinder():
	samplecodes = []
	ppp_tags = 'A'
	tissues = []
	driver = webdriver.Firefox(options=firefox_options)
	driver.get(geo_path)
	page_source = driver.page_source
	lines = page_source.split('\n')
	for line in lines:
		if 'Samples (' in line:
			line = line.replace(' ','_').replace('<td>',' ').replace('<div',' ').replace('</td',' ').split()
			for value in line:
				if 'Sample' in value:
					samples = value[9:-1]		
	if int(samples) > 3:
		for line in lines:
			if 'divhidden' in line and 'display:' in line:
				line = line.replace(' ','_').replace('id="',' ').replace('"_name',' ').split()
				for stuff in line:
					if 'divhidden' in stuff and 'display' not in stuff:
						tag_id = '//*[contains(@id, "{}")]/a'.format(stuff)
		button = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, tag_id)))				
		button.click()
	page_source = driver.page_source
	with open('tmp/selenium.html','w',encoding='utf-8') as file:
		file.write(page_source)
	driver.quit()
	sample_links = []
	with open('tmp/selenium.html','r') as texto:
		for line in texto:
			if 'GSM' in line:
				line = line.replace(' ','_').replace('href="',' ').replace('"_onmouse',' ').split()
				for stuff in line:
					if 'geo/query' in stuff:
						newnewlink = 'https://www.ncbi.nlm.nih.gov' + stuff	
						sample_links.append(newnewlink)
	tissues = []
	cell_types = []
	cell_lines = []
	races = []
	ethnicities = []
	ancestries = []
	ppp_tags = {}
	if len(p_tags) > 0:
		for value in p_tags:
			ppp_tags[value] = {}
			pat = f'{value}:(.*?)<br>'
			patt = re.compile(pat, re.DOTALL)
			ppp_tags[value]['pattern'] = patt
			ppp_tags[value]['data'] = [] 
			ppp_tags[value]['xdata'] = {}
			ppp_tags[value]['string'] = ''
	for valor in sample_links:
		sample_path = valor
		sample_html = requests.get(sample_path)
		if sample_html.status_code==200:
			sample_content=sample_html.text
			with open('tmp/sample.html','w',encoding='utf-8') as file:
				file.write(sample_content)					
			with open('tmp/sample.html','r') as texto:
				for line in texto:
					if len(p_tags) > 0:		
						for value in p_tags:
							if value in line:
								match = ppp_tags[value]['pattern'].search(line)
								if match:
									result=match.group(1).strip()
									ppp_tags[value]['data'].append(result)									
	if len(p_tags) > 0:
		for value in p_tags:
			for valueb in ppp_tags[value]['data']:
				if valueb not in ppp_tags[value]['xdata'].keys():
					ppp_tags[value]['xdata'][valueb] = ppp_tags[value]['data'].count(valueb)
	if len(p_tags) > 0:
		for valor in p_tags:
			for key, value in ppp_tags[valor]['xdata'].items():
				if len(ppp_tags[valor]['xdata'].keys()) > 0:
					keys_list = list(ppp_tags[valor]['xdata'].keys())
					if key == keys_list[-1]:
						ppp_tags[valor]['string'] += key + ' (' + str(value) + ')'
					else:
						ppp_tags[valor]['string'] += key + ' (' + str(value) + ') ' + ' / '
#	if verbose == True:		
	return ppp_tags	

#Get arguments
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true', help='Set verbose to True')
parser.add_argument('-q', '--quick', action='store_true', help='Set complete to False')
parser.add_argument('-o', '--output', type=str, default='output',help='Output file name')
parser.add_argument('-a', '--attributes', type=str, default='',help='Personalized attributes')
args = parser.parse_args()

#Save personalized tags
p_tags = ['cell type','cell line','tissue','genotype','strain','treatment','age','Sex']
c_tags = [value for value in args.attributes.replace('(','|').replace(')','').split('|') if value != '']
for value in c_tags:
	p_tags.append(value.strip())


#Set options
verbose = False
if args.verbose:
	verbose = True
complete = True
if args.quick:
	complete = False
output_name = args.output

#Set input files
paths = os.listdir('input/')
html_path = []
for path in paths:
	if '.html' in path:
		html_path.append(path)

#Set selenium options
firefox_options = Options()
firefox_options.add_argument('--headless')

#Start timer
start = time()

#Get accession codes from input file	
codes = []
for page in html_path:
	path = 'input/' + page
	acc = getAccession(path)
	for value in acc:
		codes.append(value)

#Start data dictionary		
data_for_studies = {}

#Define output path
output_name = 'output/' + output_name + '.csv'

#Parse html pages for accession codes	
n_studies = 0
all_codes = 0

#Initiate output file
files = os.listdir('output/')
pp_tags = ''
for value in p_tags:
	pp_tags += f' ; {value}'

if output_name[7:] not in files:
	if len(p_tags) > 0:
		with open(output_name,'w') as texto:
			texto.write(f'Accession code ; Link ; Citation ; Experiment Type ; Platform ; Organism ; Samples ; SRA ; SRA Link {pp_tags} ; Title \n')
	all_codes = len(codes)
else:
	with open(output_name,'r') as texto:
		done_codes = []
		for line in texto:
			if 'Accession code' not in line:
				linha = line.split()
				if len(linha)>0:
					done_codes.append(linha[0])
		all_codes = len(codes)
		codes = [value for value in codes if value not in done_codes]
		n_studies = len(done_codes)



#codes = ['GSE259276','GSE245108','GSE250469','GSE222009','GSE234729']
	

with open(output_name,'a') as output:		
	for value in codes:
		data_for_studies = {}
		#if n_studies == 20: #Limits the number of experiments parsed
		#	break
		try:
			geo_path = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + value
			html_page = requests.get(geo_path)
			data_for_studies[value] = {}
			data_for_studies[value]['Link'] = geo_path
			if html_page.status_code==200:
				html_content=html_page.text
				print('Parsing ' + value + '... \n')
				with open('tmp/Page.html','w',encoding='utf-8') as file:
					file.write(html_content)
				data_for_studies[value]['Citation'] = citationFinder()	
				with open('tmp/Page.html','r') as texto:
					data_for_studies[value]['Experiment_Type'] =  experimentTyper(texto)
				with open('tmp/Page.html','r') as texto:
					data_for_studies[value]['Platform'] = platformFinder(texto)
				with open('tmp/Page.html','r') as texto:
					data_for_studies[value]['Organism'] = organismFinder(texto)
				with open('tmp/Page.html','r') as texto:
					data_for_studies[value]['Samples'] = sampleFinder(texto)
				with open('tmp/Page.html','r') as texto:
					data_for_studies[value]['SRA'] = sraChecker(texto)
					
				with open('tmp/Page.html','r') as texto:
					if data_for_studies[value]['SRA'] == 'Yes':
						data_for_studies[value]['SRA_link'] = sralinkFinder(texto)
					else:
						data_for_studies[value]['SRA_link'] = 'NA'
				if complete == True: 
					try:
						personalized = sampledetailFinder()
					except UnboundLocalError as e:	
						if os.path.exists('output/error_log.txt'):
							with open('output/error_log.txt','a') as error:
								error.write(f'{value} {datetime.datetime.now()}\n')
								error.write(f'{e}\n')
						else:
							with open('output/error_log.txt','w') as error:
								error.write(f'{value} {datetime.datetime.now()}\n')
								error.write(f'{e}\n')
						print(f'No samples found for {value}')
						personalized = {}
						if len(p_tags) > 0:
							for tag in p_tags:
								personalized[tag]['string'] = ''	
				else:
						personalized = {}
						if len(p_tags) > 0:
							for tag in p_tags:
								personalized[tag]['string'] = ''
				with open('tmp/Page.html','r') as texto:
					data_for_studies[value]['Title'] = getTitle(texto)
				output.write(value + ' ; ')
				output.write(geo_path + ' ; ')	
				output.write(data_for_studies[value]['Citation'] + ' ; ')
				output.write(data_for_studies[value]['Experiment_Type'] + ' ; ')
				output.write(data_for_studies[value]['Platform'] + ' ; ')
				output.write(data_for_studies[value]['Organism'] + ' ; ')
				output.write(data_for_studies[value]['Samples'] + ' ; ')
				output.write(data_for_studies[value]['SRA'] + ' ; ')
				output.write(data_for_studies[value]['SRA_link'] + ' ; ')	
				if len(p_tags) > 0:
					for tag in p_tags:
						output.write(personalized[tag]['string'] + ' ; ')
				output.write(data_for_studies[value]['Title'] + '\n')				
				output.flush()	
				n_studies += 1		
				seconds = time() - start
				tax = (seconds/n_studies*len(codes)) - seconds 
				print('\nDone (' + str(n_studies) + '/' + str(all_codes)+ ') \n---------\n\n')
			else:
				print(f'Failed to download HTML. Status code: {html_page.status_code}')
				error.write(f'{value} {datetime.datetime.now()}\n')
				error.write(f'{html_page.status_code}\n')			
		except Exception as e:
			if os.path.exists('output/error_log.txt'):
				with open('output/error_log.txt','a') as error:
					error.write(f'{value} {datetime.datetime.now()}\n')
					error.write(f'{e}\n')
			else:
				with open('output/error_log.txt','w') as error:
					error.write(f'{value} {datetime.datetime.now()}\n')
					error.write(f'{e}\n')
			print(f'Error for {value}: {e}')
			print('Moving to the next study')
			codes.append(value)
			continue
				
	
	


	

	
	
	
	
	
	
	
	
