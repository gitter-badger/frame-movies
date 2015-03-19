# script to work out the actions from the previous night

import pymysql 

# connect to database
conn=pymysql.connect(host='ds',db='ngts_ops')
cur=conn.cursor()

qry="SELECT * FROM action_list WHERE schedule_start_utc BETWEEN date_sub(now(), INTERVAL 1 DAY) AND now()"
cur.execute(qry)

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
	812:[]}


for row in cur:
	cams[row[1]].append("%s_%s" % (row[0],row[4]))
	
