#!/usr/bin/python2

import paramiko
import subprocess
import shlex
import re
import os
import time

Node_Info = {
    str('cp'):{ 'nodeName': '',
                        'ip':'',
                       'routing':'/opt/nokia/SS_TestRCPCCSMCU/'},
    str('mn'):{ 'nodeName': '',
                        'ip':'',
                       'routing':'/opt/nokia/SS_TestRCPCCSMCU/'},
    str('ei'):{ 'nodeName': '',
                        'ip':'',
                       'routing':'/opt/nokia/SS_TestRCPCCSRT/'},
    str('up'):{ 'nodeName': '',
                        'ip':'',
                       'routing':'/opt/nokia/SS_TestRCPCCSRT/'}
    }

global Base_Md5sum

def try_SSH():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
    for node in Node_Info.keys():
        client.connect(node,username='robot',password='rastre1')
        print "[+] Try to ssh the destination."
    client.close()

def get_node_IP():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    for node in Node_Info.keys():
        if node != 'mn':
            client.connect(Node_Info[node]['nodeName'],username='robot',password='rastre1')
            stdin,stdout,stderr = client.exec_command('ip address')
            out = stdout.readlines()
            for line in out:
                if '169.254' in line:
                    print line
                    Node_Info[node]['ip'] = str(line.split('inet ')[1].split("/")[0])
        else:
            process = os.popen('ip address')
            output = process.readlines()
            for line in output:
                if '169.254' in line:
                    print line
                    Node_Info[node]['ip'] = str(line.split('inet ')[1].split("/")[0])
    print Node_Info
    print "[+] Get the IP information Successful ,And close the connection!"
    client.close()

def get_node_name():
    command = "sudo dvmcli -n"
    try:
        p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        out, err = p.communicate()
        for lines in out.splitlines():
            print lines.split(" ")[0]
            nodeName = lines.split(" ")[0]
            node = nodeName.split("-")[0]
            node_index = nodeName.split("-")[1]
            if "mn" in node:
                Node_Info['mn']['nodeName'] = str(nodeName) + ".local"
            if 'cp' in node:
                Node_Info['cp']['nodeName'] = str(nodeName) + ".local"
            if 'ei' in node and int(node_index) == 0:
                Node_Info['ei']['nodeName'] = str(nodeName) + ".local"
            if 'up' in nodeName:
                Node_Info['up']['nodeName'] = str(nodeName) + ".local"
               
    except:
        print "get node name failed."

def copyTorobot():
#    original_path = '/opt/nokia/SS_TestRCPCCSMCU/SysComRoute-.xml'
#    now_path = '/home/robot/'
    copyTo = 'sudo cp /opt/nokia/SS_TestRCPCCSMCU/SysComRoute-.xml /home/robot/'
    try:
        os.system(copyTo)
        return 1
    except:
        return 0

def get_md5sum_value(node, path):
    out = os.popen('sudo ssh {node} sudo md5sum {path}'.format(node=node, path=path))
    print "In Node :", node
    print out.read()
    output = out.read()
    md_value = output.split(" ")[0]
    return str(md_value)

def compare_to_md5_value(base_md5sum, compare_md5sum):
    if base_md5sum == compare_md5sum:
        return True
    print "base:", base_md5sum
    print "comapre:", compare_md5sum
    return False

def SendXmlToNode():
    ''' First, send all XML to /home/robot/
        Then, ssh the server,
        finally, cp xml to destination path.'''
    for num in range(3):
        for element in Node_Info.keys():
            os.system('sudo scp /home/robot/SysComRoute-.xml {0}:{1}'.
                      format(Node_Info[element]['nodeName'], Node_Info[element]['routing']))
            os.system('sudo ssh {node} sudo cp -f {route_file}/SysComRoute-.xml /ram'.
                      format(node=Node_Info[element]['nodeName'], route_file=Node_Info[element]['routing']))
            print "Send file to ", Node_Info[element]['nodeName']
            if "up" in element:
                os.system('sudo scp /home/robot/SysComRoute-.xml {0}:/opt/nokia/SS_TestRCPCCSMCU/'.
                          format(Node_Info['up']['nodeName']))
                os.system('sudo ssh {node} sudo cp -f {route_file}/SysComRoute-.xml /ram/MCU'.
                          format(node=Node_Info[element]['nodeName'], route_file=Node_Info["up"]['routing']))
        time.sleep(3)
        compare_md5sum_mn = get_md5sum_value(Node_Info['mn']['nodeName'], "/opt/nokia/SS_TestRCPCCSMCU/SysComRoute-.xml")
        if compare_to_md5_value(Base_Md5sum, compare_md5sum_mn) is False:
            continue
        compare_md5sum_ei = get_md5sum_value(Node_Info['ei']['nodeName'], "/opt/nokia/SS_TestRCPCCSRT/SysComRoute-.xml")
        if compare_to_md5_value(Base_Md5sum, compare_md5sum_ei) is False:
            continue
        compare_md5sum_cp = get_md5sum_value(Node_Info['cp']['nodeName'], "/opt/nokia/SS_TestRCPCCSMCU/SysComRoute-.xml")
        if compare_to_md5_value(Base_Md5sum, compare_md5sum_cp) is False:
            continue
        compare_md5sum_up_rt = get_md5sum_value(Node_Info['up']['nodeName'], "/opt/nokia/SS_TestRCPCCSRT/SysComRoute-.xml")
        if compare_to_md5_value(Base_Md5sum, compare_md5sum_up_rt) is False:
            continue
        compare_md5sum_up_mcu = get_md5sum_value(Node_Info['up']['nodeName'], "/opt/nokia/SS_TestRCPCCSMCU/SysComRoute-.xml")
        if compare_to_md5_value(Base_Md5sum, compare_md5sum_up_mcu) is False:
            continue
        print "Md5sum values equal with others, so the SysComRoute-.xml is replaced successful."
        return
    print "Re-try three times, but still can not copy successful."


