# Projeto de Simulação de Rede com KVM e Mininet

![KVM](https://img.shields.io/badge/KVM-Virtualization-2e3bff)
![Mininet](https://img.shields.io/badge/Mininet-Network%20Emulation-009999)

Este projeto envolve a criação de um cenário de rede virtual utilizando KVM e Mininet. O ambiente é composto por três VMs interligadas por redes isoladas, com o objetivo de testar e avaliar a comunicação e desempenho entre as VMs.

## Estrutura do Projeto

- **Cliente:** Máquina virtual que simula um cliente na rede.
- **Transporte:** Máquina virtual responsável por hospedar a rede Mininet que conecta as outras duas VMs.
- **Controle:** Máquina virtual que simula um servidor de controle na rede.

## Pré-requisitos

- **KVM:** Hypervisor para criar e gerenciar máquinas virtuais.
- **Mininet:** Emulador de rede para criar topologias de rede virtualizadas.
- **Libvirt:** Ferramenta para gerenciar plataformas de virtualização.
- **Virtual Network:** Configuração de redes virtuais para interconectar as VMs.

Topologia

![Mininet (3)](https://github.com/zeraimundo/Mininet/assets/82219488/c1f0f541-d4f6-46bb-a91a-bb5c035aef0a)

## Configuração do Ambiente

1. **Instalação do KVM e Libvirt:**
    ```sh
    sudo apt-get update
    sudo apt-get install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager
    sudo systemctl enable libvirtd
    sudo systemctl start libvirtd
    ```

2. **Instalação do Mininet:**
    ```sh
    sudo apt-get update
    sudo apt-get install git
    git clone https://github.com/mininet/mininet
    cd mininet/util/
    ./install.sh -a
    ```

3. **Configuração das VMs:**
    - Crie as VMs Cliente, Transporte e Controle utilizando o Virt-Manager ou via linha de comando.
    - Configure as interfaces de rede conforme necessário para garantir a conectividade entre as VMs.

## Script de Rede Mininet

O seguinte script Mininet é utilizado para configurar a rede entre as VMs:
```python
#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.link import Intf


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
    "A network topology with three routers and two hosts."

    def build(self, **_opts):
        # Add routers
        r1 = self.addNode('r1', cls=LinuxRouter, ip='10.0.1.1/24')
        r2 = self.addNode('r2', cls=LinuxRouter, ip='10.0.2.1/24')
        r3 = self.addNode('r3', cls=LinuxRouter, ip='10.0.3.1/24')

        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add hosts with IPs and default routes
        h1 = self.addHost('h1', ip='10.0.1.100/24', defaultRoute='via 10.0.1.1')
        h2 = self.addHost('h2', ip='10.0.4.100/24', defaultRoute='via 10.0.4.1')

        # Define link with bandwidth
        enlace = {'cls': TCLink, 'bw': 1000}

        # Add links between routers
        self.addLink(r1, r2, intfName1='r1-eth2', intfName2='r2-eth1', **enlace)
        self.addLink(r2, r3, intfName1='r2-eth2', intfName2='r3-eth2', **enlace)

        # Add links between routers and switches
        self.addLink(r1, s1, intfName2='r1-eth1', **enlace)
        self.addLink(r3, s2, intfName2='r3-eth1', **enlace)

        # Add links between hosts and switches
        self.addLink(h1, s1, **enlace)
        self.addLink(h2, s2, **enlace)

def run():
    "Test network topology"
    topo = NetworkTopo()
    net = Mininet(topo=topo, waitConnected=True)

    # Configure physical interfaces
    _intf1 = Intf('ens19', node=net['s1'])
    _intf2 = Intf('ens20', node=net['s2'])

    net.start()

    # Configure IP addresses on router interfaces
    net['r1'].cmd('ifconfig r1-eth1 10.0.1.1/24')
    net['r1'].cmd('ifconfig r1-eth2 10.0.2.1/24')
    net['r2'].cmd('ifconfig r2-eth1 10.0.2.2/24')
    net['r2'].cmd('ifconfig r2-eth2 10.0.3.1/24')
    net['r3'].cmd('ifconfig r3-eth2 10.0.3.2/24')
    net['r3'].cmd('ifconfig r3-eth1 10.0.4.1/24')

    # Add static routes on routers
    net['r1'].cmd('ip route add 10.0.3.0/24 via 10.0.2.2')
    net['r1'].cmd('ip route add 10.0.4.0/24 via 10.0.2.2')
    net['r2'].cmd('ip route add 10.0.4.0/24 via 10.0.3.2')
    net['r2'].cmd('ip route add 10.0.1.0/24 via 10.0.2.1')
    net['r3'].cmd('ip route add 10.0.1.0/24 via 10.0.3.1')
    net['r3'].cmd('ip route add 10.0.2.0/24 via 10.0.3.1')

    # Define buffer size in MB (example: 50MB)
    buffer_size_mb = 50  # Buffer size in MB

    # Buffer configuration on r1
    net['r1'].cmd('tc qdisc add dev r1-eth1 root handle 1: htb default 11')
    net['r1'].cmd(f'tc class add dev r1-eth1 parent 1: classid 1:1 htb rate 1000mbit burst 15k')
    net['r1'].cmd(f'tc qdisc add dev r1-eth1 parent 1:1 handle 10: bfifo limit {buffer_size_mb}mb')

    # Buffer configuration on r2
    net['r2'].cmd('tc qdisc add dev r2-eth1 root handle 1: htb default 11')
    net['r2'].cmd(f'tc class add dev r2-eth1 parent 1: classid 1:1 htb rate 1000mbit burst 15k')
    net['r2'].cmd(f'tc qdisc add dev r2-eth1 parent 1:1 handle 10: bfifo limit {buffer_size_mb}mb')

    # Buffer configuration on r3
    net['r3'].cmd('tc qdisc add dev r3-eth1 root handle 1: htb default 11')
    net['r3'].cmd(f'tc class add dev r3-eth1 parent 1: classid 1:1 htb rate 1000mbit burst 15k')
    net['r3'].cmd(f'tc qdisc add dev r3-eth1 parent 1:1 handle 10: bfifo limit {buffer_size_mb}mb')

    # Display routing tables for verification
    info('*** Routing Table on Router r1:\n')
    info(net['r1'].cmd('route'))
    info('*** Routing Table on Router r2:\n')
    info(net['r2'].cmd('route'))
    info('*** Routing Table on Router r3:\n')
    info(net['r3'].cmd('route'))

    # Test network connectivity
    info('*** Testing network connectivity\n')
    net.pingAll()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
```
<p align="center">
  <a href="https://youtu.be/jd5oj6ImwdE" target="_blank">
    <img src="https://img.youtube.com/vi/jd5oj6ImwdE/0.jpg" alt="Video on YouTube" width="600"><br>
    <b>Projeto de Simulação de Rede com KVM e Mininet</b>
  </a>
</p>

Observações:

1 - Precisa adicionar as rotas manualmente nos hosts Cliente e Servidor do KVM

2 - Precisa configurar a rede isolada para os hosts Cliente e Servidor do KVM
