from netmiko  import *
import json
from netaddr import *
import re
from time import *

"""Define Variables"""
host=''
username=''
password=''
VLANBRIEF=''
SVIBRIEF=''
VLAN=''
HSRP=[]
OPSFINTERFACE=''
CONFIG=[]
device = {
     'device_type' :'cisco_ios',
     'host' : host,
     'username' : username,
     'password': password
     }


def listToString(SVI):
    """Return SVI as string"""
    items=''
    for item in SVI:
        items+=item
    return items

"""SAVING CONFIGURATION BEFORE MAKING CHANGES"""
print("\n************************Accessing Device***************************\n")
host=input("Please enter IP or name of the device :")
username=input("Please enter your username :")
password=input("Please enter your password :")
conn=ConnectHandler(device_type ='cisco_ios',host=host,username=username,password=password)


"""print("********Please save configuration before making changes**************")
#Before_Change=''
#print()
Before_change=input("Name your saving config before you make changes?:")
print()
conn.send_config_set(f"copy runn disk0:/{Before_Change}")
print()
print(f"Configuration has been saved under disk0:/{Before_Change}" )
print("******************************************")
print(conn.send_command(f"show flash | in {Before_Change}"))"""
print("**************Confirm what vlans created on the device*************")
print(conn.send_command("show vlan brief\n"))
print(f"\n**********************Creating VLAN********************************\n")

VLAN=input("Please enter the VLAN you want to create : ")

try:
    VLANBRIEF=conn.send_command("show vlan brief" ,use_textfsm=True)
##print(json.dumps(VLANBRIEF,indent=4))
except Exception as ex:
    print()




i=0
VLANEXIST='NO'
try :
    if VLANEXIST=='NO':
        while i < len(VLANBRIEF) :
            VLANEXIST="CREATED"
            for item in VLANBRIEF :
                if item['vlan_id']==VLAN :
                   print()
                   print("Please make sure you reviwed what vlans already existed on the device ??")
                   print()
                   VLANEXIST=input("Do you want to configure SVI (YES/NO) ?:")
                   
                   if VLANEXIST=='YES' :
                     VLANEXIST='YES'
            break
            VLAN=input("Please Enter the VLAN you want to create : ")
            
            i+=1

    if VLANEXIST=='CREATED' :
        VLANCREATION=[]
        VLANCREATION.append('vlan '+ VLAN)
        VLANCREATION.append('desc ' + input(f"Please enter a description of VLAN {VLAN} :"))
        VLANCREATION.append('name ' + input(f"Please enter a name of VLAN {VLAN} :"))
        ##conn.send_config_set(VLANCREATION)
        CONFIG.append(VLANCREATION)
        print()
        print(f"Creating vlan {VLAN} .....")
        print(f"VLAN  {VLAN} has been created!!!")
        print()
    SVIBRIEF=conn.send_command(f"show ip int br | in Vlan{VLAN}", use_textfsm=True)
    print()
    print(f"*********************Confirm SVI {VLAN} not in use*******************")
    #print(SVIBRIEF)
except :
    print()
j=0
k=0


try :
    while j < len(SVIBRIEF) :
        for item in SVIBRIEF :
            if item['intf']=='Vlan'+VLAN :
               print()
               print("SVI has already been created ")
               print()
               print(conn.send_command(f"show run int vlan {VLAN}"))
               k=1
        j+=1
    if (k==0):
         print("---------------------------------------------")
         print(f"There is no SVI associated with VLAN {VLAN}")
         print("---------------------------------------------\n")
except Exception  as ex:
    print()
SVI=[]
OSPF=[]
RID=0
SVIID=0
anti_spoof_ACL=[]
IPADDR=''
IPADDL=''
try :
    SVIID=int(input("Please enter the SVI #:"))
    if SVIID not in range(1,4096):
        print(f"Vlan {VLAN} you entered is not in the range")
        print("Exiting.......")
        exit()
except :
    print("The Vlan number is not correct")
