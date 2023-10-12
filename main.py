from bs4 import BeautifulSoup
import requests

#Input file
html_path = 'input/Data.html'
verbose = False
output_name = 'output/Results.csv'

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

#Get accession codes from input file	
codes = getAccession(html_path)	
data_for_studies = {}

#codes = ['GSE223409']

for code in codes:
	data_for_studies[code] = {}
	

#Parse html pages for accession codes	
n_studies = 0

		
for value in codes:
#	if n_studies == 25:
#		break
	geo_path = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + value
	html_page = requests.get(geo_path)
	data_for_studies[value]['Link'] = geo_path	
	if html_page.status_code==200:
		html_content=html_page.text
		print('Parsing ' + value + '... \n')
		with open('tmp/Page.html','w',encoding='utf-8') as file:
			file.write(html_content)
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
		with open('tmp/Page.html','r') as texto:
			data_for_studies[value]['Title'] = getTitle(texto)	
		n_studies += 1		
		print('\nDone (' + str(n_studies) + '/' + str(len(codes))+ ')\n---------')
	else:
		print(f'Failed to download HTML. Status code: {html_page.status_code}')
	
		
with open(output_name,'w') as texto:
	texto.write('Accession code ; Link ; Title ; Experiment Type ; Platform ; Organism ; Samples ; SRA ; SRA Link \n')
	for key, value in data_for_studies.items():
		if 'Experiment_Type' in value.keys():
			texto.write(key + ' ; ' + value['Link'] + ' ; ' + value['Title'] + ' ; ' + value['Experiment_Type'] + ' ; ' + value['Platform'] + ' ; ' + value['Organism'] + ' ; ' + value['Samples'] + ' ; ' + value['SRA'] + ' ; ' + value['SRA_link'] + '\n')
		
		
	
	
	
	
	
	
	
	
	
	
	
	
	
	
