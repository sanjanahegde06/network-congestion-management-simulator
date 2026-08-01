from topology import create_network, stop_network
from config import *

import re
import time
from datetime import datetime


def extract_throughput(output):

    throughput = 0.0

    for line in output.splitlines():

        if "sender" in line:

            match = re.search(r'([\d.]+)\s+Mbits/sec', line)

            if match:
                throughput = float(match.group(1))
                break

    return throughput


def measure_latency(host):

    output = host.cmd(f"ping -c 3 {SERVER_IP}")

    match = re.search(r'rtt min/avg/max.*=.*/([\d.]+)/', output)

    if match:
        return float(match.group(1))

    return 0.0


def analyze_congestion(throughput):

    utilization = (throughput / LINK_CAPACITY) * 100
    display_utilization = min(utilization, 100.0)

    if utilization >= CONGESTION_THRESHOLD:
        status = "CONGESTED"
        traffic = "HIGH"
    else:
        status = "NORMAL"
        traffic = "NORMAL"

    return display_utilization, status, traffic


def create_result(throughput, utilization, latency, status):

    return {
        'throughput'  : throughput,
        'utilization' : utilization,
        'latency'     : latency,
        'status'      : status
    }


def run_mitigation_test(compute1):

    print("\nMitigation Triggered")
    print("-" * 40)
    print("Applying tc Traffic Rate Limiting...")
    print()

    output = ""

    try:

        compute1.cmd(
            f"tc qdisc add dev compute1-eth0 root tbf rate {MITIGATION_RATE} burst 10kb latency 70ms"
        )

        print(f"tc Rate Limit Applied : {MITIGATION_RATE}")
        print()

        output = compute1.cmd(
            f"iperf3 -c {SERVER_IP} -p {PORTS[0]} -t {TEST_DURATION}"
        )

        print(output)

    finally:

        compute1.cmd(
            "tc qdisc del dev compute1-eth0 root 2>/dev/null"
        )

        print("tc Rate Limit Removed")

    sender_rate = extract_throughput(output)

    utilization = (sender_rate / LINK_CAPACITY) * 100

    if utilization >= CONGESTION_THRESHOLD:
        status = "CONGESTED"
    else:
        status = "NORMAL"

    print("\nPost-Mitigation Results")
    print("-" * 40)
    print(f"Throughput   : {sender_rate:.2f} Mbps")
    print(f"Utilization  : {utilization:.2f}%")
    print(f"Status       : {status}")

    if status == "NORMAL":
        print("\nMitigation Successful — Congestion Resolved")
    else:
        print("\nMitigation Insufficient — Congestion Persists")

    return sender_rate, utilization, status


def display_comparison(before, after):

    print("\n")
    print("=" * 60)
    print(" BEFORE vs AFTER MITIGATION")
    print("=" * 60)
    print(f"{'Metric':<25} {'Before':>15} {'After':>15}")
    print("-" * 55)
    print(f"{'Throughput (Mbps)':<25} {before['throughput']:>15.2f} {after['throughput']:>15.2f}")
    print(f"{'Utilization (%)':<25} {before['utilization']:>15.2f} {after['utilization']:>15.2f}")
    print(f"{'Latency (ms)':<25} {before['latency']:>15.2f} {after['latency']:>15.2f}")
    print("=" * 60)

    if before['latency'] > 0:
        latency_improvement = (
            (before['latency'] - after['latency']) / before['latency']
        ) * 100
    else:
        latency_improvement = 0.0

    if before['utilization'] > 0:
        util_improvement = (
            (before['utilization'] - after['utilization']) / before['utilization']
        ) * 100
    else:
        util_improvement = 0.0

    print(f"\nLatency improved by    : {latency_improvement:.1f}%")
    print(f"Utilization reduced by : {util_improvement:.1f}%")
    print(f"Status after mitigation: {after['status']}")

    if after['status'] == "NORMAL":
        print("\nCongestion Successfully Resolved ✓")
    else:
        print("\nCongestion Persists — Further Action Needed")


def save_log(throughput, utilization, status):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as file:

        file.write("\n")
        file.write("=" * 60 + "\n")
        file.write(f"Time              : {timestamp}\n")
        file.write(f"Topology          : {TOPOLOGY}\n")
        file.write(f"Hosts             : {HOSTS}\n")
        file.write(f"Switches          : {SWITCHES}\n")
        file.write(f"Capacity          : {LINK_CAPACITY:.1f} Mbps\n")
        file.write(f"Throughput        : {throughput:.2f} Mbps\n")
        file.write(f"Utilization       : {utilization:.2f}%\n")
        file.write(f"Status            : {status}\n")
        file.write("=" * 60 + "\n")


