# Installation
- Download the program files: Click on '<> Code' and then on 'Download ZIP'
- Place the 'GEO-scraper_main.zip' file on the installation directory of your choice.
- Chang into the installation directory and unzip the file (unzip GEO-scraper_main.zip)  
- Install necessary packages: selenium, beutifulsoup4, requests and lxml (pip install package)

# Input File Preparation
- This program is suitable to scrape data from any list of studies found after a Gene Expression Omnibus (GEO) search. The input file must be one or more html files with search results. Prepare the file as following:
- 1 - Perform the GEO search with the proper key words or GEO accessions (https://www.ncbi.nlm.nih.gov/geo/) + apply desired filters.
- 2 - If the search returns more than 20 results, click on '20 per page' and change the items per page as necessary.
- 3 - Right click on the page, select 'Save Page As' and save the page as .html.
- 4 - If the search returns more than 500 results you can save more than one page with another name and use it along the first one.


# GEO_scraper Utilization
- 1 - Add the GEO search results html files in the input directory (GEO_scraper-main/input)
- 2 - Run the main.py file (python3 main.py)
- 3 - A .csv file with basic information about these studies will be created in output folder

## GEO_scraper Options
Currently, there are 4 options you can set when running the script - output name, attributes, verbose and quick-mode.
- output name (-o): Use it to define the output name. Example: '-o My_data' will produce the My_data.csv output file. If not specified, the output file will be named 'output.csv'.
- attributes (-a): allows you to specify additional sample attributes not pre-defined in GEO_scraper. Enclose your list of attributes in double quotes, with each attribute in parenthesis. For example: '-a "(antibody) (mother ethnicity)"'
- verbose (-v): Use it if you want the terminal to print the information while you are scraping. This doesn't alter the execution time or the final output.
- quick-mode (-q): Use it if you want the program to run on quick mode, i.e., gather only basic information (doesnt collect data on Tissue type, Cell type and Race/Ethnicity/Ancestry from the study samples). This considerably reduces the execution time but excludes relevant study information.


## This version retrieves the following information: Accession code, GEO link, Citation, Experiment type, Platform, Organisms, Number of samples, SRA availability, SRA link, Cell Types, Cell Lines, Tissues, Genotypes, Strains, Treatments, Age, Sex and Title. Additionally, it's possible to parse for personalized attributes (check GEO_scraper Options section)
