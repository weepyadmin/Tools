#!/usr/bin/python3.4
# nginx_hit_counter.py v1.0
# Small tool for monitoring nginx log file and sending a hit to Graphite when a page is accessed
# Usage: Feed in nginx access.log file, graphite endpoint, profit.
# Original inspiration taken and expanded on from this post on Stack Overflow (by Jochen Ritzel):
# http://stackoverflow.com/questions/1703640/how-to-implement-a-pythonic-equivalent-of-tail-f
# Written by Pseudophed Trismegistus

import socket, time, os, argparse, sys, datetime

def watch(filename, matchDict):
	f = open(filename, 'r')
	while True:
		new = f.readline()
		
		if new:
			for word in matchDict:
				if word in new:
					yield word
		else:
			time.sleep(1)

def run(hostname, port, protocol, logFile):
	
	matchDict = [
		'GET / ',
		'GET /index.php ',
		'GET /tutorials.php ',
		'GET /tools.php ',
		'GET /contact.php ',
		'GET /repository.php ', 
	]
	for hit_word in watch(logFile, matchDict):
		
		graphiteCounterName = 'weepyadmin.www.total_hits'
		timestamp = datetime.datetime.now().timestamp()
		message = '{} 1 {}'.format(graphiteCounterName, timestamp)
		
		#debug
		#print("UDP target IP:", hostname)
		#print("UDP target port:", port)
		#print("message:", message)
		
		if protocol == 'udp':
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			sock.sendto(bytes(message, "utf-8"), (hostname, port))
		else:
			#fill in TCP stuff at a later time
			print('tcp')
			sys.exit(1)

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Hit Counter for Nginx Access Logs to Feed Metrics to Graphite', prog='nginx_hit_counter.py')
	parser.add_argument('-H', action='store', dest='hostname', help='Graphite Server Hostname', required=True)
	parser.add_argument('-p', action='store', dest='port', help='Graphite Server Port', type=int)
	#parser.add_argument('-u', action='store_true', dest='udp', help='Use UDP instead of TCP to send metrics.')
	parser.add_argument('-f', action='store', dest='filename', help='Nginx Access Log File (i.e. /var/log/nginx/access.log)', required=True)
	parser.add_argument('-v, --version', action='version', version='%(prog)s 1.0')
	
	args = parser.parse_args()
	
	#adding UDP vs TCP in the future... defauling to UDP for now
	#if args.udp:
	#	proto = 'udp'
	#else:
	#	proto = 'tcp'
	
	if args.port:
		port = args.port
	else:
		port = 2003
	
	run(args.hostname, port, 'udp', args.filename)
