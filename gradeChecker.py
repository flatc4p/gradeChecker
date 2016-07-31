#!/usr/bin/env python
# -*- encoding: iso-8859-1 -*-
#  Automatically parse website for exam results
#
# "Well, if I'm not able to get my exam results, i'm at least making sure I contribute to the server outage!"
#
# Author:           Max Blank
# Last modified:    31.07.2016
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


nachname = ""   # last name of student
vorname = ""    # first name(s) of student
gebdatum = ""   # birthday of student
gebort = "" # birthplace of student
mcard = ""  # badge number of student
gradepath = "noten.html"    # path to store grade html-file

if len(sys.argv) == 1:
    print "Not enough parameters!"

browser = Browser()

while True:     # trying to load primuss.de
    try:
        response = browser.open("https://www1.primuss.de/cgi/Sesam/sesam.pl?FH=fhm")
        break

    except URLError:
        print "Timeout requesting login form; trying again!"
        sleep(20)
        pass

# Fill login form
print "Logging in..."
browser.select_form('AnmeldeForm')
browser.form['Nachname'] = nachname
browser.form['Vorname'] = vorname
browser.form['GebDatum'] = gebdatum
browser.form['GebOrt'] = gebort
browser.form['MCard'] = mcard
browser.submit()

# if login failed:
if (re.search('<span class="Fehler">Fehler:</span> Anmeldung fehlerhaft, kein Zugriff!</p>', browser.response().read())
        is not None):
    print "Login failed! Check credentials!"
else:
    print "Logged in!"
    print "Searching grades..."
    browser.follow_link(text="Services")    # navigate to grade view
    for form in browser.forms():
        if form.attrs["action"]=="https://www3.primuss.de/cgi-bin/pg_Notenbekanntgabe/index.pl":
            browser.form = form
            break

    browser.submit()
    browser.select_form('Form')
    notenurl = "https://www3.primuss.de/cgi-bin/pg_Notenbekanntgabe/showajax.pl?Language=de&Session="
    sessionid = browser.form['Session']
    poison = browser.form['Poison']
    while True:
        try:
            browser.open(notenurl + sessionid + "&Poison=" + poison + "&User=" + mcard + "&FH=fhm&Accept=X")
            break

        except URLError:
            print "Timeout openening grade view! Trying again..."
            sleep(10)
            pass

    print "Found grades!"
    print "Saving grades..."
    gradefile = open(gradepath, "w+")
    gradefile.write(browser.response().read())
    gradefile.close()
    print "Grades saved!"
    print "Displaying grades..."
    webbrowser.open('file://' + os.path.realpath(gradepath))