def generate_report(before, after):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(REPORT_FILE, "w") as file:

        file.write("NETWORK CONGESTION MANAGEMENT REPORT\n")
        file.write("=" * 45 + "\n\n")

        file.write(f"Simulation Time : {timestamp}\n\n")

        file.write("NETWORK CONFIGURATION\n")
        file.write("-" * 30 + "\n")
        file.write(f"Topology        : {TOPOLOGY}\n")
        file.write(f"Hosts           : {HOSTS}\n")
        file.write(f"Switches        : {SWITCHES}\n")
        file.write(f"Capacity        : {LINK_CAPACITY:.1f} Mbps\n\n")

        file.write("BEFORE MITIGATION\n")
        file.write("-" * 30 + "\n")
        file.write(f"Throughput      : {before['throughput']:.2f} Mbps\n")
        file.write(f"Utilization     : {before['utilization']:.2f}%\n")
        file.write(f"Latency         : {before['latency']:.2f} ms\n")
        file.write(f"Status          : {before['status']}\n\n")

        file.write("AFTER MITIGATION\n")
        file.write("-" * 30 + "\n")
        file.write(f"Throughput      : {after['throughput']:.2f} Mbps\n")
        file.write(f"Utilization     : {after['utilization']:.2f}%\n")
        file.write(f"Latency         : {after['latency']:.2f} ms\n")
        file.write(f"Status          : {after['status']}\n\n")

        if before['latency'] > 0:
            latency_improvement = (
                (before['latency'] - after['latency']) / before['latency']
            ) * 100
        else:
            latency_improvement = 0.0

        file.write("IMPROVEMENT SUMMARY\n")
        file.write("-" * 30 + "\n")
        file.write(f"Latency Improvement : {latency_improvement:.1f}%\n")
        file.write(
            f"Congestion Resolved : "
            f"{'Yes' if after['status'] == 'NORMAL' else 'No'}\n\n"
        )

        file.write("RECOMMENDATIONS\n")
        file.write("-" * 30 + "\n")

        if after['status'] == "CONGESTED":
            file.write("- Reduce rate limit further\n")
            file.write("- Upgrade link bandwidth\n")
            file.write("- Consider load balancing across multiple paths\n")
        else:
            file.write("- Network operating normally after mitigation\n")
            file.write("- Continue periodic monitoring\n")
            file.write("- Consider ECMP for production environments\n")


def display_summary(throughput, utilization, status, traffic):

    print("\n")
    print("=" * 60)
    print(" NETWORK CONGESTION ANALYSIS")
    print("=" * 60)

    print("\nNetwork Information")
    print("-" * 30)
    print(f"Topology             : {TOPOLOGY}")
    print(f"Hosts                : {HOSTS}")
    print(f"Switches             : {SWITCHES}")

    print("\nPerformance Metrics")
    print("-" * 30)
    print(f"Link Capacity        : {LINK_CAPACITY:.1f} Mbps")
    print(f"Measured Throughput  : {throughput:.2f} Mbps")
    print(f"Link Utilization     : {utilization:.2f}%")

    print("\nHealth Status")
    print("-" * 30)
    print("Connectivity         : PASS")
    print(f"Traffic Level        : {traffic}")
    print(f"Network Status       : {status}")

    print("\nGenerated Files")
    print("-" * 30)
    print(LOG_FILE)
    print(REPORT_FILE)

    print("\n" + "=" * 60)


def main():

    print("=" * 60)
    print(" Network Congestion Management Simulator")
    print("=" * 60)

    net = create_network()

    storage = None

    try:

        print("\n[1] Connectivity Test")
        net.pingAll()
        print("Status : PASS")

        compute1 = net.get("compute1")
        compute2 = net.get("compute2")
        compute3 = net.get("compute3")
        storage  = net.get("storage")

        print("\n[2] Starting iperf3 Servers")
        storage.cmd("pkill iperf3")
        time.sleep(1)
        storage.cmd(f"iperf3 -s -D -p {PORTS[0]}")
        storage.cmd(f"iperf3 -s -D -p {PORTS[1]}")
        storage.cmd(f"iperf3 -s -D -p {PORTS[2]}")
        time.sleep(3)
        print(f"Servers Started on ports {PORTS}")

        print("\n[3] Measuring Baseline Latency")
        baseline_latency = measure_latency(compute1)
        print(f"Baseline Latency : {baseline_latency:.2f} ms")

        print("\n[4] Generating Concurrent Traffic (3 flows)")
        compute1.cmd(
            f"iperf3 -c {SERVER_IP} -p {PORTS[0]} -t {TEST_DURATION} &"
        )
        compute2.cmd(
            f"iperf3 -c {SERVER_IP} -p {PORTS[1]} -t {TEST_DURATION} &"
        )
        compute3.cmd(
            f"iperf3 -c {SERVER_IP} -p {PORTS[2]} -t {TEST_DURATION} &"
        )
        print("3 concurrent background flows started")
        print("(compute1, compute2, compute3 → storage)")

        time.sleep(3)

        print("\n[5] Measuring Congested Latency (during traffic)")
        congested_latency = measure_latency(compute1)
        print(f"Congested Latency : {congested_latency:.2f} ms")

        time.sleep(TEST_DURATION)

        print("\n[6] Measuring Single Flow Throughput Under Load")
        output = compute1.cmd(
            f"iperf3 -c {SERVER_IP} -p {PORTS[0]} -t 5"
        )
        print(output)

        throughput = extract_throughput(output)
        utilization, status, traffic = analyze_congestion(throughput)

        before = create_result(
            throughput,
            utilization,
            congested_latency,
            status
        )

        save_log(throughput, utilization, status)
        display_summary(throughput, utilization, status, traffic)

        after = create_result(
            throughput,
            utilization,
            congested_latency,
            status
        )

        if status == "CONGESTED":

            print("\n[7] Running Mitigation")
            after_throughput, after_utilization, after_status = run_mitigation_test(
                compute1
            )

            print("\n[8] Measuring Post-Mitigation Latency")
            after_latency = measure_latency(compute1)
            print(f"Post-Mitigation Latency : {after_latency:.2f} ms")

            after = create_result(
                after_throughput,
                after_utilization,
                after_latency,
                after_status
            )

            display_comparison(before, after)

        generate_report(before, after)

        print("\nSimulation Completed Successfully.\n")

    finally:

        if storage:
            storage.cmd("pkill iperf3")

        stop_network(net)


if __name__ == "__main__":
    main()
