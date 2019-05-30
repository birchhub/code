#!/usr/bin/python

#
# IP multicast receiver/sender script
#   * joins group and waits for packets
#   * sends packets
#


import socket
import getopt
import sys

def usage():
    print "./mcast.py [-s/--sender] [-r/--receiver] [-g/--group groupip] [-p/--port port] [-l/--localip localip]"
    print "--receiver.. receive UDP MCASTs, default"
    print "--sender..   send UDP MCASTs instead of receiving"
    print "--group..    MCAST IP/group to use"
    print "--port..     port"
    print "--localip..  local IP (important when having multiple interfaces)"

def main():
    options,_ = getopt.getopt(sys.argv[1:], 'sg:p:l:h', ['sender', 'group=', 'port=', 'localip=', 'help'])

    beSender=False
    port=3141
    mcast_group = "228.31.31.30"
    local_ip = "0.0.0.0"        # default, bind all local IPs

    for opt,arg in options:
        if opt in ('-s', '--sender'):
            beSender=True
        if opt in ('-r', '--receiver'):
            beSender=False
        elif opt in ('-g', '--group'):
            mcast_group=arg
        elif opt in ('-p', '--port'):
            port=int(arg)
        elif opt in ('-l', '--localip'):
            local_ip=arg
        elif opt in ('-h', '--help'):
            usage()
            sys.exit(0)

    if beSender:
        sender(mcast_group,port)
    else:
        receiver(mcast_group,port,local_ip)

def receiver(mcast_group,port,local_ip):
    
    # create udp socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # reuseaddr as usual
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    
    #
    # bind socket to port
    #
    # bind in MCAST case means filtering for this (address,port) combination
    # we could just bind to (0.0.0.0,port), but then all other datagrams to port
    # would be fetched by our socket as well
    sock.bind((mcast_group,port))
   
    #
    # add ourself to the multicast group
    #
    # 3rd paramter: (taken from /usr/include/linux/in.h) has the following members:
    #  struct ip_mreq
    # {
    #         struct in_addr imr_multiaddr;   /* IP multicast address of group */
    #         struct in_addr imr_interface;   /* local IP address of interface */
    # };
    status = sock.setsockopt(socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
            socket.inet_aton(mcast_group) + socket.inet_aton(local_ip))
    
    while 1:
        try:
            data, addr = sock.recvfrom(1024)
            print "From: %s" % str(addr)
            print "Data: %s" % (data)
            print ""
        except socket.error as e:
            pass

def sender(mcast_group, port):
    import scapy.all

    ip_packet = scapy.all.IP(dst=mcast_group)
    udp_packet = scapy.all.UDP(dport=port)
    payload = "LEO LEO LEO\n"

    scapy.all.send(ip_packet/udp_packet/payload)

if __name__ == "__main__":
    main()
