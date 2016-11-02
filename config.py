'''
This page is meant as just the configuration set up
'''

import datetime
import os
import pandas as pd

## auth expires about every hour
auth = "EAACEdEose0cBAPRmC29kRmCpBEAVqSDv3MwYKMAUIteZCbh4rKR40MFbUrO6VUPi7o5UMmKRzkjVs2reZAQPJh5KFZC2DpxtQkUhTEkGK7fRgZCPZBGyPl5SqpZBX300kfZAgZA0NKga7r4b2YZCYS8PZB88H36KXZAUOQfK50Du1N6XwZDZD"

## name of file, add in location if not in working directory
## comment necessary code block for df on other file
# file_name = "FacebookUser.csv"
file_name = "supercenterinfo.csv"
supercenter_file = True

## how far back do you want to search?
days = 365
## run a test with a specific store
test = True

test_store = "Walmart2037"


## any pages not found add here
does_not_exist = ['Walmart763']



###########################################################################
########## dont edit below here ###################
#############################################################



newpath = os.getcwd()+'/results/'
if not os.path.exists(newpath):
    os.makedirs(newpath)

stop = datetime.timedelta(days=days)
today = datetime.date.today()
time_stop = today-stop
time_stop = time_stop.strftime("%Y-%m-%dT%H:%M:%S+0000")
created_time = today.strftime("%Y-%m-%dT%H:%M:%S+0000")


## find done page ids through the file names
done_files = os.listdir(newpath)
done_files = [i[:i.find('.csv')]for i in done_files]

## find the last file that has been done if
max_mtime = 0
for dirname,subdirs,files in os.walk(newpath):
    for fname in files:
        full_path = os.path.join(dirname, fname)
        mtime = os.stat(full_path).st_mtime
        if mtime > max_mtime:
            max_mtime = mtime
            max_file = fname

