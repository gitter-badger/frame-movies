# to do:
#  add top of file
#  test in morning
#  add token to ignore the image_id sequence in create_movie
#  add logging
#

import pymysql 
import os, sys
import glob as g
from create_movie import create_movie, logger
import getpass

me=getpass.getuser()

if me == "ops":
	topdir="/ngts"
	convert_loc="/usr/local/bin"
	cron_dir="/usr/local/cron"
	web_dir="/home/ops/ngts/prism/monitor/img"
else:
	print "Whoami!?"
	sys.exit(1)

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

# this should really come from the db...
# where is the camera now, use that das machine?
# cam/das map
das={801:None,
	802:"das06",
	803:"das09",
	804:"das04",
	805:None,
	806:None,
	807:None,
	808:None,
	809:None,
	810:None,
	811:None,
	812:None,
	899:None}
	
# connect to database
conn=pymysql.connect(host='ds',db='ngts_ops')
cur=conn.cursor()
		
# get the actions from yesterday
qry="SELECT action_id,camera_id,action FROM action_list WHERE schedule_start_utc BETWEEN date_sub(now(), INTERVAL 1 DAY) AND now()"
cur.execute(qry)
			
# get the action ids for each camera (and dome 899)
for row in cur:
	if row[2] != 'stow':
		cams[row[1]].append("action%s_%s" % (row[0],row[2]))

os.chdir(topdir)	
for cam in cams:
	if len(cams[cam]) > 0 and cam != 899:
		# go into the last action directory
		if das[cam] != None:
			os.chdir("%s/%s" % (das[cam],cams[cam][-1]))
		
			# get the last image
			t=sorted(g.glob('*.fits'))
			pngfile="%s.png" % (t[-1].split(".")[0])
			
			if len(t)>0 and pngfile not in os.listdir('%s/last_imgs/%s/' % (cron_dir,cam)):
				create_movie([t[-1]],images_directory='%s/last_imgs/%s' % (cron_dir,cam),
					no_time_series=True,include_increment=False)
			
				here=os.getcwd()
				os.chdir("/usr/local/cron/last_imgs/%s" % (cam))
				t2=sorted(g.glob('*.png'))
				
				try:
					f=open('last_img.log').readline()
				except IOError:
					f="XXX"
				
				if f != t2[-1]:
					os.system('cp %s %s/cam_%s.png' % (t2[-1],web_dir,cam))
					f3=open('last_img.log','w')
					f3.write(t2[-1])
					f3.close()
				else:
					print "Last image already up to date, skipping..."
				
				os.chdir(here)
			
			else:
				print "No new fits images to convert, skipping %s..." % (das[cam])
			
			os.chdir('../../')

