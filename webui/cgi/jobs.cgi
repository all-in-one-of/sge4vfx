#!/code/devtools/centos5.5/python-2.6.6/bin/python

import cgi

print "Content-type:text/html\r\n\r\n"

import psycopg2
import datetime
import urllib

import sgewebuisettings

rvInstalled = True
rvString = "Opening RV.  Please wait..."

priorities = {None: 'Normal',
	-600: 'Whenever',
	-300: 'Low',
	0: 'Normal',
	300: 'High',
	600: 'Highest'}

# Get the CGI values from the form submission
vals_in = cgi.FieldStorage()
sortby = vals_in.getvalue("sortby")
sortdir = vals_in.getvalue("sortdir")
if vals_in.has_key("username"):
	user = vals_in.getvalue("username")
else:
	user = ""
if vals_in.has_key("projname"):
	project = vals_in.getvalue("projname")
else:
	project = ""
if vals_in.has_key("done"):
	done = True
else:
	done = False
if vals_in.has_key("running"):
	running = True
else:
	running = False
if vals_in.has_key("error"):
	error = True
else:
	error = False
if vals_in.has_key("wait"):
	wait = True
else:
	wait = False
if vals_in.has_key("limit"):
	hasLimit = True
	limit = vals_in.getvalue("limit")
else:
	hasLimit = False
if vals_in.has_key("offset"):
	hasOffset = True
	offset = vals_in.getvalue("offset")
else:
	hasOffset = False
if vals_in.has_key("namesearch"):
	nameSearch = vals_in.getvalue("namesearch")
else:
	nameSearch = ""

# Connect to the Postgres DB
conn = psycopg2.connect("dbname=%s user=%s host=%s" % (sgewebuisettings.dbname,
	sgewebuisettings.user, sgewebuisettings.host))
cur = conn.cursor()

# Compose the query using all the submitted filters
gotawherealready=False
gotastatusalready=False
psqlcommand = ""
if user != "":
	psqlcommand += "WHERE username='" + user + "' "
	gotawherealready = True
if project != "":
	if gotawherealready:
		psqlcommand += "AND project='" + project + "' "
	else:
		psqlcommand += "WHERE project='" + project + "' "
	gotawherealready = True
if nameSearch != "":
	if gotawherealready:
		psqlcommand += "AND jobname LIKE '%" + nameSearch + "%' "
	else:
		psqlcommand += "WHERE jobname LIKE '%" + nameSearch + "%' "
	gotawherealready = True
if done:
	if gotawherealready:
		psqlcommand += "AND (status=3 "
	else:
		psqlcommand += "WHERE (status=3"
	gotawherealready = True
	gotastatusalready = True
if running:
	if gotastatusalready:
		psqlcommand += "OR status=1 "
	else:
		if gotawherealready:
			psqlcommand += "AND (status=1 "
		else:
			psqlcommand += "WHERE (status=1"
	gotawherealready = True
	gotastatusalready = True
if wait:
	if gotastatusalready:
		psqlcommand += "OR status=0 "
	else:
		if gotawherealready:
			psqlcommand += "AND (status=0 "
		else:
			psqlcommand += "WHERE (status=0"
	gotawherealready = True
	gotastatusalready = True
if error:
	if gotastatusalready:
		psqlcommand += "OR status=2 "
	else:
		if gotawherealready:
			psqlcommand += "AND (status=2 "
		else:
			psqlcommand += "WHERE (status=2 "
	gotawherealready = True
	gotastatusalready = True
if gotastatusalready:
	psqlcommand += ") "
psqlcommand_end = "ORDER BY " + sortby + " " + sortdir + " "
if hasLimit:
	psqlcommand_end += "LIMIT " + limit + " "
	if hasOffset:
		psqlcommand_end += "OFFSET " + offset + " "

jobRecordsQuery = "SELECT * FROM jobs " + psqlcommand + psqlcommand_end + ";"
countQuery = "SELECT count(*) FROM jobs " + psqlcommand + ";"

