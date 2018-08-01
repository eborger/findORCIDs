# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 12:05:18 2018

@author: eb427
"""

import requests, json
from xml.etree import ElementTree
import os, sys
import csv, pickle

##Search by "University of St Andrews"
url = 'https://pub.orcid.org/v2.1/search/?q=affiliation-org-name:"University+of+St+Andrews"&start=401&rows=200'
response = requests.get(url)
results = ElementTree.fromstring(response.text)

## Search by "University of Saint Andrews"
url = 'https://pub.orcid.org/v2.1/search/?q=affiliation-org-name:"University+of+Saint+Andrews"&start=1&rows=200'
response = requests.get(url)
results = ElementTree.fromstring(response.text)

with open('ORCIDsearch-SAINT.txt', 'w', encoding='utf-8') as f:
    f.write(ElementTree.tostring(results).decode("utf-8"))
    
## Sarch by Ringgold ID 7486
url = 'https://pub.orcid.org/v2.1/search/?q=ringgold-org-id:7486&start=1&rows=200'
response = requests.get(url)
results = ElementTree.fromstring(response.text)

with open('ORCIDsearch-RG.txt', 'w', encoding='utf-8') as f:
    f.write(ElementTree.tostring(results).decode("utf-8"))
    

##Search by email (typically not public), uncomment if needed    
#url = 'https://pub.orcid.org/v2.1/search/?q=email:*@st-andrews.ac.uk&start=1&rows=200'
#response = requests.get(url)
#results = ElementTree.fromstring(response.text)
#
#with open('ORCIDsearch-email.txt', 'w', encoding='utf-8') as f:
#    f.write(ElementTree.tostring(results).decode("utf-8"))


##Functions to combine individual files downloaded after keyword search:
def getfiles(path):
    '''generates a list of full paths for all txt files.'''
    files = []
    for filename in os.listdir(path):
        if filename.endswith('.txt'):
            filepath = os.path.join(path, filename)
            files.append(filepath)
    return files
            
def combine_xml_files(files):
    '''Takes a list of filepaths and combines the xml content from all xml files.'''
    first = None            
    for filename in files:
        data = ElementTree.parse(filename).getroot()
        if first is None:
            first = data
        else:
            first.extend(data)
    if first is not None:
        return first #ElementTree.tostring(first).decode("utf-8") for printing to console

##load the xml data into one element
path = r'C:\Users\eb427\Documents\ORCID\ORCID-APIsearch\20180711'
files = getfiles(path)
output = combine_xml_files(files) # yields 1877 ORCID iDs

#extract ORCID iDs from the output
orcids = []
for result in output.findall('{http://www.orcid.org/ns/search}result'):
    for identifier in result.findall('{http://www.orcid.org/ns/common}orcid-identifier'):
        for orcid in identifier.findall('{http://www.orcid.org/ns/common}path'):
            orcids.append(orcid.text)

#write ORCID iDs to file
#  NOTE: these are ONLY the ORCID iDs, not associated with names!
with open('UStA_orcids.txt', 'w') as f:
    for row in orcids:
        f.write(row)
        f.write(',')

## Match ORCID iDs with names from info in the ORCID registry using API search.
def match_names(orcid_ids):
    ''' 
    takes a list of ORCID iDs to search the ORCID Public API and returns a dictionary of {"ORCID iD" : "name"}
    '''
    orcids_names = {}      
    for i in orcids:
        url = 'https://pub.orcid.org/v2.1/%s/person' %i
        response = requests.get(url)
        result = ElementTree.fromstring(response.text)
        try:
            if result.find(".//{http://www.orcid.org/ns/personal-details}given-names") != None:
                firstname = result.find(".//{http://www.orcid.org/ns/personal-details}given-names").text
                lastname = result.find(".//{http://www.orcid.org/ns/personal-details}family-name").text
                orcids_names[i] = {}
                orcids_names[i]["firstname"] = firstname
                orcids_names[i]["lastname"] = lastname
        except:
            orcids_names[i] = ""
    #return orcids_names
    export_csv(orcids_names) 

#my orcid https://orcid.org/0000-0003-4965-2969
#test_ids = {}
#url = 'https://pub.orcid.org/v2.1/0000-0003-2705-3105/person'
#response = requests.get(url)
#result = ElementTree.fromstring(response.text)
#firstname = result.find(".//{http://www.orcid.org/ns/personal-details}given-names").text
#lastname = result.find(".//{http://www.orcid.org/ns/personal-details}family-name").text
#test_ids["0000-0003-2705-3105"] = {}
#test_ids["0000-0003-2705-3105"]["firstname"] = firstname
#test_ids["0000-0003-2705-3105"]["lastname"] = lastname
#In [139]: orcids_names
#Out[139]: {'0000-0003-4965-2969': 'Eva Borger'}

def export_csv(my_dict):
    with open('ORCIDs_names.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['ORCID_iD', 'name', 'lastname']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        data = [dict(zip(fieldnames, [k, v])) for k, v in oricds_names.items()]
        writer.writerows(data)

#Backup: export the dictionary to a pickle file which can be loaded again:
with open('ORCIDs_names.pkl', 'wb') as f:
    pickle.dump(orcids_names, f, pickle.HIGHEST_PROTOCOL)
#load backup for further investigation:
with open("ORCIDs_names.pkl", "rb") as f:
    oricds_names = pickle.load(f)