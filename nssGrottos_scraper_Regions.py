import urllib2
from BeautifulSoup import BeautifulSoup
import re
import csv

'''
Currently this sciprt will produce the grotto name, gid, and website
Somehow this produced a large number of duplicate entries! 4nov2011
'''

class AutoVivification(dict):    
    '''
    Implementation of perl's autovivification feature.
    #class taken from stackoverflow
    #http://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries-in-python
    '''
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value  
allGrottos = AutoVivification()
def main():   

    #The nss grotto website is a bit flaky. Try twice for good measure
    try:
        addressToCheck = "http://www.nssio.org/find_region_overview.cfm"
        page = urllib2.urlopen(addressToCheck)
        soup = BeautifulSoup(page) 
    except urllib2.URLError, e:
        print "Error trying to open "+addressToCheck
        print "Error code: ",e
        #Try a second time!
        #addressToCheck = "http://www.nssio.org/find_grotto_overview.cfm?state="+state
        page = urllib2.urlopen(addressToCheck)
        soup = BeautifulSoup(page)
  
    spantags(soup)
    ptags(soup)
    #printer()  
    toCsv()
        
########################################
#Gather data from <span> tags
def spantags(soup):
    l3 = []
    l4 = []
    one = ""
    # page = urllib2.urlopen("http://www.nssio.org/find_grotto_overview.cfm?state=CA")
    # soup = BeautifulSoup(page)
    for item in soup.findAll('span'):
        l3.append(item)
    for thing in l3:
        website = ""
        grotto = ""
        moreinfo = ""
        addressList = []
        one = str(thing.prettify())
        sour = BeautifulSoup(one)
        l4 = sour.findAll('a')
        if len(l4) == 1:
            grotto = sour.find('strong').renderContents().strip()
            moreinfo = l4[0]['href']
        elif len(l4) == 2:
            grotto = sour.find('strong').findNext('a').renderContents().strip()
            moreinfo = l4[1]['href']
            website = l4[0]['href']
        if grotto not in allGrottos.keys():
            if (re.search("\d{6}$", moreinfo)):
                gid = (re.search(".{6}$", str(moreinfo))).group(0)
                for item in sour.findAll('font', size=2, text=True): 
                    if (len(item)> 2):
                        addressList.append(item.strip())    
                allGrottos[grotto]['name'] = grotto.strip()
                allGrottos[grotto]['website'] = website
                allGrottos[grotto]['gid'] = gid
                allGrottos[grotto]['addressList'] = addressList
                moreInfoPage(gid, grotto)
    return ()

def ptags(soup):
    ########################################
    #Gather data from <p> tags        
    lp = []       
    for item in soup.findAll('p', "admin"):
        lp.append(item)
    for item in lp:
        website = ""
        grotto = ""
        moreinfo = ""
        addressList = []
        one = str(item.prettify())
        sour = BeautifulSoup(one)

        if len(sour.findAll('a')) == 2:
            website = sour.findAll('a')[0]['href']
            moreinfo = sour.findAll('a')[1]['href']
        if len(sour.findAll('a')) == 1:
            moreinfo = sour.findAll('a')[0]['href']
        if (re.search("\d{6}$", moreinfo)):
            if grotto not in allGrottos.keys():
                grotto = item.findNext('a').renderContents().strip()
                #Take some actions using this line to remove the garbage at the end!
                gid = (re.search("\d{6}$", str(moreinfo))).group(0)
                for item in sour.findAll(text=True):
                    if len(item)> 2:
                        addressList.append(item.strip())
                allGrottos[grotto]['name'] = grotto.strip()
                allGrottos[grotto]['website'] = str(website)
                allGrottos[grotto]['gid'] = gid 
                # allGrottos[grotto]['addressList'] = addressList
                moreInfoPage(gid, grotto)
    return()
    