SVIN=str(SVIID)
ISIP=False
try :
    while ISIP==False:
        SVI.append('interface vlan '+SVIN)
        SVI.append('desc  ' + input("please enter a description :"))
        SVI.append("IP address " +input("Please Enter IP Address :")+" "+input("Please enter the mask :"))
        IPADDR=listToString(SVI)
        IPADDR=re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",IPADDR)
        IPADDR=IPADDR.group(0)
        
        if IPAddress(IPADDR).is_unicast() :
            ISIP=True
        print()
        HSRPID=input("Please enter HSRP process ID :")
        HSRPPROCESS=HSRPID + " ip "+input("Please enter the virtual IP:")
        
        SVI.append(" standby " + HSRPPROCESS)
        PREEMPT=''
        PREEMPT=input("Do you want  to enable PREEMPT (YES/NO) ?:")
        if(PREEMPT=='YES'):
           SVI.append(f"standby {HSRPID} preempt")
        SVI.append(f"standby {HSRPID} priority "+input(f"Please enter the priority of standby {HSRPID} :"))
        SVI.append("no shutdown")
        print()
        ##conn.send_config_set(SVI)
        CONFIG.append(SVI)
    OPSFINTERFACE=input("Do you want to enable OSPF in the interface (YES/NO) :")
    if(('YES'or'yes'or'Yes') in OPSFINTERFACE):
        SVI.append("ip ospf "+input("enter OSPF router ID: ")+"  area "+ input("Enter area ID :"))
        #print(SVI)
        print(f"Configuring interface vlan {VLAN} ......")
        conn.send_config_set(SVI)
        print(f"interface vlan {VLAN}  has been configured")
        print()
        print("---------------------------------------------\n")
        print(conn.send_command(f"show run int vlan {VLAN}"))
        print("---------------------------------------------\n")
    else :
        print("***************************Confirming OSPF**********************")
        print()
        print(conn.send_command(" show  run | s router ospf"))
        print()
        print("*************************Configuring OSPF***********************")
        print()
        RID=input("Please enter OSPF router ID :")
        OSPF.append("router ospf "+RID)
        OSPF.append("network "+input ("Please enter network, wildcard mask and area ID :"))
        print()
        print("Configuring OSPF.......\n")
        ##conn.send_config_set(OSPF)
        CONFIG.append(OSPF)
        print("--------------------------------")
        print(conn.send_command(f"show run | s router ospf {RID}"))
        print("--------------------------------")
        print("\n***********************************************************\n")
        
        
except  Exception as ex:
        print(ex)
KEY='YES'
while KEY=='YES'  :
    try  :
        
        
        KEY=input("Do you want to add your newest configigured network into anti-spoof Access-list (YES/NO)?:")
        if KEY=='YES':
                ACLN=input("Please enter the access-list name :")
                anti_spoof_ACL.append("ip access-list  extended "+ACLN)
                print("***********************************************************\n")
                print(conn.send_command(f"show  run | s {ACLN}"))
                print("***********************************************************\n")
                print(conn.send_command(f"show access-l | s {ACLN}"))
                print("***********************************************************\n")
                anti_spoof_ACL.append(input("lease enter sequence #:")+" "+input(" Please enter your attribtues:"))
                print("Configuring Access-list.....\n")
                print(anti_spoof_ACL)
                ##conn.send_config_set(anti_spoof_ACL)
                CONFIG.append(anti_spoof_ACL)
                print(f"**************Confirming Acccess-list{ACLN}******************\n")
                print(conn.send_command(f" show access-list | s {ACLN}"))
                print("***********************************************************\n")
                print("Saving Configuration!!!!!\n")
                conn.send_config_set("wr")
                print("Config has been saved!!!!!\n")
        else :
            break
    except  Exception as ex:
        
            input("Please hit \"Enter\" to exit!!!!")
            print("***********************************************************\n")

PUSH_CONFIG=''
print(json.dumps(CONFIG,indent=4))
PUSH_CONFIG=input(f"Do you want to config device {host} ('YES/NO')?")
if PUSH_CONFIG=="YES":
    conn.send_config_set(CONFIG)

print("\n***********************************************************\n")
input("Please hit \"any key\" to exit!!!!")        




