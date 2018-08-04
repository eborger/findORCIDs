#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 09:20:42 2018
@author: eva borger
"""

##Functions to combine individual xml files downloaded after keyword search. Required if multiple search results are to be combined
def getfiles(path):
    '''generates a list of full paths for all txt files in the path.
    Useful for combining '''
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
path = r'[patj]'
files = getfiles(path)
output = combine_xml_files(files)

#Backup: export the dictionary to a pickle file which can be loaded again:
with open('ORCIDs_names.pkl', 'wb') as f:
    pickle.dump(orcids_names, f, pickle.HIGHEST_PROTOCOL)
#load backup for further investigation:
with open("ORCIDs_names.pkl", "rb") as f:
    oricds_names = pickle.load(f)

