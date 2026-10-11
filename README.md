# Network Congestion Management Simulator (NCMS)

## About
A Python-based network simulator that detects possible network congestion, attempts traffic mitigation, and records network performance results.

## Features
- Simulates a virtual network using Mininet and Open vSwitch.
- Generates concurrent traffic using iperf3.
- Measures network throughput and latency.
- Detects congestion using a configured utilization threshold.
- Applies traffic rate limiting using Linux `tc` and Token Bucket Filter (TBF).
- Records simulation logs and generates performance reports.

## Technologies Used
- Python
- Mininet
- Open vSwitch
- Linux
- iperf3
- Linux `tc` (TBF)
- Ping

## Network Topology
- **Switches:** s1, s2, s3
- **Hosts:** compute1, compute2, compute3, storage

The three compute hosts generate traffic toward the storage host through the virtual switches.

## How It Works
1. Creates the virtual network.
2. Tests connectivity between hosts.
3. Generates concurrent network traffic.
4. Measures throughput and latency.
5. Checks for possible congestion.
6. Attempts traffic rate limiting when congestion is detected.
7. Records results and generates a before-and-after performance report.

## Output
Displays network performance metrics and congestion status, while saving simulation logs and a report containing the results.

## Objective
To explore network performance monitoring, congestion detection, and traffic shaping in a simulated network environment.
