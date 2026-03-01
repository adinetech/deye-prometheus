#!/usr/bin/env python3
"""
main.py — Entry point for the Deye inverter Prometheus exporter.

Usage:
    python main.py             # Print all register values once (debug)
    python main.py --exporter  # Start Prometheus metrics server on :9105
"""
import sys

from exporter import DeyeExporter


def main():
    exporter = DeyeExporter()

    if "--exporter" in sys.argv:
        exporter.setup_metrics()
        exporter.run()
    else:
        exporter.print_once()


if __name__ == "__main__":
    main()
