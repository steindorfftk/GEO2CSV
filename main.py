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

print('Starting')

#OPTIONS
verbose = False
complete = True
output_name = 'output'

#Input file
paths = os.listdir('input/')

html_path = []

for path in paths:
	if '.html' in path:
		html_path.append(path)

firefox_options = Options()
firefox_options.add_argument('--headless')

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
	return citation

def tissueFinder():
	samplecodes = []
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
	pattern_t = re.compile(r'tissue:(.*?)<br>', re.DOTALL)
	pattern_c = re.compile(r'cell type:(.*?)<br>', re.DOTALL)
	pattern_l = re.compile(r'cell line:(.*?)<br>', re.DOTALL)
	for valor in sample_links:
		sample_path = valor
		sample_html = requests.get(sample_path)
		if sample_html.status_code==200:
			sample_content=sample_html.text
			with open('tmp/sample.html','w',encoding='utf-8') as file:
				file.write(sample_content)					
			with open('tmp/sample.html','r') as texto:
				tdata = {}
				cdata = {}
				ldata = {}
				for line in texto:
					if 'tissue:' in line:
						match = pattern_t.search(line)
						if match:
							result=match.group(1).strip()
							tissues.append(result)
					if 'cell type' in line:
						match = pattern_c.search(line)
						if match:
							result=match.group(1).strip()
							cell_types.append(result)
					if 'cell line' in line:
						match = pattern_l.search(line)
						if match:
							result=match.group(1).strip()
							cell_lines.append(result)
				for value in tissues:
					if value not in tdata.keys():
						tdata[value] = tissues.count(value)
				for value in cell_types:
					if value not in cdata.keys():
						cdata[value] = cell_types.count(value)
				for value in cell_lines:
					if value not in ldata.keys():
						ldata[value] = cell_lines.count(value)
	tissue = ''
	cells = ''
	lines = ''
	for key, value in tdata.items():
		if len(tdata.keys()) > 0:
			keys_list = list(tdata.keys())		
			if key == keys_list[-1]:
				tissue += key + ' (' + str(value) + ')'
			else:
				tissue += key + ' (' + str(value) + ') ' + ' / '		
	for key, value in cdata.items():
		if len(cdata.keys()) > 0:
			keys_list = list(cdata.keys())		
			if key == keys_list[-1]:
				cells += key + ' (' + str(value) + ')'
			else:
				cells += key + ' (' + str(value) + ') ' + ' / '
	for key, value in ldata.items():
		if len(ldata.keys()) > 0:
			keys_list = list(ldata.keys())	
			if key == keys_list[-1]:
				lines += key + ' (' + str(value) + ')'
			else:
				lines += key + ' (' + str(value) + ') ' + ' / '	
	return tissue, cells, lines		
			
		
					

start = time()

#Get accession codes from input file	
codes = []

for page in html_path:
	path = 'input/' + page
	acc = getAccession(path)
	for value in acc:
		codes.append(value)

		
data_for_studies = {}

output_name = 'output/' + output_name + '.csv'

#Parse html pages for accession codes	
n_studies = 0

files = os.listdir('output/')

if output_name[7:] not in files:
	with open(output_name,'w') as texto:
		texto.write('Accession code ; Link ; Citation ; Experiment Type ; Platform ; Organism ; Samples ; SRA ; SRA Link ; Tissue ; Cell type ; Cell line ; Title \n')
else:
	with open(output_name,'r') as texto:
		done_codes = []
		for line in texto:
			if 'Accession code' not in line:
				linha = line.split()
				if len(linha)>0:
					done_codes.append(linha[0])
		codes = [value for value in codes if value not in done_codes]		


#codes = ['GSE48865']
	

with open(output_name,'a') as output:		
	for value in codes:
	#	if n_studies == 20: #Limits the number of experiments parsed
	#		break
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
				data_for_studies[value]['Tissue'], data_for_studies[value]['Cells'], data_for_studies[value]['Lines'] = tissueFinder()
			else:
				data_for_studies[value]['Tissue'] = ''
				data_for_studies[value]['Cells'] = ''
				data_for_studies[value]['Lines'] = ''
			with open('tmp/Page.html','r') as texto:
				data_for_studies[value]['Title'] = getTitle(texto)
			n_studies += 1		
			seconds = time() - start
			tax = (seconds/n_studies*len(codes)) - seconds 
			print('\nDone (' + str(n_studies) + '/' + str(len(codes))+ ') \n---------\n\n')
		else:
			print(f'Failed to download HTML. Status code: {html_page.status_code}')
			output.write(value + ' ; ')
			output.write(geo_path + ' ; ')	
			output.write('Connection error \n')
		output.write(value + ' ; ')
		output.write(geo_path + ' ; ')	
		output.write(data_for_studies[value]['Citation'] + ' ; ')
		output.write(data_for_studies[value]['Experiment_Type'] + ' ; ')
		output.write(data_for_studies[value]['Platform'] + ' ; ')
		output.write(data_for_studies[value]['Organism'] + ' ; ')
		output.write(data_for_studies[value]['Samples'] + ' ; ')
		output.write(data_for_studies[value]['SRA'] + ' ; ')
		output.write(data_for_studies[value]['SRA_link'] + ' ; ')	
		output.write(data_for_studies[value]['Tissue'] + ' ; ' + data_for_studies[value]['Cells'] + ' ; ' + data_for_studies[value]['Lines'] + ' ; ')			
		output.write(data_for_studies[value]['Title'] + '\n')				
		output.flush()	
	
	


	

	
	
	
	
	
	
	
	
