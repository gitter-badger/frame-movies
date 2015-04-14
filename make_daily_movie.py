#!/usr/bin/env python
###############################################################################
#                                                                             #
#            Script to make a movie from the previous night's images          #
#                                    v1.1                                     #
#                               James McCormac                                #
#                                                                             #
# Version History:                                                            #
#	20150319	v1.0	Code written                                          #
#   20150321	v1.1	Added montaging + logger                              #
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
#	add movie making with ffmpeg (generate_movie)
#	add a timer for the whole process
#

import os, os.path, datetime
import pymysql 
import logging
import glob as g
from create_movie import create_movie, generate_movie, logger
import numpy as np
import getpass
import argparse as ap

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

def ArgParse():
	parser=ap.ArgumentParser()
	parser.add_argument("--pngs",help="make the PNG files",action="store_true")
	parser.add_argument("--montage",help="montage all PNG files",action="store_true")
	parser.add_argument("--movie",help="make movie from montaged PNG files",action="store_true")
	args=parser.parse_args()
	return args


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
		qry="SELECT action_id,camera_id,action FROM action_list WHERE schedule_start_utc BETWEEN date_sub(now(), INTERVAL 1 DAY) AND now()"
		cur.execute(qry)
			
		# get the action ids for each camera (and dome 899)
		for row in cur:
			if row[2] != 'stow':
				cams[row[1]].append("action%s_%s" % (row[0],row[2]))
		
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
			logger.info(movie_dir)
			for j in cams[i]:
				logger.info("%s%s/%s/*.fits" % (top_dir,das[i],j))
				t=sorted(g.glob('%s%s/%s/*.fits' % (top_dir,das[i],j)))
				
				camera_movie_dir=movie_dir+das[i]
				create_movie(t,images_directory=camera_movie_dir,include_increment=False,clobber_images_directory=False,resize_factor=4)


def getDatetime(t):
	'''
	get the date and time from a raw image filename
	and create a datetime variable
	'''
	ychk=int(t[8:12])
	mthchk=int(t[12:14])
	dchk=int(t[14:16])
	hchk=int(t[16:18])
	minchk=int(t[18:20])
	schk=int(t[20:22])
	
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
	logger.info("Moving to: " + os.getcwd())
	
	# empty lists for various things	
	t_refs=[]
	das_tracker=[]
	imlens=[]
	
	##############################
	# scan all folders looking for 
	# earliest image of the night
	##############################

	for i in das:
		if das[i] != None:
			os.chdir(das[i])
			logger.info("Moving to: " + os.getcwd())
			
			t=sorted(g.glob('*.png'))
			if len(t) == 0:
				os.chdir('../')
				logger.info("Moving to: " + os.getcwd())
				continue
			
			x=getDatetime(t[0])				
			t_refs.append(x)
			imlens.append(len(t))
			das_tracker.append(das[i])
			
			os.chdir('../')
			logger.info("Moving to: " + os.getcwd())
	
	# list of earliest times per camera
	# and length of imaging run		
	t_refs=np.array(t_refs)		
	imlens=np.array(imlens)
	
	# now work out which was the earliest and go there to start the time series
	n=np.where(t_refs==min(t_refs))[0]
	if len(n) > 1:
		n=n[0]
	logger.info("Reference DAS machine: " + das_tracker[n])

	##############################
	# start in earliest folder and
	# generate a list of reference times
	##############################	
	
	os.chdir(das_tracker[n])
	logger.info("Moving to: " + os.getcwd())

	# these are the time slots, match the other images to start with a certain slot
	slots=np.arange(0,imlens[n],1)
	
	# reset t_refs for start_id calculations
	t=sorted(g.glob('*.png'))
	t_refs=[]
	for i in range(0,len(t)):		
		x=getDatetime(t[i])
		t_refs.append(x)
	
	os.chdir('../')
	logger.info("Moving to: " + os.getcwd())
	
	
	##############################
	# now go through each other dir and
	# generate their starting points
	##############################
	
	for i in das:
		if das[i] != None:
			os.chdir(das[i])
			logger.info("Moving to: " + os.getcwd())
			
			t=sorted(g.glob('*.png'))
			if len(t) == 0:
				os.chdir('../')
				logger.info("Moving to: " + os.getcwd())
				continue
				
			x=getDatetime(t[0])	
			diff=[]
			for j in range(0,len(t_refs)):
				diff.append(abs((t_refs[j]-x).total_seconds()))
			
			z=diff.index(min(diff))
			start_id[i]=z
			
			os.chdir('../')
			logger.info("Moving to: " + os.getcwd())
	
	logger.info("Dictionary of start_ids:")
	logger.info(start_id)
	
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
	
	# keep a dictionary of the directory contents from 
	# first glob as to not check each time we loop around...
	t={801:[],
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
		812:[]}
	
	for i in range(0,run_len):
		files=""
		
		for j in das:
			if i==0:
				if das[j] != None:
					t[j].append(sorted(g.glob('%s/*.png' % (das[j]))))
				else:
					t[j].append([])
			
			if start_id[j] == -1 or i < start_id[j]:
				files=files+"empty/empty.png "
			else:
				try:
					files=files+t[j][0][i-start_id[j]]+" " 
				except IndexError:
					files=files+"empty/empty.png "
					
		logger.debug("[%d/%d] %s" % (i+1,run_len,files))
		
		# now montage them together
		comm="montage %s -tile 6x2 -geometry 400x300-50+3 tiled_%05d.png" % (files,i)
		logger.debug(comm)
		os.system(comm)


def make_movie(movie_dir,movie):
	generate_movie(movie_dir,movie)
	

def main():	
	args=ArgParse()
	if args.pngs:
		make_pngs()
	if args.montage:
		make_montage(movie_dir,das)
	if args.movie:
		make_movie(movie_dir,"movie")

if __name__=='__main__':
	main()			
	
