#!/usr/bin/env python
###############################################################################
#                                                                             #
#            Script to make a movie from the previous night's images          #
#                                    v1.0                                     #
#                               James McCormac                                #
#                                                                             #
# Version History:                                                            #
#	20150319	v1.0	Code written                                          #
#   20150321	v1.1	Added montaging                                       #
#                                                                             #
###############################################################################
#
# process:
#	get a list of actions from the previous night
#	use Simon's create_movie code to generate the pngs
#	use imagemagick to montage the pngs (getCameraMovie.py snippet)
#	use ffmpeg to make the movie of the montaged pngs
#
# to do: 
#	add montaging 
#	change montaging to look at start time not longest run
#	add movie making with ffmpeg
#
#

import os, os.path, datetime
import pymysql 
import logging
import glob as g
from create_movie import create_movie as cmovie
import numpy as np

######################################################
###################### Globals #######################
######################################################

movie_dir="/local/movie/"

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

######################################################
##################### Functions ######################
######################################################


def make_pngs(cams,das):
	'''
	Get all the images from yesterday and make pngs 
	for the daily montage. PNGs will be stored in 
	
	/ngts/dasXX/movie/ 
	
	These will be removed each day once the movie is made
	'''
	# connect to database
	conn=pymysql.connect(host='ds',db='ngts_ops')
	cur=conn.cursor()
	
	# get the actions from yesterday
	qry="SELECT * FROM action_list WHERE schedule_start_utc BETWEEN date_sub(now(), INTERVAL 1 DAY) AND now()"
	cur.execute(qry)
		
	# get the action ids for each camera (and dome 899)
	for row in cur:
		cams[row[1]].append("action%s_%s" % (row[0],row[4]))
	
	
	# remove the roof entry, not needed
	del cams[899]
	
	# now we have the action ids go through and create the images for each 
	for i in cams:
		if len(cams[i]) > 0:
			if os.path.exists(movie_dir) == False:
				os.mkdir(movie_dir)	
			print movie_dir
			for j in cams[i]:
				print "/ngts/%s/%s/*.fits" % (das[i],j)
				t=g.glob('/ngts/%s/%s/*.fits' % (das[i],j))
				
				camera_movie_dir=movie_dir+das[i]
				#cmovie(t,images_directory=camera_movie_dir)
	
	return cams, das		


def make_montage(movie_dir,das):
	'''
	montage all the pngs with imagemagick
	'''
	
	os.chdir(movie_dir)
	
	imlens=np.zeros(12)	
	
	# THIS NEEDS CHANGED TO START AT WHICH ONE IS FIRST NOT THE LONGEST!
	for i in range(0,12):
		imlens[i]=len(g.glob("%s/*.png" % (das[i])))
		# find directory with most images, scale to that one
		n=np.where(imlens==max(imlens))[0][0]
	
	os.chdir("%s/" % (das[n]))
	
	# these are the time slots, match the other images to start with a certain slot
	slots=np.arange(0,imlens[n],1)
	
	t=g.glob('*.png')


	# CHECK THIS!!!!  - stop! fix montage
	t_refs=[]
	for i in range(0,len(t)):
		# split the times up into datetimes
		yref=int(t[i][12:16])
		mthref=int(t[i][16:18])
		dref=int(t[i][18:20])
		
		href=int(t[i][20:22])
		minref=int(t[i][22:24])
		sref=int(t[i][24:26])
	
	
	
	
	

	return 0
	

def main():
	cams,das=make_pngs(cams,das)
	#done=make_montage(movie_dir,das)


if __name__=='__main__':
	main()			
	
