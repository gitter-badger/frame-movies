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
import getpass
me=getpass.getuser()

######################################################
###################### Globals #######################
######################################################

if me == 'James':
	movie_dir="/Volumes/DATA/ngts/paranal/12Cams/movie/"
	top_dir="/Volumes/DATA/ngts/paranal/12Cams/"
if me == 'ops':
	movie_dir="/local/movie/"
	top_dir="/ngts/"

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

# start id for movie
start_id={801:-1,
	802:-1,
	803:-1,
	804:-1,
	805:-1,
	806:-1,
	807:-1,
	808:-1,
	809:-1,
	810:-1,
	811:-1,
	812:-1,
	899:-1}

######################################################
##################### Functions ######################
######################################################

def make_pngs():
	'''
	Get all the images from yesterday and make pngs 
	for the daily montage. PNGs will be stored in 
	
	/ngts/dasXX/movie/ 
	
	These will be removed each day once the movie is made
	'''
	if me=='ops':
		# connect to database
		conn=pymysql.connect(host='ds',db='ngts_ops')
		cur=conn.cursor()
		
		# get the actions from yesterday
		qry="SELECT * FROM action_list WHERE schedule_start_utc BETWEEN date_sub(now(), INTERVAL 1 DAY) AND now()"
		cur.execute(qry)
			
		# get the action ids for each camera (and dome 899)
		for row in cur:
			cams[row[1]].append("action%s_%s" % (row[0],row[4]))
		
	if me=='James':
		for i in cams:
			cams[i].append('action100000_focusSweep')
	
	# remove the roof entry, not needed
	del cams[899]
	
	# now we have the action ids go through and create the images for each 
	for i in cams:
		if len(cams[i]) > 0 and das[i] != None:
			if os.path.exists(movie_dir) == False:
				os.mkdir(movie_dir)	
			print movie_dir
			for j in cams[i]:
				print "%s%s/%s/*.fits" % (top_dir,das[i],j)
				t=g.glob('%s%s/%s/*.fits' % (top_dir,das[i],j))
				
				camera_movie_dir=movie_dir+das[i]
				cmovie(t,images_directory=camera_movie_dir)


def getDatetime(t):
	'''
	get the date and time from a raw image filename
	and create a datetime variable
	'''
	ychk=int(t[14:18])
	mthchk=int(t[18:20])
	dchk=int(t[20:22])
	hchk=int(t[22:24])
	minchk=int(t[24:26])
	schk=int(t[26:28])
	
	x=datetime.datetime(year=ychk,month=mthchk,
		day=dchk,hour=hchk,minute=minchk,second=schk)
	
	return x
	

def make_montage(movie_dir,das):
	'''
	sync the pngs according to earliest image that day then
	montage all the pngs with imagemagick
	'''
	
	if os.path.exists(movie_dir) == False:
		os.mkdir(movie_dir)
	
	os.chdir(movie_dir)		
	print "Moving to: " + os.getcwd()
	
	# empty lists for various things	
	t_refs=[]
	das_tracker,camera_tracker=[],[]
	imlens=[]
	
	##############################
	# scan all folders looking for 
	# earliest image of the night
	##############################

	for i in das:
		if das[i] != None:
			os.chdir(das[i])
			print "Moving to: " + os.getcwd()
			
			t=g.glob('*.png')
			if len(t) == 0:
				os.chdir('../')
				print "Moving to: " + os.getcwd()
				continue
			
			x=getDatetime(t[0])				
			t_refs.append(x)
			imlens.append(len(t))
			das_tracker.append(das[i])
			camera_tracker.append(i)
			
			os.chdir('../')
			print "Moving to: " + os.getcwd()
	
	# list of earliest times per camera
	# and length of imaging run		
	t_refs=np.array(t_refs)		
	imlens=np.array(imlens)
	
	# now work out which was the earliest and go there to start the time series
	n=np.where(t_refs==min(t_refs))[0]
	print "Reference DAS machine: " + das_tracker[n]

	##############################
	# start in earliest folder and
	# generate a list of reference times
	##############################	
	
	os.chdir(das_tracker[n])
	print "Moving to: " + os.getcwd()

	# these are the time slots, match the other images to start with a certain slot
	slots=np.arange(0,imlens[n],1)
	
	# reset t_refs for start_id calculations
	t=g.glob('*.png')
	t_refs=[]
	
	for i in range(0,len(t)):		
		x=getDatetime(t[i])
		t_refs.append(x)
	
	os.chdir('../')
	print "Moving to: " + os.getcwd()
	
	
	##############################
	# now go through each other dir and
	# generate their starting points
	##############################
	
	for i in range(0,len(das_tracker)):
		os.chdir(das_tracker[i])
		print "Moving to: " + os.getcwd()
		
		t=g.glob('*.png')
		if len(t) == 0:
			os.chdir('../')
			print "Moving to: " + os.getcwd()
			continue
			
		x=getDatetime(t[0])
			
		diff=[]
		for j in range(0,len(t_refs)):
			diff.append(abs((t_refs[j]-x).total_seconds()))
		
		print diff
		
		z=diff.index(min(diff))
		print z
		start_id[camera_tracker[i]]=z
		
		os.chdir('../')
		print "Moving to: " + os.getcwd()
	
	print "Dictionary of start_ids:"
	print start_id
	
	##############################
	# work out the new video size for
	# non time overlapping images
	##############################
	 
	max_start=0
	for i in start_id:
		if start_id[i]>max_start:
			max_start=start_id[i]
	run_len=int(max(imlens)+max_start)
	
	##############################
	# montage based on start_ids
	##############################

	for i in range(0,run_len):
		files=""
		
		for j in das:
			if das[j] != None:
				t=sorted(g.glob('%s/*.png' % (das[j])))
			else:
				t=[]
			
			if start_id[j] == -1:
				files=files+"empty/empty.png "
			elif i < start_id[j]: 	
				files=files+"empty/empty.png "
			else:
				try:
					files=files+t[i-start_id[j]]+" " 
				except IndexError:
					files=files+"empty/empty.png "
					
		print "[%d/%d]" % (i+1,run_len)
		print files
	
		# now montage them together
		os.system("montage %s -tile 6x2 -geometry 400x300-50+3 tiled_%05d.png" % (files,i))


def main():
	
	pngs = 0
	if pngs > 0:
		make_pngs()
	make_montage(movie_dir,das)


if __name__=='__main__':
	main()			
	