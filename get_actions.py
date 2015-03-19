# script to work out the actions from the previous night
# movies and pngs should go in /ngts/staging/movies/
# ./create_images.py -d /path/to/png_directory `ls /ngts/dasXX/actionYYYY_ZZZZZ/*IMAGE*.fits` 

import pymysql 
import logging
# from create_images import create_images as cimgs

# connect to database
conn=pymysql.connect(host='ds',db='ngts_ops')
cur=conn.cursor()

# get the actions from yesterday
qry="SELECT * FROM action_list WHERE schedule_start_utc BETWEEN date_sub(now(), INTERVAL 1 DAY) AND now()"
cur.execute(qry)

# empty dictionary for the actions for each camera
cams={801:[],
	802:[],
	803:[],
	804:[],
	805:[],
	806:[],
	807:[],
	808:[],
	809:[],
	810:[],
	811:[],
	812:[],
	899:[]}

# set the key to the das machines for each camera
das={801:None,
	802:'das06',
	803:'das09',
	804:'das04',
	805:None,
	806:None,
	807:None,
	808:None,
	809:None,
	810:None,
	811:None,
	812:None}


# get the action ids for each camera (and dome 899)
for row in cur:
	cams[row[1]].append("action%s_%s" % (row[0],row[4]))


# remove the roof entry, not needed
del cams[899]

# now we have the action ids go through and create the images for each 
for i in cams:
	if len(cams[i]) > 0:
		for j in cams[i]:
			print "/ngts/%s/%s/*.fits" % (das[i],j)
			t=g.glob('/ngts/%s/%s/*.fits' % (das[i],j))
			
			
			
	
