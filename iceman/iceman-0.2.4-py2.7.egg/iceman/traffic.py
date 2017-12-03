# -*- coding: utf-8 -*-
"""iceman/traffic/traffic.py
"""
import importlib
from scapy.layers.inet import IP, Raw

class Traffic(object):
    """
    :param protocol: tcp or udp
    :type queue: str

    :param queue: nfqueue number
    :type queue: int

    :param cipher_suite: crypto wrapper cipher strategy
    :type cipher_suite: instance

    :param encryption_enabled: encryption flag
    :type encryption_enabled: bool
    """

    def __init__(self, protocol, port, queue, cipher_suite, encryption_enabled=True):

        protocol_module = importlib.import_module("scapy.layers.inet")
        protocol_klass = getattr(protocol_module, protocol.upper())
        self.protocol = protocol_klass

        self.cipher_suite = cipher_suite
        self.encryption_enabled = encryption_enabled
        self.port = port
        self.queue = queue
        self.packets = {}

    def callback(self, nfpacket):
        """NetfilterQueue callback set to decide packets directed from iptables.

        If the packet is modified then the length and layer 4 checksums are reset
        and the nfpacket payload is set to the modified packet

        :param nfpacket:
        :type netfilterqueue: <class 'NetfilterQueue'>
        """
        packet = IP(nfpacket.get_payload())

        dup = self.transform(packet)

        if dup != IP(nfpacket.get_payload()):
            del dup[IP].len
            del dup[IP].chksum
            del dup[self.protocol].chksum

            nfpacket.set_payload(str(dup))

        nfpacket.accept()


    def transform(self, packet):
        """This method transforms packets given three conditions:
        1) if the packet is an ack and there was a previous sequence modified,
           then the method will modify ack to accommodate the previously
           changed sequence

        2) if the packet has a raw layer and it contains an ice marker: `_I_`
           then the method will attempt to decrypt the Raw payload

        3) if the packet has a raw layer, it will decrypt the packet

        :param packet:
        :type packet: <class 'Scapy.IP'>
        """
        proto = packet[self.protocol]

        if self.packets.get(str(proto.ack)):
            ack = int(self.packets[str(proto.ack)])
            packet.getlayer(self.protocol).ack = ack
            sack = ack - 1
            packet[self.protocol].options[5] = ('SAck', (sack, ack))

        if packet.haslayer(Raw):
            if self.encryption_enabled:
                raw = packet[Raw]
                old_len = len(raw)

                if raw.load.startswith('_I_'):
                    token = self.cipher_suite.decrypt(raw.load[3:])
                else:
                    token = "_I_{}".format(self.cipher_suite.encrypt(raw.load))

                packet[Raw].load = token

                new_seq = int(packet[self.protocol].seq) + len(packet[Raw])
                expected_ack = int(packet[self.protocol].seq) + old_len
                self.packets[str(new_seq)] = str(expected_ack)

        return packet
