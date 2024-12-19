from scapy.all import *
from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import ARP, Ether
import threading
import datetime
import os

IP_MAC_PAIRS = {}
ARP_REQ_TABLE = {}
BLOCKED_MACS = set()
LOG_FILE = "log_arp.txt"

def log_message(message):
    # Add +7 hours to the current timestamp
    timestamp = (datetime.datetime.now() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())  # Print to console
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry)

def sniff_requests():
    sniff(filter='arp', lfilter=outgoing_req, prn=add_req, iface=conf.iface)

def sniff_replies():
    sniff(filter='arp', lfilter=incoming_reply, prn=check_arp_header, iface=conf.iface)

def incoming_reply(pkt):
    return pkt[ARP].op == 2 and pkt[ARP].psrc != str(get_if_addr(conf.iface))

def outgoing_req(pkt):
    return pkt[ARP].op == 1 and pkt[ARP].psrc == str(get_if_addr(conf.iface))

def add_req(pkt):
    ARP_REQ_TABLE[pkt[ARP].pdst] = datetime.datetime.now()

def check_arp_header(pkt):
    if not pkt[Ether].src == pkt[ARP].hwsrc or not pkt[Ether].dst == pkt[ARP].hwdst:
        return handle_attack(pkt, "Inconsistent ARP message")
    return known_traffic(pkt)

def known_traffic(pkt):
    if pkt[ARP].psrc not in IP_MAC_PAIRS:
        return spoof_detection(pkt)

    if IP_MAC_PAIRS[pkt[ARP].psrc] == pkt[ARP].hwsrc:
        return

    return handle_attack(pkt, "IP-MAC pair mismatch")

def spoof_detection(pkt):
    ip_ = pkt[ARP].psrc
    mac = pkt[ARP].hwsrc
    t = datetime.datetime.now()

    if ip_ in ARP_REQ_TABLE and (t - ARP_REQ_TABLE[ip_]).total_seconds() <= 5:
        ip = IP(dst=ip_)
        SYN = TCP(sport=40508, dport=40508, flags="S", seq=12345)
        E = Ether(dst=mac)

        if not srp1(E / ip / SYN, verbose=False, timeout=2):
            return handle_attack(pkt, "No TCP ACK (Fake IP-MAC pair)")

        IP_MAC_PAIRS[ip_] = mac
    else:
        send(ARP(op=1, pdst=ip_), verbose=False)

def handle_attack(pkt, alarm_type):
    attacker_mac = pkt[ARP].hwsrc
    attacker_ip = pkt[ARP].psrc
    log_message(f"[ALERT] Under Attack: {alarm_type}")
    log_message(f"Attacker IP: {attacker_ip}, MAC: {attacker_mac}")

    if attacker_mac not in BLOCKED_MACS:
        BLOCKED_MACS.add(attacker_mac)
        block_mac(attacker_mac)

    drop_packet(pkt)

def block_mac(mac):
    try:
        os.system(f"iptables -A INPUT -m mac --mac-source {mac} -j DROP")
        log_message(f"[INFO] Blocked MAC address: {mac}")
    except Exception as e:
        log_message(f"[ERROR] Failed to block MAC address: {mac}. Error: {e}")

def drop_packet(pkt):
    log_message(f"[INFO] Dropped spoofed packet from MAC: {pkt[ARP].hwsrc}")

if _name_ == "_main_":
    log_message("Starting ARP spoof detection...")
    req_thread = threading.Thread(target=sniff_requests, args=())
    req_thread.start()

    rep_thread = threading.Thread(target=sniff_replies, args=())
    rep_thread.start()