if __name__ == '__main__':
#    try_SSH()
    print "Starting get node name >>>>>>>>>"
    get_node_name()
    for node in Node_Info.keys():
        os.system('ssh-keyscan -t rsa {} >> ~/.ssh/known_hosts'.format(Node_Info[node]['nodeName']))
    
    get_node_IP()
    flag = copyTorobot()
    if flag == 1:
        print "[+] Copying file to /home/robot. Running Success."
    else:
        print "[-] Copying file to /home/robot. Running Failed."

    file1 = open('/home/robot/SysComRoute-.xml','r+')
    file2 = open('/home/robot/tmp.xml','w+')
    
    ei = str(Node_Info['ei']['ip'])
    print ei
    up = str(Node_Info['up']['ip'])
    print up
    cp = str(Node_Info['cp']['ip'])
    print cp
    mn = str(Node_Info['mn']['ip'])
    print mn
    output = file1.readlines()
    for line in output:
        if 'rsic="0x1190ffff"' in line and 'lsic="0x1180ffff"' not in line:
            line = line.replace("29214", "29210")
        if 'lsic="0x1190ffff"' in line and 'rsic="0x1160ffff"' in line:
            line = line.replace("10.5.5.9", "127.0.0.1")
            line = line.replace("10.5.5.6:29214", "127.0.0.1:29212")
        if 'lsic="0x1190ffff"' in line and 'rsic="0x1140ffff"' in line:
            line = line.replace("10.5.5.9:29214", "127.0.0.1:29215")
            line = line.replace("10.5.5.4:29214", "127.0.0.1:29212")
        if 'lsic="0x1190ffff"' in line and 'rsic="0x1150ffff"' in line:
            line = line.replace("10.5.5.9:29214", "127.0.0.1:29216")
            line = line.replace("10.5.5.5:29214", "127.0.0.1:29212")
        if 'lsic="0x1190ffff"' in line and 'rsic="0x1180ffff"' in line:
            line = line.replace("10.5.5.9", "127.0.0.1")
            line = line.replace("10.5.5.8", "127.0.0.1")
        if 'lsic="0x1180ffff"' in line and 'rsic="0x1190ffff"' in line:
            line = line.replace("10.5.5.9", "127.0.0.1")
            line = line.replace("10.5.5.8", "127.0.0.1")
        try:
            if len(ei) > 5:
                line = line.replace("10.5.5.6",ei)
            if len(cp) > 5:
                line = line.replace("10.5.5.5",cp)
            if len(mn) > 5:
                line = line.replace("10.5.5.4",mn)
            if len(up) > 5:
                line = line.replace("10.5.5.8",up)
                line = line.replace("10.5.5.9",up)
        except:
            print "[-] Replace failed."
        file2.write(line)

    file1.close()
    file2.close()
    
    try:
        command = "sudo mv /home/robot/tmp.xml /home/robot/SysComRoute-.xml"
        os.system(command)
        os.system("sudo chown _nokrcpsysccs:_nokrcpsysccs /home/robot/SysComRoute-.xml")
        print "[+] Move the File Success!"
    except:
        print "[-] Move the File Failed!"

    global Base_Md5sum
    Base_Md5sum = get_md5sum_value(Node_Info['mn']['nodeName'], "/home/robot/SysComRoute-.xml")
    SendXmlToNode() 
    print "[+] The environment is deployed Successful!"
    print "[+] Reboot Now!!!!!"
    os.system('sudo reboot')
