#!/usr/local/python/bin/python
###############################################################################
#                                                                             #
#          Script to get the last image from NGTS and display on webpage      #
#                                    v1.0                                     #
#                               James McCormac                                #
#                                                                             #
# Version History:                                                            #
#	20150408	v1.0	Code written and tested on par-ds                     #
#                                                                             #
###############################################################################
#
# process:
#	grab all the actions from 1 day ago, split according to camera
#	go to last action and get the last image
#	only make pngs and upload to webserver if needed
#
# to do:
#  test in morning
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
	cron_dir="/usr/local/cron/work"
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
	813:[],
	899:[]}

# this should really come from the db...
# where is the camera now, use that das machine?
# cam/das map
das={801:None,
	802:None,
	803:None,
	804:None,
	805:None,
	806:None,
	807:None,
	808:None,
	809:None,
	810:None,
	811:None,
	812:None,
	813:None,
	899:None}

def getDasLoc():
	for i in das:
		if i != 899:
			s=os.popen('/usr/local/paladin/bin/ngwhereis %d' % (i)).readline()
			try:
				das[i]=s.split()[0]
			except IndexError:
				das[i]=None
			print s
		
getDasLoc()

# check all machines are up
cont=0
for i in das:
	if das[i]:
		x=os.popen('ping -w 0.2 -c 1 %s' % (das[i])).readlines()
		if ' 0% packet loss' in x[-2]:
			cont+=0
		else:
			cont+=1
			
if cont > 0:
	logger.fatal("MACHINES ARE DOWN - ignoring image generation (NFS issues)")
	sys.exit(1)
	
# connect to database
conn=pymysql.connect(host='ds',db='ngts_ops')
cur=conn.cursor()
		
# get the actions from yesterday
#qry="SELECT action_id,camera_id,action FROM action_list WHERE schedule_start_utc BETWEEN date_sub(now(), INTERVAL 1 DAY) AND now()"
#cur.execute(qry)

os.chdir(topdir)	
for cam in cams:
	qry="SELECT image_id,raw_image_list.camera_id,raw_image_list.action_id,action FROM raw_image_list LEFT JOIN action_list USING (action_id) WHERE raw_image_list.camera_id=%d ORDER BY image_id DESC LIMIT 1 " % (cam)
	cur.execute(qry)
	
	# get the action ids for each camera (and dome 899)
	for row in cur:
		if row[3] != 'stow':
			cams[row[1]].append("action%s_%s" % (row[2],row[3]))
	
	if len(cams[cam]) > 0 and cam != 899:
		# go into the last action directory
		if das[cam] != None:
			os.chdir("%s/%s" % (das[cam],cams[cam][-1]))
			logger.info("Moving to %s/%s" % (das[cam],cams[cam][-1]))
			# get the last image
			t=sorted(g.glob('*.fits'))
			
			if len(t)>0:
			 	pngfile="%s.png" % (t[-1])
				logger.info("PNG file to make is %s.png" % (t[-1]))
			 	if pngfile not in os.listdir('%s/last_imgs/%s/' % (cron_dir,cam)):
					create_movie([t[-1]],images_directory='%s/last_imgs/%s' % (cron_dir,cam),
						no_time_series=True,include_increment=False,clobber_images_directory=False,resize_factor=4)
				
					here=os.getcwd()
					os.chdir("%s/last_imgs/%s" % (cron_dir,cam))
					logger.info("Moving to %s/last_imgs/%s" % (cron_dir,cam))
					
					try:
						f=open('last_img.log').readline()
					except IOError:
						f="XXX"
					logger.info("Last image: %s" % (f))
					
					if f != pngfile:
						os.system('cp %s %s/cam_%s.png' % (pngfile,web_dir,cam))
						logger.info("Copying %s to %s/cam_%s.png" % (pngfile,web_dir,cam))
						f3=open('last_img.log','w')
						f3.write(pngfile)
						f3.close()
						logger.info('last_img.log updated with %s' % pngfile)
												
					else:
						print "Last image already up to date, skipping..."
						logger.info('Last image up to date')
						
					os.chdir(here)
					logger.info('Moving to %s' % (here))
				
				else:
					logger.info('%s exists already, skipping...' % (pngfile))
				
			else:
				logger.info("No new fits images to convert, skipping %s..." % (das[cam]))
			
			os.chdir('../../')
			logger.info('Moving to ../../')
