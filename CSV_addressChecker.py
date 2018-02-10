import csv
import urllib2
from pygeocoder import Geocoder

'''
requires changing the input csv, output csv, which columns are address and name
appends cord and coord quality cols to file

MORE THAN JUST A CHECKER! AN AWESOME!
'''
def main():
    inputcsv = 'D:/Cave Data/North Carolina/NCcounties.csv'
    outputcsv = 'D:/Cave Data/North Carolina/NC_counties_numAndCords.csv'
    csvReader = csv.reader(open(inputcsv, 'r'), delimiter=';')
    # writer = csv.writer(open(outputcsv, 'wb'), delimiter=';', quotechar='', quoting=csv.QUOTE_MINIMAL)
    writer = csv.writer(open(outputcsv, 'wb'), delimiter=';')
    previous = ""
    current = ""
    validList = []
    rowsList = []
    validWebsites = {}
    errorWebsites = {}
    goodAddresses = {}
    errorAddresses = {}
    for row in csvReader:
		if row[2] != 0:
			#Skip first row
			col0value = row[0]
			if col0value == 'Code':
				writer.writerow(row)
			else:
				address = row [1]
				print address, row[2]
				# print col0value
					
				#Check if address is understood by google geolocator
				try:
					result = Geocoder.geocode(address)
				except Exception as error:
					print "\nError with address for:",col0value
					print "Address:",address
					print "Error:", error
					row.append('0.0,0.0')
					row.append(error)
				else:
					coordinates = result[0].coordinates
					west = str(coordinates[0])
					north = str(coordinates[1])
					coordinates = ','.join([north,west])
					row.append(coordinates)
					row.append(result.raw[0][u'geometry'][u'location_type'])
				writer.writerow(row)

if __name__ == "__main__":
    main()
