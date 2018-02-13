#!/usr/bin/env python
# -*- encoding: iso-8859-1 -*-
#  Automatically parse website for exam results
#
# "Well, if I'm not able to get my exam results, i'm at least making sure I contribute to the server outage!"
#
# Author:           Max Blank
# Last modified:    13.02.2016
#
# Adapted to new login process and form layout
#
# Please use with care! I'm not to be held responsible for any damage
# this software might cause to anyone or anything!

import sys
import re
import webbrowser
import os
from mechanize import Browser
from urllib2 import URLError
from time import sleep


user = ""                   # login name
password = ""               # password
gradepath = "noten.html"    # path to store grade html-file

# if len(sys.argv) == 1:
#     print "Not enough parameters!"

browser = Browser()
browser.set_handle_robots(False) # ignore robots.txt

while True:     # trying to load primuss.de
    try:
        response = browser.open("https://www3.primuss.de/cgi-bin/login/index.pl?FH=fhm")
        break

    except URLError:
        print "Timeout requesting login form; trying again!"
        sleep(20)
        pass

# Fill login form
print "Logging in..."
browser.form = list(browser.forms())[0]
browser['j_username'] = user
browser['j_password'] = password
# browser.select_form('AnmeldeForm')
# browser.form['Nachname'] = nachname
# browser.form['Vorname'] = vorname
# browser.form['GebDatum'] = gebdatum
# browser.form['GebOrt'] = gebort
# browser.form['MCard'] = mcard
response = browser.submit()

# print response.read()

# if login failed:
if (re.search("Das eingegebene Passwort ist nicht korrekt.", browser.response().read()) is not None) \
        or (re.search("Der eingegebene Benutzername wurde nicht gefunden.", browser.response().read()) is not None):
    print "Login failed! Check credentials!"
    exit(1)
else:
    print "Logged in!"
    browser.form = list(browser.forms())[0]     # proceed from javascript-warning
    response = browser.submit()

    print "Extracting Session ID"
    browser.select_form("Form1")
    control = browser.form.find_control("Session")
    sessionID = control._value
    control = browser.form.find_control("User")
    userID = control._value

    print "Opening grade view..."
    while True:
        try:
            response = browser.open("https://www3.primuss.de/cgi-bin/pg_Notenbekanntgabe/showajax.pl?FH=fhm&Session="
                                    + sessionID + "&User=" + userID + "&Portal=1")
            break
        except URLError:
            print "Timeout opening grade view! Trying again in 10 seconds..."
            sleep(10)
            pass

if re.search("Wir befinden uns jetzt <b>vor</b> dem Zeitraum der Notenbekanntgabe.", response.read()) is not None:
    print "Grades not published yet! Try again later!"
    exit(1)
else:
    print "Found grades!"
    print "Saving grades..."
    gradefile = open(gradepath, "w+")
    gradefile.write(browser.response().read())
    gradefile.close()
    print "Grades saved!"
    print "Displaying grades..."
    webbrowser.open('file://' + os.path.realpath(gradepath))
    exit(0)
