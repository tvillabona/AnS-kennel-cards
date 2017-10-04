'''
written in python 2.7 by tim villabona timv@alum.mit.edu

put an adminShelter login and password below, within the single quotes:
'''	
##############################################
login = 'tvillabona'
password = 'rockstar1'
#define a biography in case there isn't one in the ishelters database
defaultbio = r"I just arrived here at Adopt & Shop, so I'm still adjusting to my new living situation. The staff & volunteers have not had a chance to get to know me yet, but please ask for more information if you are interested in making me a part of your family!"
##############################################

import urllib, urllib2, cookielib, csv, glob, os, pdfkit
from datetime import datetime
from operator import itemgetter

picnames = [] #initialize
#user prompt
print "Enter the name of any animals that need kennel cards but don't have a photo yet, press enter after each one. Then press enter again when you're done. Or just press enter to skip: \n"
while True:     #keep asking for names until the user hits Enter twice
	newname = raw_input('\nEnter name:')
	if not newname:
		break
	else:
		picnames.append(newname)
today = str(datetime.now())[0:10] #get date to compute animal's age
today = datetime.strptime(today, '%Y-%m-%d')

def compute_age(birthday): #computes age, rounds to months, only give months if 3 years and younger
	age = ''
	birthday = birthday[0:10]
	birthday = datetime.strptime(birthday, '%Y-%m-%d')
	agedays = str(today - birthday)[0:-14]
	years,days = divmod(int(agedays),365)
	months,remainder = divmod(days,28)
	if years == 1:
		age = age + str(years) + ' year, '
	if years > 1:
		age = age + str(years) + ' years, '
	if years < 4:
                if months == 1:
                        age = age + str(months) + ' month, '
                else:
                        age = age + str(months) + ' months, '
	return age

categories = ['checkins', 'animals']#prepare to download databases
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
login_data = urllib.urlencode({'email' : login, 'password' : password})#from above

#log in and then download each dataset

resp = opener.open('http://admin.ishelters.com/loginProcess.php', login_data)
print "Downloading data from iShelter..."
for category in categories:
        csvdata = opener.open('http://admin.ishelters.com/sy/ex/' + category + '.php')
        f = open(category + '.csv', 'w+')
        f.write(csvdata.read())
        f.close()
animals = open('animals.csv')
checkins = open('checkins.csv')
animalsdict = csv.DictReader(animals)
checkinsdict = csv.DictReader(checkins)
checkinsorted = sorted(checkinsdict, key=itemgetter('Animal Id'))#, reverse=True) #sort by ID#
animalsorted = sorted(animalsdict, key=itemgetter('id'))#reverse = True)

idnum = -1	#initialize only
os.chdir(r'C:\KennelCards\photos')	#change to directory containing kennel card photos

#build list of animal names for all extensions - JPG, JPEG, jpg, jpeg, rename to .jpg
for f in glob.glob("*.jpg"):
	picnames.append(f[0:-4])
for f in glob.glob("*.jpeg"):
	picnames.append(f[0:-5])
	os.rename(f, f[0:-5] + '.jpg')
#for f in glob.glob("*.JPG"):		#written in linux but windows is case-insensitive
#	picnames.append(f[0:-4])
#	os.rename(f, f[0:-4] + '.jpg')
#for f in glob.glob("*.JPEG"):
#	picnames.append(f[0:-5])
#	os.rename(f, f[0:-5] + '.jpg')
os.chdir(r'C:\KennelCards')#write PDF to root dir

#begin building PDF of cards
pdfoptions = {
    'page-size': 'Letter',
    'margin-top': '.2in',
    'margin-right': '1in',
    'margin-bottom': '.2in',
    'margin-left': '1in',
    'encoding': "Unicode"
}
print "Building Kennel Cards..."
with open("cards.html", "w") as cards:	#create html, overwrite each time
	vertpos = 0.5		#top of each card's border, to be incremented
	n = 0
