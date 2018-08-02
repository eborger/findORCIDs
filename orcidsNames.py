# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 12:05:18 2018
@author: eb427, ORCID: https://orcid.org/0000-0003-4965-2969

This module provides functions that can be used to retrieve ORCID iDs and public names from the ORCID registry based on keyword search. 
Serch can be done for affiliation, ringgold ID or email domain.
"""
import requests, csv
from xml.etree import ElementTree
import sys

def searchORCID(searchterm, ringgold = False, email = False):
    '''
    Searches the ORCID registry for ORCID iDs based on the search term entered as string with quoation marks. 
    Maximum response lengths is 200, so search must be done in stages for retrieving more than 200 IDs.
    
    Use a search string such as "University of xxx". 
    If search is done usig ringgold ID, set optional second argument ringold = True. Default is False.
    If search is done by email domain, set optional third argument email = True. Defaul is False.
    
    Prints the total number of ORCID iDs found to the comman line.
    Results are individual ORCID iDs, saved to a csv/text file in the working directory.
    '''
    start = 1
    q = (searchterm, start)
    IDs = []
    
    if ringgold == True:
        url = 'https://pub.orcid.org/v2.1/search/?q=ringgold-org-id:%s&start=%s&rows=200' % q
    elif email == True:
        url = 'https://pub.orcid.org/v2.1/search/?q=email:%s&start=%s&rows=200' % q
    else: 
        url = "https://pub.orcid.org/v2.1/search/?q=affiliation-org-name:%s&start=%s&rows=200" % q
    
    response = requests.get(url)
    results = ElementTree.fromstring(response.text)
    identifiers  = results.findall('{http://www.orcid.org/ns/search}result/{http://www.orcid.org/ns/common}orcid-identifier/{http://www.orcid.org/ns/common}path')
    for identifier in identifiers:
        IDs.append(identifier.text)
    
    #afterthe first iteration, repeat the cycle until the response is no longer of length 200 (all IDs have been fetched)
    while (len(results) == 200):
        start += 200
        q = (searchterm, start)
        url = "https://pub.orcid.org/v2.1/search/?q=affiliation-org-name:%s&start=%s&rows=200" % q
        response = requests.get(url)
        results = ElementTree.fromstring(response.text)
        #extract all ORCID iDs and append them to the IDs list
        identifiers  = results.findall('{http://www.orcid.org/ns/search}result/{http://www.orcid.org/ns/common}orcid-identifier/{http://www.orcid.org/ns/common}path')
        for identifier in identifiers:
            IDs.append(identifier.text)
    
    #write a csv file
    with open('ORICD-IDs.txt', 'w') as f:
        for row in IDs:
            f.write(row)
            f.write(',')
    
    print("Done.", len(IDs), "ORCID iDs found. 'ORCID-IDs.txt' in working directory.")



def export_csv(my_dict):
    '''
    Takes a nested python dictionary and produces a CSV file with ORCID iDs, first and last names.
    '''
    with open('ORCIDs_names.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['ORCID_iD', 'name']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        data = [dict(zip(fieldnames, [k, v])) for k, v in my_dict.items()]
        writer.writerows(data)
    
    print("Done. ORCIDs_names.csv in working directory.")


## Match ORCID iDs with names from info in the ORCID registry using API search.
def match_names(filepath):
    ''' 
    takes a list of ORCID iDs to search the ORCID Public API.
    Returns a dictionary of {"ORCID iD" : "name"} saved in a .csv file
    '''
    
    ##reading the ORCID iD file.
    with open(filepath,"r") as f:
        for line in f:
            orcids = line.strip().split(",")
            
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


if __name__ == '__main__':
    param1 = sys.argv[1]
    if sys.argv[2]:
        param2 = sys.argv[2]
    else: 
        param2 = ""
    
    if sys.argv[3]:
        param3 = sys.argv[3]
    else:
        param3 = ""
    
    searchORCID(param1, param2, param3)
    
    filepath = "ORCID-IDs.txt"
    
    match_names(filepath)