# Execute the SQL query
cur.execute(jobRecordsQuery)
zebra = False
today = datetime.date.today()
todayStr = today.strftime("%d %b")
for record in cur:
	[sgeid, jobname, username, project, priority, submittime, starttime,
		endtime, firsttask, lasttask, chunk, status,
		submissionscript, donetasks, stdout, stderr] = record
	sgeid = str(sgeid)

	# Format the dates into strings if not Null
	oldDate = ""
	newDate = ":%S"
	if todayStr != submittime.strftime("%d %b"):
		oldDate = "%d %b "
		newDate = ""
	submittimestr = submittime.strftime(oldDate + "%H:%M" + newDate)
	submittimetitle = submittime.strftime("%d %b %H:%M:%S")

	if starttime is not None:
		oldDate = ""
		newDate = ":%S"
		if todayStr != starttime.strftime("%d %b"):
			oldDate = "%d %b "
			newDate = ""
		starttimestr = starttime.strftime(oldDate + "%H:%M" + newDate)
		starttimetitle = starttime.strftime("%d %b %H:%M:%S")
		starttimealt = starttime.strftime("%m")
	else:
		starttimestr = "-"
		starttimetitle = ""
		starttimealt = ""
	if endtime is not None:
		oldDate = ""
		newDate = ":%S"
		if todayStr != endtime.strftime("%d %b"):
			oldDate = "%d %b "
			newDate = ""
		endtimestr = endtime.strftime(oldDate + "%H:%M" + newDate)
		endtimetitle = endtime.strftime("%d %b %H:%M:%S")
		duration = endtime - starttime
		s = duration.seconds + (duration.days * 86400)
		hours, remainder = divmod(s, 3600)
		minutes, seconds = divmod(remainder, 60)
		if (hours > 0):
			durationstr = '%sh %sm %ss' % (hours, minutes, seconds)
		elif (minutes > 0):
			durationstr = '%sm %ss' % (minutes, seconds)
		else:
			durationstr = '%ss' % (seconds)
		realtimeupdate = ""
	else:
		endtimestr = "-"
		durationstr = "-"
		realtimeupdate = " class=\"rtupdate\""

	# Put in the appropriate status classes
	if status == 1:
		statusclass = "running"
	elif status == 2:
		statusclass = "error"
	elif status == 3:
		statusclass = "completed"
	else:
		statusclass = ""

	# Zebra stripe the rows
	if zebra:
		tempstring = "<tr onclick=\"addJobTab(" + sgeid + ");\""
		tempstring += "id=\"row" + sgeid + "\" class=\"" + statusclass
		tempstring += " zebra\">"
	else:
		tempstring = "<tr onclick=\"addJobTab(" + sgeid + ");\""
		tempstring += "id=\"row" + sgeid + "\" class=\"" + statusclass
		tempstring += "\">"
	zebra = not zebra

	# If RV is installed, look for an output path in the job_extras table
	output_path = ""
	if rvInstalled and donetasks > 0 and status != 2:
		output_path = ""
		cur2 = conn.cursor()
		sqlQuery2 = "SELECT value FROM job_extras WHERE sgeid=" + sgeid
		sqlQuery2 += " AND key = 'output_path';"
		cur2.execute(sqlQuery2)
		for record2 in cur2:
			[tempStr] = record2
			output_path = urllib.quote(tempStr)
		cur2.close

	tempstring += "<td><img class=\"iconbtn\" onclick=\"deleteJob(event, "
	tempstring += sgeid + ");\" src=\"images/delete.png\" title=\"Delete"
	tempstring += " Job\"/>"
	if status != 3:
		tempstring += "<img class=\"iconbtn\" onclick=\"changePriority(event, "
		tempstring += sgeid + ");\" src=\"images/priority.png\" title=\"Change"
		tempstring += " Priority\"/>"
	#tempstring += "<a onclick=\"event.stopPropagation();\" "
	#tempstring += "href=\"http://" + sgewebuisettings.httphost + submissionscript
	#tempstring += "\"><img class=\"iconbtn\" alt=\"Submission Script\""
	#tempstring += " src=\"images/script.png\" /></a>"
	if output_path != "":
		tempstring += "<a onclick=\"event.stopPropagation(); "
		tempstring += "toast('RV','" + rvString + "');\" "
		tempstring += "href=\"rvlink://" + output_path + "\">"
		tempstring += "<img class=\"iconbtn\" src=\"images/film.png\" "
		tempstring += "title=\"Preview in RV\"/></a>"
	if status == 2:
		tempstring += "<img class=\"iconbtn\" onclick=\"retry(event, "
		tempstring += sgeid + ")\" src=\"images/retry.png\" "
		tempstring += "title=\"Retry errors\"/>"
	tempstring += "</td><td>" + sgeid
	tempstring += "</td><td>" + jobname
	tempstring += "</td><td>" + username
	tempstring += "</td><td>" + str(project)
	tempstring += "</td><td>" + priorities.get(priority, "Unknown")
	tempstring += "</td><td title=\"" + submittimetitle + "\">" + submittimestr
	tempstring += "</td><td title=\"" + starttimetitle + "\" alt=\""
	tempstring += starttimealt + "\" class=\"starttime\">" + starttimestr
	tempstring += "</td><td title=\"" + starttimetitle + "\">" + endtimestr
	# Only auto-update durations that aren't already known
	if durationstr == "-" and starttimestr != "-":
		tempstring += "</td><td" + realtimeupdate + ">" + durationstr
	else:
		tempstring += "</td><td>" + durationstr
	tempstring += "</td><td>" + str(firsttask) + "-" + str(lasttask) + ":" + str(chunk)

	percentdone = (float(donetasks) / (float(lasttask) - float(firsttask) + 1.0)) * 100.0

	tempstring += "</td><td class=\"percentdone\">" + str(int(percentdone)) + "% (" + str(donetasks) + ")"
	tempstring += "</td></tr>"
	print tempstring

count = 0
cur.execute(countQuery)
for record in cur:
	[count] = record
	tempstring = "<tr class=\"hiddencountrow\">"
	tempstring += "<td id=\"hiddencount\">" + str(count) + "</td></tr>"
	print tempstring

cur.close()
conn.close()
