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

def finder(messy,findMe):
  found = 'UNKNOWN'
  for m in range(len(messy)):
    messS = re.split('\n', messy[m])
    for s in range(len(messS)):
      if re.search(findMe, messS[s]):
        if s + 1 != len(messS):
          found=re.sub('\s*<.+>(.*)<.+>\s*',r'\1',messS[s+1])
  return found

def asciiCleanup():
  print 'done'

wr.writerow(['title', 'apply_url', 'job_description', 'location', 'company_name', 'company_description', 'company_website', 'company_logo', 'company_facebook', 'company_twitter', 'company_linkedin', 'career_id', 'deployment', 'travel', 'job_lat', 'job_lon', 'company_benefits', 'job_category', 'clearance', 'keywords'])

wr2.writerow(['title', 'apply_url', 'job_description', 'location', 'company_name', 'company_description', 'company_website', 'company_logo', 'company_facebook', 'company_twitter', 'company_linkedin', 'career_id', 'deployment', 'travel', 'job_lat', 'job_lon', 'company_benefits', 'job_category', 'clearance', 'keywords'])

infoComp,infoDesc,infoSite,infoLogo,infoFace,infoTwit,infoLinked,infoBeni=companyinfo.infofiller(companyName)

with open(csvFile, 'rb') as mycsv:
  data=csv.reader(mycsv, dialect='mydialect')
  for row in data:
    keyw   = ''
    keywordsLoc = ''
    desc    = row[1]
    appUrl = row[0]
    title   = row[3]
    messL   = row[3:]
    reqL = re.split('/', appUrl)
    if (len(reqL) > 4):
      req = reqL[5]
    else:
      req = 'UNKNOWN'
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
    
    loc = city+', '+state
    
    #print req
    #print '\n\n\n'
    if re.match('location', loc):
      LOG.write("Skipping header field")
    elif len(desc) == 0:
      LOG.write("This one has an empty desc.")
    elif doneThis.has_key(req):
      LOG.write("Already done this crap...")
    else:
      doneThis[req] = "TRUE"
      # This is the final fix for REQ
      req=re.sub(".+ID=(\d+)\&.+",r'\1',req)
      clearance,keywords = clear.clear(clearanceRaw)

      loc,lat,lon,keywordsLoc = parser.loc(loc,"lockheed")
      for i in keywords:
        keyw=keyw+' '+i
      keyw = keyw + ' ' + keywordsLoc+ ' ' +addiLoca
      #print loc + ' ||||||||||||| THIS IS FUCKED UP ||||||||||||| ' + keywordsLoc
      
      finalList = [title, appUrl, desc, loc, infoComp, infoDesc, infoSite, infoLogo, infoFace, infoTwit, infoLinked, req, 'UNKNOWN', virtual, lat, lon, infoBeni, job_c, clearance, keyw]

      for a in range(len(finalList)):
        finalList[a] = ascii_clean.cleanUp(finalList[a])
      
      if not re.match("None|^$", clearance):
        wr.writerow(finalList)

