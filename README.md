# Installation
- Download the program files: Click on '<> Code' and then on 'Download ZIP'
- Place the 'GEO-scraper_main.zip' file on the installation directory of your choice.
- Unzip the file (unzip GEO-scraper_main.zip)  
- Install necessary packages: selenium, beutifulsoup4 and requests (pip install package)

# Input File Preparation
- This program is suitable to scrape data from any list of studies found after a Gene Expression Omnibus (GEO) search. The input file must be one or more html files with search results. Prepare the file as following:
-1 - Perform the GEO search with the proper key words or GEO accessions (https://www.ncbi.nlm.nih.gov/geo/) + apply desired filters.
-2 - If the search returns more than 20 results, click on '20 per page' and change the items per page as necessary.
-3 - Right click on the page, select 'Save Page As' and save the page as .html.
-4 - If the search returns more than 500 results you can save more than one page with another name and use it along the first one.


# GEO_scraper Utilization
-1 - Add the GEO search results html files in the input directory (GEO_scraper-main/input)
-2 - In-script configuration: there are 3 variables you can define in-script - verbose, tissue and output_name.
-2.1 - verbose: set to 'True' if you want the terminal to print the information while you are scraping, either else keep on 'False'. This doesn't alter the execution time or the final output.
-2.2 - complete: set to 'True' if you want the program to gather information on Tissue type and Cell type from the studies. This considerably increases the execution time but it's recommended.
-2.3 - output_name: set the desired output file name. The standard name is 'output'.
-3 - Run the main.py file (python3 main.py)
-4 - A .csv file with basic information about these studies will be created in output folder

## This version retrieves the following information: Accession code, GEO link, Study title, Experiment type, platform, organisms, number of samples, SRA availability, SRA link, Tissues, Cell Types and Title
