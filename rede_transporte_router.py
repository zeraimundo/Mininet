#!/usr/bin/env python

import os
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import Node

class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class NetworkTopo(Topo):
    "A network topology with three routers and four hosts."

    def build(self, **_opts):
        # Add routers
        r1 = self.addNode('r1', cls=LinuxRouter, ip='10.0.1.1/24')
        r2 = self.addNode('r2', cls=LinuxRouter, ip='10.0.2.1/24')
        r3 = self.addNode('r3', cls=LinuxRouter, ip='10.0.3.1/24')

        # Add hosts
        h1 = self.addHost('h1', ip='10.0.1.100/24', defaultRoute='via 10.0.1.1')
        h2 = self.addHost('h2', ip='10.0.4.100/24', defaultRoute='via 10.0.4.1')

        enlace = {'cls': TCLink, 'bw': 1000}

        # Add links between routers
        self.addLink(r1, r2, intfName1='r1-eth2', intfName2='r2-eth1', **enlace)
        self.addLink(r2, r3, intfName1='r2-eth2', intfName2='r3-eth2', **enlace)

        # Add links between hosts and routers
        self.addLink(h1, r1, intfName2='r1-eth1', **enlace)
        self.addLink(h2, r3, intfName2='r3-eth1', **enlace)

def run():
    "Test network topology"
    topo = NetworkTopo()
    net = Mininet(topo=topo, waitConnected=True)

    net.start()

    # Configure the interfaces on the routers
    net['r1'].cmd('ifconfig r1-eth1 10.0.1.1/24')
    net['r1'].cmd('ifconfig r1-eth2 10.0.2.1/24')
    net['r2'].cmd('ifconfig r2-eth1 10.0.2.2/24')
    net['r2'].cmd('ifconfig r2-eth2 10.0.3.1/24')
    net['r3'].cmd('ifconfig r3-eth2 10.0.3.2/24')
    net['r3'].cmd('ifconfig r3-eth1 10.0.4.1/24')

    # Add static routes
    net['r1'].cmd('ip route add 10.0.3.0/24 via 10.0.2.2')
    net['r1'].cmd('ip route add 10.0.4.0/24 via 10.0.2.2')
    net['r2'].cmd('ip route add 10.0.4.0/24 via 10.0.3.2')
    net['r2'].cmd('ip route add 10.0.1.0/24 via 10.0.2.1')
    net['r3'].cmd('ip route add 10.0.1.0/24 via 10.0.3.1')
    net['r3'].cmd('ip route add 10.0.2.0/24 via 10.0.3.1')

    # Verificar configurações de interface em h2
    info('*** Verificando configurações de interface em h2:\n')
    info(net['h2'].cmd('ifconfig'))

    info('*** Network configuration:\n')
    for host in net.hosts:
        info(f'{host.name} -> {host.cmd("ifconfig")}\n')

    info( '*** Routing Table on Router r1:\n' )
    info( net[ 'r1' ].cmd( 'route' ) )
    info( '*** Routing Table on Router r2:\n' )
    info( net[ 'r2' ].cmd( 'route' ) )
    info( '*** Routing Table on Router r3:\n' )
    info( net[ 'r3' ].cmd( 'route' ) )

    info('*** Testing network connectivity\n')
    net.pingAll()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