def moreInfoPage(gid, grotto):
    publication = ""
    moreInfoText = []
    try:
        addressToCheck = 'http://www.nssio.org/find_grotto_detail.cfm?gid='+gid
        pager = urllib2.urlopen(addressToCheck)
        souper = BeautifulSoup(pager)
    except urllib2.URLError, e:
        print "Error trying to open "+addressToCheck
        print "Error code: ",e
        #addressToCheck = 'http://www.nssio.org/find_grotto_detail.cfm?gid='+gid
        pager = urllib2.urlopen(addressToCheck)
        souper = BeautifulSoup(pager)
    temp = souper.find('body').findAllNext('table')
    for item in temp[3].findAll('p'): 
        moreInfoText.append(remove_html_tags(item.renderContents()).strip())

    i = 0
    mail_address = []
    t2 = []
    genCont = []
    firstCont = []
    secondCont = []
    meetEnable = 0
    contactEnable = 0
    meetLoc = ""
    #assumed all grottos have 2 contact people listed (might be wayyy off)
    name1 = ""
    name2 = ""
    finalcountdown = 0
    #Work around to a ~mistake~ I made?
    temp = '\n'.join(moreInfoText)
    moreInfoText = temp.split('\n')
    for item in moreInfoText:
        item = item.strip()
        if len(item)>0:
            t2.append(item)

    moreInfoText = t2
    for line in moreInfoText:
        #print line
        #assumes all addresses are only two lines
        if (i==3) or (i==4):
            mail_address.append(line)
        #pull out meeting location
        if (meetEnable == 2) and (len(meetLoc)==0):
            #print "in the final meat:",line
            meetLoc = line
        if (meetEnable == 1) and (re.search('Please', line)):
            #print "meetEnable2!!!:", line
            meetEnable = 2
        if (re.search('Meeting', line)):
            meetEnable = 1
        if (re.search('Publication', line)):
            publication = line[13:]
        if (contactEnable == 1):
            #print "spacer"+ line + "spacer"
            #In contact info if not a website or phone num expect as contact name
            #Doesn't cover ALL cases, but should be good enough
            if (bool(re.search('^.*(\.com|\.org|\.net|\.edu|@|\d).*$',line))==False ):
                #print line
                if (len(name1) == 0):            
                    name1 = line               
                elif (len(name2) == 0):
                    name2 = line
            #read two lines after the last contact then break the loop    
            if (len(name2)>0):           
                if (finalcountdown > 2):
                    #print "BROKEN!!!"
                    break
                finalcountdown+=1
            #Hopefully the length here isn't too big.
            #Ignorirng all & was to drop things like &nsbp, but it also
            #killed some websites (facebook)
            #if (len(line)>6) and (re.search('^[^&]*$', line)):
            if (len(line)>6):   
                if len(name1) == 0:
                    genCont.append(line)
                elif (len(name1) > 0) and (len(name2) == 0):
                    firstCont.append(line)
                else:
                    secondCont.append(line)
                
        if (re.search('Contact Info',line)):       
            contactEnable = 1
        i+=1

    allGrottos[grotto]['mailaddress'] = ', '.join(mail_address)
    allGrottos[grotto]['meetLoc'] = meetLoc   
    allGrottos[grotto]['publication'] = publication    
    allGrottos[grotto]['genCont'] = ', '.join(genCont)    
    allGrottos[grotto]['firstCont'] = ', '.join(firstCont)    
    allGrottos[grotto]['secondCont'] = ', '.join(secondCont)    
    print 'Name:',allGrottos[grotto]['name']
    print 'Address:',allGrottos[grotto]['mailaddress']
    print 'Website:',allGrottos[grotto]['website']
    print 'Gid:',allGrottos[grotto]['gid']
    print 'Meeting location:',allGrottos[grotto]['meetLoc']
    print 'Publication:',allGrottos[grotto]['publication']
    print 'General Contact Info:',allGrottos[grotto]['genCont']
    print 'First Contact:',allGrottos[grotto]['firstCont']
    print 'Second Contact:',allGrottos[grotto]['secondCont']
    print '\n'

def printer():
    for grotto in allGrottos:
        print 'Name:',allGrottos[grotto]['name']
        print 'Address:',allGrottos[grotto]['mailaddress']
        print 'Website:',allGrottos[grotto]['website']
        print 'Gid:',allGrottos[grotto]['gid']
        print 'Meeting location:',allGrottos[grotto]['meetLoc']
        print 'Publication:',allGrottos[grotto]['publication']
        print 'General Contact Info:',allGrottos[grotto]['genCont']
        print 'First Contact:',allGrottos[grotto]['firstCont']
        print 'Second Contact:',allGrottos[grotto]['secondCont']
    
def toCsv():
    outputWriter = csv.writer(open('NSSRegions.csv', 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #probably a prettier way to loop through this...
    outputWriter.writerow(['Name', 
            'Mailaddress', 
            'Website', 
            'GID',
            'Meeting Location',
            'Publication', 
            'genCont', 
            'firstCont', 
            'secondCont'])
    for grotto in allGrottos:
        outputWriter.writerow([allGrottos[grotto]['name'], 
            allGrottos[grotto]['mailaddress'], 
            allGrottos[grotto]['website'], 
            allGrottos[grotto]['gid'],
            allGrottos[grotto]['meetLoc'],
            allGrottos[grotto]['publication'], 
            allGrottos[grotto]['genCont'], 
            allGrottos[grotto]['firstCont'], 
            allGrottos[grotto]['secondCont']])
        
# def getStates():
    # stateList = []
    # page = urllib2.urlopen("http://www.nssio.org/Find_Grotto.cfm")
    # soup = BeautifulSoup(page)
    # hogwash =  soup.findAll(value=re.compile("^..$"))
    # for item in hogwash: 
        # stateList.append(str(item['value']))
    # return stateList

def remove_html_tags(data):
    #this function was taken from another website...
    p = re.compile(r'<.*?>')
    return p.sub('', data)

  
            
if __name__ == "__main__":
    main()
