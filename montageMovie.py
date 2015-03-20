#!/usr/bin/env python
###############################################################################
#                                                                             #
#                Script to display all images from previous night             #
#                                    v1.0                                     #
#                               James McCormac                                #
#                                                                             #
# Version History:                                                            #
#	20150309	v1.0	Code written                                          #
#                                                                             #
#                                                                             #
###############################################################################
#
# process:
# 	get a list of all the images.
#	check for the earliest, use this as start 
# 	using the file names work out the time range for each camera
# 	sync the start times for cameras going in and with somewhere in the mains timeline
# 	once synced in play image for image until there are none left
# 	fill spaced with the blank images
#
# to do: 
#	fix start of script to look for first image instead of longest run
#
# montage example
# montage *.png -tile 6x2 -geometry 400x300-50+3 tiled.gif
#
# simon makes the pngs and they go somewhere, ideally in one separate directoy
# or in 1 dir per camera. 
#

import numpy as np
import glob as g
import os, datetime

#topdir="/Volumes/DATA/ngts/paranal/saturation_check/23-wasp18b/test_pngs"
topdir="."

os.chdir(topdir)

imlens=np.zeros(12)

# THIS NEEDS CHANGED TO START AT WHICH ONE IS FIRST NOT THE LONGEST!
for i in range(0,12):
	imlens[i]=len(g.glob("%02d/*.png" % (i+1)))
	# find directory with most images, scale to that one
	n=np.where(imlens==max(imlens))[0][0]


os.chdir("%02d/" % (n+1))

# these are the time slots, match the other images to start with a certain slot
slots=np.arange(0,imlens[n],1)

t=g.glob('*.png')
t_refs=[]
for i in range(0,len(t)):
	# split the times up into datetimes
	yref=int(t[i][12:16])
	mthref=int(t[i][16:18])
	dref=int(t[i][18:20])
	
	href=int(t[i][20:22])
	minref=int(t[i][22:24])
	sref=int(t[i][24:26])
	
	x=datetime.datetime(year=yref,month=mthref,day=dref,hour=href,minute=minref,second=sref)
	t_refs.append(x)


# now go through each other dir and generate the starting point
os.chdir('../')

start_id=[]

for i in range(0,12):
	os.chdir("%02d/" % (i+1))
	
	t=g.glob('*.png')
	if len(t) == 0:
		start_id.append(-1)
		os.chdir('../')
		continue
		
	ychk=int(t[0][12:16])
	mthchk=int(t[0][16:18])
	dchk=int(t[0][18:20])
	
	hchk=int(t[0][20:22])
	minchk=int(t[0][22:24])
	schk=int(t[0][24:26])
	
	x=datetime.datetime(year=ychk,month=mthchk,day=dchk,hour=hchk,minute=minchk,second=schk)
	
	diff=[]
	for j in range(0,len(t_refs)):
		diff.append(abs((t_refs[j]-x).total_seconds()))
	
	z=diff.index(min(diff))
	print z
	start_id.append(z)
	
	os.chdir('../')

# need to look for runs starting late and running longer than the longest run...
run_len=int(max(imlens+start_id))

# now create the frame by frame montages
t1=g.glob('01/*.png')
t2=g.glob('02/*.png')
t3=g.glob('03/*.png')
t4=g.glob('04/*.png')
t5=g.glob('05/*.png')
t6=g.glob('06/*.png')
t7=g.glob('07/*.png')
t8=g.glob('08/*.png')
t9=g.glob('09/*.png')
t10=g.glob('10/*.png')
t11=g.glob('11/*.png')
t12=g.glob('12/*.png')

for i in range(0,run_len):
	
	files=""
	
	# 1
	if start_id[0] == -1:
		files=files+"empty/empty_01.png "
	elif i < start_id[0]:
		files=files+"empty/empty_01.png "
	else:
		try:
			files=files+t1[i-start_id[0]]+" " 	
		except IndexError:
			files=files+"empty/empty_01.png "
	
	# 2
	if start_id[1] == -1:
		files=files+"empty/empty_02.png "
	elif i < start_id[1]:
		files=files+"empty/empty_02.png "
	else:
		try:
			files=files+t2[i-start_id[1]]+" " 	
		except IndexError:
			files=files+"empty/empty_02.png "

	# 3
	if start_id[2] == -1:
		files=files+"empty/empty_03.png "
	elif i < start_id[2]:
		files=files+"empty/empty_03.png "
	else:
		try:
			files=files+t3[i-start_id[2]]+" "
		except IndexError:
			files=files+"empty/empty_03.png "
		
	# 4
	if start_id[3] == -1:
		files=files+"empty/empty_04.png "
	elif i < start_id[3]:
		files=files+"empty/empty_04.png "
	else:
		try:
			files=files+t4[i-start_id[3]]+" "
		except IndexError:
			files=files+"empty/empty_04.png "
	
	# 5
	if start_id[4] == -1:
		files=files+"empty/empty_05.png "
	elif i < start_id[4]:
		files=files+"empty/empty_05.png "
	else:
		try:
			files=files+t5[i-start_id[4]]+" "
		except IndexError:
			files=files+"empty/empty_05.png "
	
	# 6
	if start_id[5] == -1:
		files=files+"empty/empty_06.png "
	elif i < start_id[5]:
		files=files+"empty/empty_06.png "
	else:
		try:
			files=files+t6[i-start_id[5]]+" "
		except IndexError:
			files=files+"empty/empty_06.png "
		
	# 7
	if start_id[6] == -1:
		files=files+"empty/empty_07.png "
	elif i < start_id[6]:
		files=files+"empty/empty_07.png "
	else:
		try:
			files=files+t7[i-start_id[6]]+" "
		except IndexError:
			files=files+"empty/empty_07.png "
		
	# 8
	if start_id[7] == -1:
		files=files+"empty/empty_08.png "
	elif i < start_id[7]:
		files=files+"empty/empty_08.png "
	else:
		try:
			files=files+t8[i-start_id[7]]+" "
		except IndexError:
			files=files+"empty/empty_08.png "
		
	# 9
	if start_id[8] == -1:
		files=files+"empty/empty_09.png "
	elif i < start_id[8]:
		files=files+"empty/empty_09.png "
	else:
		try:
			files=files+t9[i-start_id[8]]+" "
		except IndexError:
			files=files+"empty/empty_09.png "
		
	# 10
	if start_id[9] == -1:
		files=files+"empty/empty_10.png "
	elif i < start_id[9]:
		files=files+"empty/empty_10.png "
	else:
		try:
			files=files+t10[i-start_id[9]]+" "
		except IndexError:
			files=files+"empty/empty_10.png "
		
	# 11
	if start_id[10] == -1:
		files=files+"empty/empty_11.png "
	elif i < start_id[10]:
		files=files+"empty/empty_11.png "
	else:
		try:
			files=files+t11[i-start_id[10]]+" "
		except IndexError:
			files=files+"empty/empty_11.png "
		
	# 12
	if start_id[11] == -1:
		files=files+"empty/empty_12.png "
	elif i < start_id[11]:
		files=files+"empty/empty_12.png "
	else:
		try:
			files=files+t12[i-start_id[11]]+" "
		except IndexError:
			files=files+"empty/empty_12.png "
		
	print "[%d/%d]" % (i+1,run_len)
	print files

	# now montage them together
	os.system("montage %s -tile 6x2 -geometry 400x300-50+3 tiled_%04d.png" % (files,i))
	
	
	
	
	