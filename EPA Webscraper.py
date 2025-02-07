#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Created on Thu Jul 25 10:32:48 2024
Last Update: 7/25/2024

@author: liamthompson

Application: Downloads all links from EPA RadNet

Contact: 
    email: liam.c.thompson-1@ou.edu
"""

# Import Libraries 
import os 
import requests
from bs4 import BeautifulSoup # Web scraping library with documentation found online
import zipfile 
from io import BytesIO

# url = "https://www.epa.gov/radnet/radnet-csv-file-downloads" # Uncomment this line of code. Commenting prevents downloads when working in File.
output_folder =  '' # set save dir
os.makedirs(output_folder, exist_ok = True)

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.content, "html.parser")

links = soup.find_all("a", href = True)
zip_links = [link['href'] for link in links if link['href'].endswith('.zip')] # Files on website are zip. 

# Years of interest 
years_of_interest = ['2021', '2022', '2023'] # add or remove years as seen fit

# Download and extract each ZIP file
for link in zip_links:
    zip_url = link if link.startswith('http') else f'https://www.epa.gov{link}'
    zip_name = os.path.join(output_folder, zip_url.split('/')[-1])
    
    print(f'Downloading {zip_url} to {zip_name}')
    
    zip_response = requests.get(zip_url)
    zip_response.raise_for_status()
    
    # Extract the ZIP file contents
    with zipfile.ZipFile(BytesIO(zip_response.content)) as zip_ref:
        for file_info in zip_ref.infolist():
            if any(year in file_info.filename for year in years_of_interest):
                print(f'Extracting {file_info.filename}')
                zip_ref.extract(file_info, output_folder)

print('Download and extraction completed!') # End of Program 

