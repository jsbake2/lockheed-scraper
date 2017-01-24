#!/usr/bin/python
import time
import csv
import re
import companyinfo
from companyinfo import infofiller
import locations
from locations import parser
import clearances
from clearances import clearance as clear
import asciiClean
from asciiClean import ascii_clean
from sys import argv
import datetime
logFile = 'logfile'
csvFile = 'csvWork.csv'
outFile = 'csvFinal.csv'
clearance = ""
doneThis = {}

LOG = open(logFile, 'w')

# Open CSV output stream
logDate= datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
companyName = 'Lockheed Martin'
output = open('/home/jbaker/Desktop/'+companyName+'_'+logDate+'_'+outFile, 'wb')
output2 = open('/home/jbaker/Desktop/'+companyName+'_2_'+logDate+'_'+outFile, 'wb')
wr = csv.writer(output, quoting=csv.QUOTE_ALL)
wr2 = csv.writer(output2, quoting=csv.QUOTE_ALL)

csv.register_dialect(
  'mydialect',
  delimiter=',',
  quotechar='"',
  doublequote=True,
  skipinitialspace=True,
  lineterminator='\r\n',
  quoting=csv.QUOTE_MINIMAL)

divC = lambda x: re.sub('</div>|<div>', '', x)


def finder(messy,findMe):
  found = 'UNKNOWN'
  for m in range(len(messy)):
    messS = re.split('\n', messy[m])
    for s in range(len(messS)):
      if re.search(findMe, messS[s]):
        if s + 1 != len(messS):
          found=re.sub('\s*<.+>(.*)<.+>\s*',r'\1',messS[s+1])
  return divC(found)

def asciiCleanup():
  print 'done'


wr.writerow(['title', 'apply_url', 'job_description', 'location', 'company_name', 'company_description', 'company_website', 'company_logo', 'company_facebook', 'company_twitter', 'company_linkedin', 'career_id', 'deployment', 'travel', 'job_lat', 'job_lon', 'company_benefits', 'job_category', 'clearance', 'keywords'])

wr2.writerow(['title', 'apply_url', 'job_description', 'location', 'company_name', 'company_description', 'company_website', 'company_logo', 'company_facebook', 'company_twitter', 'company_linkedin', 'career_id', 'deployment', 'travel', 'job_lat', 'job_lon', 'company_benefits', 'job_category', 'clearance', 'keywords'])

infoComp,infoDesc,infoSite,infoLogo,infoFace,infoTwit,infoLinked,infoBeni=companyinfo.infofiller(companyName)

with open(csvFile, 'rb') as mycsv:
  data=csv.reader(mycsv, dialect='mydialect')
  for row in data:
    #for k in range(len(row)):
      #print "########################## "+str(k)+" "+row[k]
    keyw   = ''
    keywordsLoc = ''
    desc    = row[1]
    pageUrl = row[0]
    title   = row[2]
    messL   = row[5:]
    #reqL = re.split('/', pageUrl)
    req = str()
    reqIdList = re.split('\n', row[4])
    for r in range(len(reqIdList)):
      if re.search('Req ID ', reqIdList[r]):
        req =  re.sub('(<div class="jobdescription-value">)|(</div>)', '', reqIdList[r+1])
        
    #if (len(reqL) > 4):
      #req = reqL[5]
    #else:
      #req = 'UNKNOWN'
    req    = divC(req)
    title  = divC(title)
    state         = finder(messL,'State')
    shift         = finder(messL,'Shift')
    city          = finder(messL,'City')
    reqType       = finder(messL,'Req Type')
    workSchedule  = finder(messL,'Work Schedule')
    virtual       = finder(messL,'Vitrual')
    businessUnit  = finder(messL,'Business Unit')
    addiLoca      = finder(messL,'Additional Posting Locations')
    reloc         = finder(messL,'Relocation Available')
    prog          = finder(messL,'Program')
    clearanceRaw  = finder(messL,'Security Clearance')
    jobClass      = finder(messL,'Job Class')
    job_c         = finder(messL,'Job Category')
    forLoc        = finder(messL, 'Foreign Location')
    applyLink     = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(row))
    loc = city+', '+state
    if re.match('location', loc):
      LOG.write("Skipping header field")
    elif len(desc) == 0:
      LOG.write("This one has an empty desc.")
    elif doneThis.has_key(req):
      LOG.write("Already done this crap...")
    elif (re.match('UNKNOWN', loc)):
      print "This one is a fucking mess"+loc+'   '+title
    elif (re.match('International', loc)):
      print title+'   '+loc
    else:
      doneThis[req] = "TRUE"
      # This is the final fix for REQ
      #req=re.sub(".+ID=(\d+)\&.+",r'\1',req)
      clearance,keywords = clear.clear(clearanceRaw)
      if re.search('UNKNOWN', forLoc):
        #print "Here we are (conus): "+loc
        loc,lat,lon,keywordsLoc = parser.loc(loc,"lockheed")
      else:
        #print "Here we are(oconus): "+forLoc
        loc,lat,lon,keywordsLoc = parser.loc(forLoc,"lockheedO")
      for i in keywords:
        keyw=keyw+' '+i
      keyw = keyw + ' ' + keywordsLoc+ ' ' +addiLoca
      appUrl = re.sub("',",'',applyLink[1])

      finalList = [title, appUrl, desc, loc, infoComp, infoDesc, infoSite, infoLogo, infoFace, infoTwit, infoLinked, req, 'UNKNOWN', virtual, lat, lon, infoBeni, job_c, clearance, keyw]

      for a in range(len(finalList)):
        finalList[a] = ascii_clean.cleanUp(finalList[a])
      
      if not re.match("None|^$", clearance):
        wr.writerow(finalList)

