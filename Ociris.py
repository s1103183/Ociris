import requests
import re
import time
import os
import smtplib
from BeautifulSoup import BeautifulSoup
from time import gmtime, strftime

class studieVolg(object):
	def __init__(self, gebruikersnaam, wachtwoord):
		os.system('cls')
		print("		                                                    ")
		print("   _|_|      _|_|_|  _|_|_|  _|_|_|    _|_|_|    _|_|_|  ")
		print(" _|    _|  _|          _|    _|    _|    _|    _|        ")
		print(" _|    _|    _|_|      _|    _|_|_|      _|      _|_|    ")
		print(" _|    _|        _|    _|    _|    _|    _|          _|  ")
		print("   _|_|    _|_|_|    _|_|_|  _|    _|  _|_|_|  _|_|_|    ")
		print("")	
		print("Logging in with username: " + gebruikersnaam)
		print("")
		
		self.gebruikersnaam = gebruikersnaam
		self.wachtwoord = wachtwoord
		self.baseurl = "https://studievolg.hsleiden.nl/student/"
		self.lastdegree = {"Cursus": "ISLP" }
		
	def run(self): 
		while True:
			self.get_requestToken()
			self.login()
			self.get_resultaten()
			self.loguit()
			time.sleep(45 * 60)
			
	def login(self):  
		#POST /student/AuthenticateUser.do HTTP/1.1
		#startUrl=Personalia.do&inPortal=&callDirect=&requestToken=******************&VB_gebruikersNaam=***********&VB_wachtWoord=*********&event=login
		data = { "startUrl" : "Personalia.do", "inPortal=" : "", "callDirect" : "", "requestToken" : self.requestToken, "VB_gebruikersNaam" : self.gebruikersnaam, "VB_wachtWoord" : self.wachtwoord, "event" : "login" }
		response = requests.post(self.baseurl + "AuthenticateUser.do", data = data)
		
		cookiedata = response.headers['Set-Cookie']
		if len(cookiedata) > 0: 
			print(strftime("[%H:%M:%S]", gmtime()) + " Login Succesful")
			#print("")	
			self.sessionid = self.find_between(cookiedata, "OSISTUDENTSESSIONID=", "; path=/; HttpOnly, _")
			self.authcookie = self.find_between(cookiedata, "_WL_AUTHCOOKIE_OSISTUDENTSESSIONID=", "; path=/; secure; HttpOnly") 
			self.cookie = { "OSISTUDENTSESSIONID" : self.sessionid, "_WL_AUTHCOOKIE_OSISTUDENTSESSIONID" : self.authcookie, "oracle.uix" : "0^^GMT+1:00" }
			#print("SessionID: \t" + self.sessionid)
			#print("AuthCookie: \t"   + self.authcookie)
			#print("")	
		else:
			print("Failed to login")
			
		 
		
		
	def get_resultaten(self):
		response = requests.get(self.baseurl + "ToonResultaten.do", cookies = self.cookie)
		self.soup = BeautifulSoup(response.text)
		table = self.soup.findAll("table", { "class" : "OraTableContent"})
		lines = table[0].findAll("tr")
		 
		topresult = self.parse_resultaat(lines[1])
		
		if str(self.lastdegree["Cursus"]) != topresult["Cursus"]:
			print(strftime("[%H:%M:%S]", gmtime()) + " Nieuw resultaat gevonden!!!!") 
			self.send_mail(topresult)
			self.lastdegree = topresult 
			
	def parse_resultaat(self, line):
		#Cursus 1
		#Type 3
		#Datum toets 0
		#Resultaat 6
		objects = line.findAll("td")
		return { "Cursus" : objects[1].text, "Type" : objects[3].text, "ToetsDatum" : objects[0].text, "Resultaat" : objects[6].text}
		 
	def loguit(self):
		response = requests.get(self.baseurl + "Logout.do", cookies = self.cookie)
		
	def get_requestToken(self):
		#GET /student/StartPagina.do HTTP/1.1 
		result = requests.get(self.baseurl + "Personalia.do")
		if result.status_code == 200:
			self.requestToken = self.find_between(result.text, "<input id=\"requestToken\" type=\"hidden\" value=\"", "\" name=\"requestToken\"")
			 
			#print("Requesttoken: \t" + self.requestToken)
			return True
		else:
			return False
			
	def find_between(self, s, first, last ):
		try:
			start = s.index( first ) + len( first )
			end = s.index( last, start )
			return s[start:end]
		except ValueError:
			return ""
	
	#Outlook / Hotmail
	def send_mail(self, degree):
		import smtplib  
		from email.MIMEMultipart import MIMEMultipart
		from email.MIMEText import MIMEText
		fromaddr = '' #Sender Email
		toaddrs  = '' #Target Email
		message= str(degree["Cursus"]) + "\t" + str(degree["ToetsDatum"]) + "\t" + str(degree["Resultaat"])

		msg = MIMEMultipart()
		msg['From'] = fromaddr
		msg['To'] = toaddrs
		msg['Subject'] ='Nieuw Cijfer voor ' + str(degree['Cursus'])
		msg.attach(MIMEText(message))
		
		# Credentials   
		password = '' #wachtwoord van je mail
		# The actual mail send  
		server = smtplib.SMTP('smtp.live.com:587')  
		server.starttls()  
		server.login(fromaddr,password) 
		server.sendmail(fromaddr, toaddrs, msg.as_string()) 
		server.quit()
		print("Succesfully send mail!")

studievolg = studieVolg("<studentennummer hier>", "<wachtwoord hier>")
studievolg.run()