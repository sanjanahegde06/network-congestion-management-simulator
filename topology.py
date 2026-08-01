from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel


def create_network():

    net = Mininet(
        controller=Controller,
        switch=OVSSwitch,
        link=TCLink
    )

    print("\n======================================")
    print(" Creating Network Topology")
    print("======================================")

    print("*** Adding Controller")

    net.addController(
        "c0",
        controller=Controller,
        command="ovs-testcontroller"
    )

    print("*** Adding Switches")

    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")
    s3 = net.addSwitch("s3")

    print("*** Adding Hosts")

    compute1 = net.addHost(
        "compute1",
        ip="10.0.0.1/24"
    )

    compute2 = net.addHost(
        "compute2",
        ip="10.0.0.2/24"
    )

    compute3 = net.addHost(
        "compute3",
        ip="10.0.0.3/24"
    )

    storage = net.addHost(
        "storage",
        ip="10.0.0.4/24"
    )

    print("*** Creating Links")

    net.addLink(
        s1,
        s2,
        cls=TCLink,
        bw=20
    )

    net.addLink(
        s1,
        s3,
        cls=TCLink,
        bw=20
    )

    net.addLink(s2, compute1)
    net.addLink(s2, compute2)

    net.addLink(s3, compute3)
    net.addLink(s3, storage)

    print("*** Starting Network")

    net.start()

    print("\n======================================")
    print(" Network Started Successfully")
    print("======================================")

    print("""
                Spine/Core
                    s1
                  /    \\
                 /      \\
               s2        s3
             /   \\      /   \\
      compute1 compute2 compute3 storage
""")

    return net


def stop_network(net):

    print("\n*** Stopping Network")

    net.stop()


if __name__ == "__main__":

    setLogLevel("info")

    network = create_network()

    CLI(network)

    stop_network(network)
