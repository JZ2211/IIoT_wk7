"""
 Save sensor data into a file named with hostname and the date information:
  hostname_log_yyyy_mm_dd.txt. 
 Usage:
  savedata_locally(output, datatype) 
  where output = timestamp + all the data, datatype = field title headings
  
 Modified 7/10/2023
 by Jin Zhu
"""

from os import path
import os
import re
import subprocess
from subprocess import PIPE

##uncomment the next lines if upload the date to a remote Linux box 
#import paramiko


HOSTNAME='192.168.1.1' #IP address of the remote host
USERNAME='pi'  #username that you use to ssh to the remote host
PASSWORD='yourpassword' #ssh password to the remote host

#Data will be save under the dirctory HOMEPATH/hostname. For example, /home/pi/sensor516
HOMEPATH='/home/pi/' #adjust the home path if needed

"""Write to this Rpi locally"""
def savedata_locally(output, datatype): #output = timestamp + all the data, datatype = field title headings
    x=subprocess.run('hostname', stdout=PIPE, universal_newlines=True)
    sname=x.stdout.strip('\n')

    logdate = output.split(',')[0]  #obtain the date information for the log file name
    filename = sname + '_log_' + re.sub('-','_', logdate)+ '.txt' #log file will be named as log_yyyy_mm_dd.txt
    
    if not path.exists(HOMEPATH+sname):  #create the directory for the data if it does not exist yet
        os.mkdir(HOMEPATH+sname)
    os.chdir(HOMEPATH+sname) #change to the right directory for saving data
    if path.exists(filename): #is the file already here?
        #If yes, append the new data to the date log file
        timelog = open(filename, 'a', buffering=1)
        timelog.write(output + "\n")
        timelog.close()     
    else:
        #if not, creat the new file and write the field tilte headings into the date log file first
        timelog = open(filename, 'w', buffering=1)
        timelog.write(datatype + "\n")
        timelog.write(output + "\n")
        timelog.close()
    return
    
def savedata_remotely(output, datatype,extra):
    # get the hostname as the sensor id
    x=subprocess.run('hostname', stdout=PIPE, universal_newlines=True)
    sname=x.stdout.strip('\n')

    extra.append(output)
    #connect to the Linux server/remote Raspberry pi
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #allows for first time ssh
        ssh.connect(hostname=HOSTNAME, username=USERNAME, password=PASSWORD) #make sure the password is correct
        sftp = ssh.open_sftp()
        """Move to right directory"""
        sftp.chdir("sensors")
        if sname in sftp.listdir():
            sftp.chdir(sname)
        else:
            sftp.mkdir(sname)
            sftp.chdir(sname)
        
        for outline in extra:
            """find file"""
            brokenline = outline.split(',')[0].split('-')
            if 'log_'+brokenline[0]+"_"+brokenline[1]+"_"+brokenline[2]+'.txt' in sftp.listdir(): #does the file exist?
                timelog = sftp.file('log_'+times+'.txt', 'a')
                timelog.write(output + "\n")
                timelog.close()
            else:                 #if new file, write the field title headings along with the new sensor data
                timelog = sftp.file('log_'+brokenline[0]+"_"+brokenline[1]+"_"+brokenline[2]+'.txt', 'w')
                timelog.write(datatype)
                timelog.write(output + "\n")
                timelog.close()
        ssh.close()
        extra = []
    except:
        pass
    return extra
    
