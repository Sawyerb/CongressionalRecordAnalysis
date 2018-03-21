import urllib2
import re
from tqdm import tqdm
import json
import pprint

#first download the html from this url: https://www.congress.gov/congressional-record/112th-congress/browse-by-date as 
#save it as ./congressional_record_home.html
#to get data for another session, go to the corresponding url
with open('./congressional_record_home.html', 'r') as file:
	text = file.read()

cr = {}
i = 0
success = 0
total = 0
pattern = re.compile('congressional-record.{0,12}(?=house-section)')
for match in tqdm(re.findall(pattern, text)):
	i += 1
	try:
		url = 'https://www.congress.gov/' + match + 'house-section'
		req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
		text = urllib2.urlopen( req )
		text= text.read()
		
		pattern = re.compile('congressional-record.{0,12}\/house-section\/article.*?(?=">)')
		for match2 in tqdm(re.findall(pattern, text)):
			try:
				url = 'https://www.congress.gov/' + match2
				req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
				con = urllib2.urlopen( req )
				con = con.read()
				con = re.search("\[www\.gpo\.gov.+?(?=<\/pre)", con, re.DOTALL).group(0)
				pattern = re.compile("M(?:r|s|rs)\. (?:[A-Z -]|Mc|De|Del|Des|La|Lo)+?(?:\.|of [A-z ]+?\.).+?(?=M(?:r|s|rs)\. (?:[A-Z -]|Mc|De|Del|Des|La|Lo)+?(?:\.|of [A-z ]+?\.)|__________|The SPEAKER|The Acting CHAIR|The CHAIR|A recorded vote was ordered|The Clerk read the title of the bill|I reserve the balance of my time|\(M(?:r|s|rs)\. (?:[A-Z -]|Mc|De|Del|Des|La|Lo)+?(?:\.|of [A-z ]+?\.))",  re.DOTALL)
				for match3 in re.findall(pattern, con):		 
					try:
						match4 = re.search("(M(?:r|s|rs)\. (?:[\w -])+?\.) (.*[\.?])", match3, re.DOTALL)
						name = match4.group(1)
						text = match4.group(2)
						if(name not in cr):
							cr[name] = []
						cr[name].append(text)
					except:
						continue
				total += 1
				success += 1
			except:
				total += 1		
	except:
		total += 1

print "success ratio: " + str(success) + '/' + str(total) 

with open('congressional_record.json', 'w') as outfile:
	json.dump(cr, outfile)