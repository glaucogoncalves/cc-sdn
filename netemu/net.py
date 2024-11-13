#Simple practice of the course Advanced Topics in Computer Networks at UFRPE/Brazil 
#Author: Kleber Leal and Glauco Goncalves, PhD

import atexit
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import info,setLogLevel
from mininet.node import RemoteController
from mininet.link import TCLink

net = None

def createTopo():
        topo=Topo()

        #Create Nodes
        topo.addHost("h1")
        topo.addHost("h2")
        topo.addHost("h3")
        topo.addHost("h4")
        topo.addSwitch('s1', protocols="OpenFlow14")
        topo.addSwitch('s2', protocols="OpenFlow14")
        topo.addSwitch('s3', protocols="OpenFlow14")

        #Create links
        topo.addLink('s1','s2',bw=10,delay='10ms')
        topo.addLink('s1','s3',bw=10,delay='10ms')
        topo.addLink('s2','s3',bw=10,delay='30ms')
        topo.addLink('h1','s2')
        topo.addLink('h2','s2')
        topo.addLink('h3','s3')
        topo.addLink('h4','s3')
        return topo

def startNetwork():
        topo = createTopo()
        global net
        net = Mininet(topo=topo, autoSetMacs=True, controller=None, link=TCLink)
        net.addController( 'c0', controller=RemoteController, ip='172.17.0.1', port=6653)
        net.start()
        CLI(net)

def stopNetwork():
        if net is not None:
                net.stop()

if __name__ == '__main__':
        atexit.register(stopNetwork)
        setLogLevel('info')
        startNetwork()