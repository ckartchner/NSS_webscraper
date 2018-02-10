import csv
import re
import xml.dom.minidom
from xml.dom.minidom import parseString
from pygeocoder import Geocoder
import time

'''
Takes in cvs file with one row containing confirmed coordinates
Requires manual editing of the column names, coordinate column, input fname and output fname

This current version also requires manually adding my "US_standard_kml_header.txt" 
to the beginning of the file after creation.

NOT REALLY FOR REGIONS!!!!
'''

def createPlacemark(kmlDoc, row):
    # This creates a  element for a row of data.
    # A row is a dict.
    # print "row:"
    # for item in row: print item,
    placemarkElement = kmlDoc.createElement('Placemark')
    #Add style note to each element. REMEMBER to add style header!
    styleElement = kmlDoc.createElement('styleUrl')
    placemarkElement.appendChild(styleElement)
    styleElement.appendChild(kmlDoc.createTextNode('#myDefaultStyles')) 
    
    nameElement = kmlDoc.createElement('name')  
    placemarkElement.appendChild(nameElement)
    nameElement.appendChild(kmlDoc.createTextNode(row[0]))
    
    extElement = kmlDoc.createElement('ExtendedData')
    placemarkElement.appendChild(extElement)
    print '\n'+row[0]
    #categories
    cats = ['Cave Name', 'County', 'Topographic Map', 'State', 'Coordinates']
    m = re.match('^(\d\d)(\d\d)(\d\d).(\d\d\d)(\d\d)(\d\d)(.)$', row[-1])
    #convert from dms to decimal degrees. No accounting for NAD27 to WGS84
    north = int(m.group(1))+(int(m.group(2))/60.0)+(int(m.group(3))/3600.0)
    west  = int(m.group(4))+(int(m.group(5))/60.0)+(int(m.group(6))/3600.0)
    if m.group(7) == 'W':
        coordinates = '-'+str(west)+','+str(north)
    elif m.group(7) == 'E':
        coordinates = str(west)+','+str(north)
    else:
        print 'ERROR!'
    i=0  
    while i<len(cats):
        dataElement = kmlDoc.createElement('Data')
        dataElement.setAttribute('name', cats[i] )
        valueElement = kmlDoc.createElement('value')
        dataElement.appendChild(valueElement)
        print "Element in while:", row[i]
        valueText = kmlDoc.createTextNode(row[i])
        valueElement.appendChild(valueText)
        extElement.appendChild(dataElement)
        i+=1

    pointElement = kmlDoc.createElement('Point')
    placemarkElement.appendChild(pointElement)
    coorElement = kmlDoc.createElement('coordinates')
    #Change column the coords are in here
    coorElement.appendChild(kmlDoc.createTextNode(coordinates))
    pointElement.appendChild(coorElement)
    return placemarkElement
    
def createKML(csvReader, fileName):
    # This constructs the KML document from the CSV file.
    kmlDoc = xml.dom.minidom.Document()
    kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2', 'kml')
    kmlElement.setAttribute('xmlns','http://earth.google.com/kml/2.2')
    kmlElement = kmlDoc.appendChild(kmlElement)
    documentElement = kmlDoc.createElement('Document')
    documentElement = kmlElement.appendChild(documentElement)    
    for row in csvReader:
        # skip lines with that don't have well formated coordinates!
        # some lines report "unknown" for coordinates. These lines are skipped.
        if (re.match('^(\d\d)(\d\d)(\d\d).(\d\d\d)(\d\d)(\d\d).$', row[-1])):
            placemarkElement = createPlacemark(kmlDoc, row)
            documentElement.appendChild(placemarkElement)
    kmlFile = open(fileName, 'w')
    kmlFile.write(kmlDoc.toprettyxml('  ', newl = '\n', encoding = 'utf-8'))

def main():
    csvReader = csv.reader(open('NSSRegions_wCords.csv', 'r'), delimiter=';')
    kml = createKML(csvReader, 'NSSRegions.kml')
    
if __name__ == '__main__':
    main()