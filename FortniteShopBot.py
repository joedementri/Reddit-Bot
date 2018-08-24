#!/usr/bin/python
import praw
import pdb
import re
import os
import requests
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials

#Format of Comment to Make:
"""
Last time each item was in the shop:

* [Featured] - [Date], X days ago

* [Featured] - [Date], X days ago

* [Daily] - [Date], X days ago

* [Daily] - [Date], X days ago

* [Daily] - [Date], X days ago

* [Daily] - [Date], X days ago

* [Daily] - [Date], X days ago

* [Daily] - [Date], X days ago

---

Since people always wonder/complain about skins not appearing enough, I'm keeping a spreadsheet of the last time each item was in the shop.

[**Link to Spreadsheet**](https://docs.google.com/spreadsheets/d/1vsascLSC9ynd6JFEgaIbolFPSYUXz-xgigvTjiANxkU/edit?usp=sharing)
"""

#Create the Reddit Instance
reddit = praw.Reddit('bot1')

# Have we run this code before? If not, create an empty list
if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []
# If we have run the code before, load the list of posts we have replied to
else:
    #Read the file into a list and remove empty values
    with open("posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n")
        posts_replied_to = list(filter(None, posts_replied_to))
        print(posts_replied_to)

# Get the top 5 values from our subreddit
subreddit = reddit.subreddit('FortniteBR')
for submission in subreddit.new(limit=50):
    #print(submission.title)

    # If we haven't replied to this post before
    if submission.id not in posts_replied_to:
        #approved submitters (me and ###) and titles
        #Usernames Redacted Below
        if (submission.author == "" or submission.author == "") and ("store" in submission.title.lower() or "item" in submission.title.lower() or "skins" in submission.title.lower()):

            #reply to the post
            #API Key Redacted Below
            headers = {'x-api-key':""}
            gottenFromAPI = False
            while (not gottenFromAPI):
                r = requests.get('https://fnbr.co/api/shop', headers=headers)
                # Handle any errors stemmed from API not returning properly
                # Done by catching exceptions (when error happens) and waiting to try again. When it succeeds, the loop will break and everything continues
                try:
                    jsonOfShop = r.json()
                except ValueError:
                    print("No Data Recieved - waiting then trying again")
                    time.sleep(5)
                else:
                    gottenFromAPI = True
                    print("Success - continuing script")

            #Google Sheets API
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
            client = gspread.authorize(creds)

            outfits = client.open('Fortnite Shop History').get_worksheet(0)
            pickaxes = client.open('Fortnite Shop History').get_worksheet(1)
            gliders = client.open('Fortnite Shop History').get_worksheet(2)
            emotes = client.open('Fortnite Shop History').get_worksheet(3)

            commentString = "Last time each item was in the shop:\n\n"
            currDate = jsonOfShop['data']['date']
            currDateFormatted = str(currDate[:currDate.find('T')])


            featured = jsonOfShop['data']['featured']
            for i in featured:
                print("* [" + i['name'] + "](" + i['images']['icon'] + ")")
                currString = "* [" + i['name'] + "](" + i['images']['icon'] + ") - "
                #IF BLOCK TO DETERMINE WHICH SHEET TO CHECK
                dateAndDaysSince = "N/A"
                currCell = None
                if i['readableType'] == "Outfit":
                    currCell = outfits.find(i['name'])
                    rowNum = currCell.row
                    dateOfLastTime = outfits.cell(rowNum,4).value
                    if dateOfLastTime == "???":
                        dateAndDaysSince = "NEW\n\n"
                    else:
                        dateAndDaysSince = dateOfLastTime + ", " + outfits.cell(rowNum,5).value + " days ago\n\n"
                    #update cell
                    #change date
                    outfits.update_cell(rowNum,4,currDateFormatted)
                    outfits.update_cell(rowNum,6,str(int(outfits.cell(rowNum,6).value)+1))
                elif i['readableType'] == "Pickaxe":
                    currCell = pickaxes.find(i['name'])
                    rowNum = currCell.row
                    dateOfLastTime = pickaxes.cell(rowNum,4).value
                    if dateOfLastTime == "???":
                        dateAndDaysSince = "NEW\n\n"
                    else:
                        dateAndDaysSince = dateOfLastTime + ", " + pickaxes.cell(rowNum,5).value + " days ago\n\n"
                    #update cell
                    #change date
                    pickaxes.update_cell(rowNum,4,currDateFormatted)
                    pickaxes.update_cell(rowNum,6,str(int(pickaxes.cell(rowNum,6).value)+1))
                elif i['readableType'] == "Glider":
                    currCell = gliders.find(i['name'])
                    rowNum = currCell.row
                    dateOfLastTime = gliders.cell(rowNum,4).value
                    if dateOfLastTime == "???":
                        dateAndDaysSince = "NEW\n\n"
                    else:
                        dateAndDaysSince = dateOfLastTime + ", " + gliders.cell(rowNum,5).value + " days ago\n\n"
                    #update cell
                    #change date
                    gliders.update_cell(rowNum,4,currDateFormatted)
                    gliders.update_cell(rowNum,6,str(int(gliders.cell(rowNum,6).value)+1))
                elif i['readableType'] == "Emote":
                    currCell = emotes.find(i['name'])
                    rowNum = currCell.row
                    dateOfLastTime = emotes.cell(rowNum,4).value
                    if dateOfLastTime == "???":
                        dateAndDaysSince = "NEW\n\n"
                    else:
                        dateAndDaysSince = dateOfLastTime + ", " + emotes.cell(rowNum,5).value + " days ago\n\n"
                    #update cell
                    #change date
                    emotes.update_cell(rowNum,4,currDateFormatted)
                    emotes.update_cell(rowNum,6,str(int(emotes.cell(rowNum,6).value)+1))
                else:
                    dateAndDaysSince = "N/A\n\n"
                currString = currString + dateAndDaysSince
                commentString = commentString + currString

            daily = jsonOfShop['data']['daily']
            for i in daily:
                print("* [" + i['name'] + "](" + i['images']['icon'] + ")")
                currString = "* [" + i['name'] + "](" + i['images']['icon'] + ") - "
                #IF BLOCK TO DETERMINE WHICH SHEET TO CHECK
                dateAndDaysSince = "N/A"
                currCell = None
                if i['readableType'] == "Outfit":
                    currCell = outfits.find(i['name'])
                    rowNum = currCell.row
                    dateOfLastTime = outfits.cell(rowNum,4).value
                    if dateOfLastTime == "???":
                        dateAndDaysSince = "NEW\n\n"
                    else:
                        dateAndDaysSince = dateOfLastTime + ", " + outfits.cell(rowNum,5).value + " days ago\n\n"
                    #update cell
                    #change date
                    outfits.update_cell(rowNum,4,currDateFormatted)
                    outfits.update_cell(rowNum,6,str(int(outfits.cell(rowNum,6).value)+1))
                elif i['readableType'] == "Pickaxe":
                    currCell = pickaxes.find(i['name'])
                    rowNum = currCell.row
                    dateOfLastTime = pickaxes.cell(rowNum,4).value
                    if dateOfLastTime == "???":
                        dateAndDaysSince = "NEW\n\n"
                    else:
                        dateAndDaysSince = dateOfLastTime + ", " + pickaxes.cell(rowNum,5).value + " days ago\n\n"
                    #update cell
                    #change date
                    pickaxes.update_cell(rowNum,4,currDateFormatted)
                    pickaxes.update_cell(rowNum,6,str(int(pickaxes.cell(rowNum,6).value)+1))
                elif i['readableType'] == "Glider":
                    currCell = gliders.find(i['name'])
                    rowNum = currCell.row
                    dateOfLastTime = gliders.cell(rowNum,4).value
                    if dateOfLastTime == "???":
                        dateAndDaysSince = "NEW\n\n"
                    else:
                        dateAndDaysSince = dateOfLastTime + ", " + gliders.cell(rowNum,5).value + " days ago\n\n"
                    #update cell
                    #change date
                    gliders.update_cell(rowNum,4,currDateFormatted)
                    gliders.update_cell(rowNum,6,str(int(gliders.cell(rowNum,6).value)+1))
                elif i['readableType'] == "Emote":
                    currCell = emotes.find(i['name'])
                    rowNum = currCell.row
                    dateOfLastTime = emotes.cell(rowNum,4).value
                    if dateOfLastTime == "???":
                        dateAndDaysSince = "NEW\n\n"
                    else:
                        dateAndDaysSince = dateOfLastTime + ", " + emotes.cell(rowNum,5).value + " days ago\n\n"
                    #update cell
                    #change date
                    emotes.update_cell(rowNum,4,currDateFormatted)
                    emotes.update_cell(rowNum,6,str(int(emotes.cell(rowNum,6).value)+1))
                else:
                    dateAndDaysSince = "N/A\n\n"
                currString = currString + dateAndDaysSince
                commentString = commentString + currString

            bottomText = "---\n\nSince people always wonder/complain about skins not appearing enough, I'm keeping a spreadsheet of the last time each item was in the shop.\n\n[**Link to Spreadsheet**](https://docs.google.com/spreadsheets/d/1vsascLSC9ynd6JFEgaIbolFPSYUXz-xgigvTjiANxkU/edit?usp=sharing)\n\n---\n\n^(Special Thanks to fnbr.co for allowing me to use their API)"

            commentString = commentString + bottomText

            submission.reply(commentString)

            print("Bot replying to: ", submission.title)

            # store the current id into our list
            posts_replied_to.append(submission.id)

            # NOW UPDATE THE SHEET BOIIIII


with open("posts_replied_to.txt", "w") as f:
    for post_id in posts_replied_to:
        f.write(post_id + "\n")