#html preamble, css

	cards.write(r'<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1 plus MathML 2.0//EN" "http://www.w3.org/Math/DTD/mathml2/xhtml-math11-f.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head profile="http://dublincore.org/documents/dcmi-terms/"><meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8"/><style type="text/css">* { margin:0;}'
	'.box { height:5in;width:8in; padding:0; position:absolute; left:0cm;  border-width:0.5cm; border-style:solid;}'
	'.photo { height:4in;width:3in; padding:0; position:absolute; left:0.1cm;}'
	'.logo { height:1.8cm;width:6cm; padding:0; position:absolute; left:3.75in;}'
	'.name { height:0.75in;padding:0;position:absolute;left:0.2cm;  font-size:38pt; font-family:Arial; color:#8A0829; writing-mode:page; font-weight:bold; text-align:left }'
	'.bio { height:3.25in;width:10cm; padding:0; position:absolute; left:9.25cm;  font-size:14pt; font-family:Arial; writing-mode:page; text-align:justify ! important; }'
	'.info { height:2.25in;width:12cm; padding:0; position:absolute; left:8.5cm;  font-size:18pt; font-family:Arial; color:#8A0829; writing-mode:page; text-align:center ! important; }'
	'break { page-break-after:always; }	</style></head><body>'
	)
	
	for picname in picnames:		#find ID# by most recent animal checked in matching name
		for row in checkinsorted:
			if row['Name'] == picname and row['Previous Agency'] == 'RETURN ADOPTION':
                                continue
                        elif row['Name'] == picname:
				prev_agency = row['Previous Agency']
                                idnum = row['Animal Id']
			for rowe in animalsorted:
				if rowe['id'] == idnum:			#gather kennel card info
					bio = rowe['long biography']
					if not bio:#sub dummy bio if no bio written
						bio = defaultbio					
					pribreed = rowe['primary breed']
					species = rowe['species']
					secbreed = rowe['secondary breed']
					if rowe['sex'][-4:] == 'Male': # xxxx Female would be lower case m
						sex = 'Male'
						bordercol = r'FACC2E' #gold for males
					else:
						sex = 'Female'
						bordercol = r'04B4AE' #teal for females
					pricol = rowe['primary color']
					if pricol[-1] == ')': #chop off (Dog) or (Cat)
                                             pricol = pricol[0:-6]
					#seccol = rowe['secondary color']#currently not writing secondary colors
					code = rowe['code']
					age = compute_age(rowe['birth date'])
		try:
                        cards.write('<div style="top:' + str(vertpos) + 'in; border-color:#' + bordercol + ';" class="box">')
                except:
                        cards.write('div style="top:' + str(vertpos) + 'in; border-color:#000000;" class="box">') 
		if len(picname) > 13:#if name is too long decrease font size		
			cards.write('<p style=" top:0.5cm; font-size:32pt;" class="name">')
		else:			
			cards.write('<p style=" top:0.5cm" class="name">')# begin writing HTML body
		cards.write(picname)
		cards.write('</p>')
		cards.write('<img class="logo" style="bottom:0.2cm;" alt="photo-missing.jpg" src="as_logo.png"/>')
		cards.write('<img class="photo" style="bottom:0.1cm;" alt="photo-missing.jpg" src="')
		if os.path.isfile('photos\\' + picname + '.jpg'):#if photo exists, use it, otherwise use default dog/cat photos
			cards.write('photos/' + picname + '.jpg')
		else:
			if species == 'Cat':
				cards.write('cat.png')
			else:
				cards.write('dog.png')
		cards.write('"/>')
		if len(pribreed) > 19:#decrease font size if breed name too long
			cards.write('<p class="info" style="font-size:12pt; top:0.5cm;">')
		else:
			cards.write('<p class="info" style="top:0.5cm;">')
		cards.write(pricol + ' ' + pribreed)
		cards.write('<br>')
		cards.write(age + sex)
		cards.write(r'<br>ID# ' + code)
		cards.write(r'</p>')
		if len(bio) > 450:#decrease font size if bio too long
			cards.write(r'<p class="bio" style="font-size:12pt; bottom:1.75cm;">')
		else:
			cards.write(r'<p class="bio" style="bottom:1.85cm;">')
                if prev_agency:
                        cards.write(bio + '<br><br>' + picname + ' was procured from ' + prev_agency + '.')
                else:
                        cards.write(bio)
		cards.write(r'</p></div>')
		n = n + 1
		vertpos += 6.9
		code = ''
		prev_agency = ''
	cards.write(r"</body></html>")		#close out html
pdfkit.from_file('cards.html', 'cards.pdf', options = pdfoptions)
raw_input('Kennel Card PDF generated. Press Enter to exit.')
