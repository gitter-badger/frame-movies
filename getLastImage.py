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
qry="SELECT action_id,camera_id,action FROM action_list WHERE schedule_start_utc BETWEEN date_sub(now(), INTERVAL 7 DAY) AND now()"
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
			
			if len(t)>0:
				create_movie([t[-1]],images_directory='/usr/local/cron/last_imgs/%s' % (cam))
			else:
				print "No fits images to convert, skipping %s..." % (das[cam])
			
			os.chdir('../../')

# at the end rename all the images to default
os.chdir("/usr/local/cron/last_imgs/")
t=sorted(g.glob("8*"))
for i in range(0,len(t)):
	os.chdir(t[i])
	os.system('mv *IMAGE*.png cam_%s.png' % (t[i]))
	os.chdir('../')

