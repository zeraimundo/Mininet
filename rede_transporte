#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.link import Intf

class NetworkTopo( Topo ):
    "A network topology with three switches and four hosts."

    def build( self, **_opts ):

        # Add switches
        s1, s2, s3 = [ self.addSwitch( s ) for s in ( 's1', 's2', 's3' ) ]

        # Add hosts
        h1 = self.addHost( 'h1', ip='10.0.1.101/24' )
        h2 = self.addHost( 'h2', ip='10.0.1.102/24' )
        h3 = self.addHost( 'h3', ip='10.0.1.103/24' )
        h4 = self.addHost( 'h4', ip='10.0.1.104/24' )

        enlace = {'cls': TCLink, 'bw':1000}

        # Add links between switches
        self.addLink( s1, s2, intfName1='s1-eth1', intfName2='s2-eth1', **enlace )
        self.addLink( s3, s2, intfName1='s3-eth1', intfName2='s2-eth2', **enlace )

        # Add links between hosts and switches
        self.addLink( h1, s1, intfName2='s1-eth2', **enlace )
        self.addLink( h2, s1, intfName2='s1-eth3', **enlace )
        self.addLink( h3, s3, intfName2='s3-eth2', **enlace )
        self.addLink( h4, s3, intfName2='s3-eth3', **enlace )

def run():
    "Test network topology"
    topo = NetworkTopo()
    net = Mininet( topo=topo, waitConnected=True )

    _intf = Intf( 'enp7s0' , node=net[ 's1'] )
    _intf = Intf( 'enp8s0' , node=net[ 's3'] )

    net.start()

    info( '*** Network configuration:\n' )
    for host in net.hosts:
        info( f'{host.name} -> {host.cmd("ifconfig")}\n' )

    info( '*** Testing network connectivity\n' )
    net.pingAll()

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()

