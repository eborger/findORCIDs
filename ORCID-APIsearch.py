# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 12:05:18 2018

@author: eb427
"""

import requests, json
from xml.etree import ElementTree
import os, sys
import csv, pickle

def searchORCID(searchterm, ringgold = False, email = False):
    '''
    Searches the ORCID registry for ORCID iDs based on the search term entered as string with quoation marks. 
    Maximum response lengths is 200, so search must be done in stages for retrieving more than 200 IDs.
    
    Use a search string such as "University of xxx". 
    If search is done usig ringgold ID, set optional second argument ringold = True. Default is False.
    If search is done by email domain, set optional third argument email = True. Defaul is False.
    
    Results is an xml tree saved to a text will in the working directory.
    '''
    start = 1
    q = (searchterm, start)
    IDs = ElementTree.Element("results")
    
    if ringgold == True:
        url = 'https://pub.orcid.org/v2.1/search/?q=ringgold-org-id:%s&start=%s&rows=200' % q
    elif email == True:
        url = 'https://pub.orcid.org/v2.1/search/?q=email:%s&start=%s&rows=200' % q
    else: 
        url = "https://pub.orcid.org/v2.1/search/?q=affiliation-org-name:%s&start=%s&rows=200" % q
        
    response = requests.get(url)
    results = ElementTree.fromstring(response.text)
    IDs.append(results)
    
    while (len(results) == 200):
        start += 200
        q = (searchterm, start)
        url = "https://pub.orcid.org/v2.1/search/?q=affiliation-org-name:%s&start=%s&rows=200" % q
        response = requests.get(url)
        results = ElementTree.fromstring(response.text)
        IDs.append(results)
    
    # exract ORCIDiDs
    orcids = []
    for result in output.findall('{http://www.orcid.org/ns/search}result'):
        for identifier in result.findall('{http://www.orcid.org/ns/common}orcid-identifier'):
            for orcid in identifier.findall('{http://www.orcid.org/ns/common}path'):
                orcids.append(orcid.text)
            
    with open('ORCID-IDs.txt', 'w', encoding='utf-8') as f:
        f.write(ElementTree.tostring(IDs).decode("utf-8"))
    
    print("Done.")


##Functions to combine individual files downloaded after keyword search:
def getfiles(path):
    '''generates a list of full paths for all txt files in the path.'''
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

def export_csv(my_dict):
    with open('ORCIDs_names.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['ORCID_iD', 'name', 'lastname']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        data = [dict(zip(fieldnames, [k, v])) for k, v in oricds_names.items()]
        writer.writerows(data)


##load the xml data into one element
path = r'C:\Users\eb427\Documents\ORCID\ORCID-APIsearch\20180711'
files = getfiles(path)
output = combine_xml_files(files)

#extract ORCID iDs from the output
#root.findall('{*/{http://www.orcid.org/ns/search}result') to extract from nested result
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
        url = 'https://pub.orcid.org/v2.1/%s/person' % i
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


#Backup: export the dictionary to a pickle file which can be loaded again:
with open('ORCIDs_names.pkl', 'wb') as f:
    pickle.dump(orcids_names, f, pickle.HIGHEST_PROTOCOL)
#load backup for further investigation:
with open("ORCIDs_names.pkl", "rb") as f:
    oricds_names = pickle.load(f)