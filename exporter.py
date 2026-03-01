"""
exporter.py — Prometheus metrics setup, collection loop and debug print mode.
"""
import re
import time

from prometheus_client import Gauge, start_http_server

from config import EXPORTER_PORT, POLL_INTERVAL
from decoders import decode
from inverter import InverterClient
from parameters import PARAMETERS


def _sanitize(name: str) -> str:
    """Convert a human-readable parameter name to a valid Prometheus metric name."""
    name = name.lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)
    # Collapse multiple underscores
    name = re.sub(r"_+", "_", name).strip("_")
    return "deye_" + name


class DeyeExporter:
    """Sets up and runs the Prometheus metrics exporter."""

    def __init__(self):
        self.client = InverterClient()
        self.gauges: dict[str, Gauge] = {}

    def setup_metrics(self) -> None:
        """Register all numeric parameters as Prometheus Gauge metrics."""
        for p in PARAMETERS:
            # String/lookup parameters return None from decode — skip them
            if p.get("isstr", False) or p.get("rule", 1) == 5:
                continue
            metric_name = _sanitize(p["name"])
            uom = p.get("uom", "")
            description = p.get("help", p["name"])
            if uom:
                description += f" [{uom}]"
            self.gauges[p["name"]] = Gauge(metric_name, description)

    def collect(self) -> None:
        """Poll the inverter and update all gauges."""
        regs = self.client.read_all()
        for p in PARAMETERS:
            gauge = self.gauges.get(p["name"])
            if gauge is None:
                continue
            value = decode(p, regs)
            if value is not None:
                gauge.set(value)

    def run(self) -> None:
        """Start the HTTP server and enter the polling loop."""
        start_http_server(EXPORTER_PORT)
        print(f"[deye-exporter] Prometheus metrics running on :{EXPORTER_PORT}/metrics")
        print(f"[deye-exporter] Exposing {len(self.gauges)} gauges — polling every {POLL_INTERVAL}s\n")

        while True:
            try:
                self.collect()
            except Exception as exc:
                print(f"[deye-exporter] Poll error: {exc}")
            time.sleep(POLL_INTERVAL)

    def print_once(self) -> None:
        """Debug mode: read registers once and print all values to stdout."""
        regs = self.client.read_all()
        print("\n─── DEYE INVERTER SNAPSHOT ─────────────────────────────────────")
        current_group = None
        for p in PARAMETERS:
            if p.get("group") != current_group:
                current_group = p.get("group", "")
                print(f"\n  [{current_group.upper()}]")
            value = decode(p, regs)
            uom  = p.get("uom", "")
            if value is None:
                print(f"    {p['name']:35} (string/unsupported)")
            else:
                print(f"    {p['name']:35} {value:>12.3f}  {uom}")
        print("\n────────────────────────────────────────────────────────────────\n")
