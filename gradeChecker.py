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


import webbrowser
import os
from threading import *
from Tkinter import *
from mechanize import Browser
from urllib2 import URLError
from time import sleep

Version = "v0.3"

# Nachname = "Blank"   # last name of student
# Vorname = "Maximilian Alexander"    # first name(s) of student
# GebDatum = "20.02.1989"   # birthday of student
# GebOrt = "München" # birthplace of student
# MCard = "88948888012"  # badge number of student
GradePath = "noten.html"    # path to store grade html-file


def checkgrades():

    # get values from entry fields
    nachname = enterNachname.get()
    vorname = enterVorname.get()
    gebdatum = enterGebDatum.get()
    gebort = enterGebOrt.get().encode('iso-8859-1')
    mcard = enterMCard.get()
    print gebort

    browser = Browser()

    while True:     # trying to load primuss.de
        try:
            browser.open("https://www1.primuss.de/cgi/Sesam/sesam.pl?FH=fhm")
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
                print "Timeout opening grade view! Trying again..."
                sleep(10)
                pass

        print "Found grades!"
        print "Saving grades..."
        gradefile = open(GradePath, "w+")
        gradefile.write(browser.response().read())
        gradefile.close()
        print "Grades saved!"
        print "Displaying grades..."
        webbrowser.open('file://' + os.path.realpath(GradePath))


# build gui
root = Tk()
root.title("gradeChecker " + Version)

lab = Label(root, text="Das leidige Abfragen von Primuss automatisieren")
lab.pack()

labelNachname = Label(root, text="Nachname:")
labelNachname.pack()
enterNachname = Entry(root)
enterNachname.pack()

labelVorname = Label(root, text="Vorname(n):")
labelVorname.pack()
enterVorname = Entry(root)
enterVorname.pack()

labelGebDatum = Label(root, text="Geburtsdatum:")
labelGebDatum.pack()
enterGebDatum = Entry(root)
enterGebDatum.pack()

labelGebOrt = Label(root, text="Geburtsort:")
labelGebOrt.pack()
enterGebOrt = Entry(root)
enterGebOrt.pack()

labelMCard = Label(root, text="Magnetkarten-Nr.:")
labelMCard.pack()
enterMCard = Entry(root)
enterMCard.pack()

runningthread = Thread(target=checkgrades)

def abort():
    print "Abbrechen"
    if runningthread.isAlive():
        runningthread.join()

def start():
    print "Starting query..."
    runningthread.start()

buttonAbort = Button(root, text="Abbrechen", command=abort)
buttonCheckGrades = Button(root, text="Abfrage", command=checkgrades)
buttonCheckGrades.pack()
buttonAbort.pack()

root.mainloop()



