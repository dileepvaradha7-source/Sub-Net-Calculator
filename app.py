"""A small, stateless IPv4 subnet calculator for the deployment assessment."""

import ipaddress
import os

from flask import Flask, jsonify, render_template, request


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/api/version")
def version():
    return jsonify(version=os.environ.get("APP_VERSION", "local"))


@app.post("/api/subnets")
def calculate_subnet():
    body = request.get_json(silent=True)
    cidr = body.get("cidr") if isinstance(body, dict) else None
    if not isinstance(cidr, str) or not cidr.strip() or len(cidr) > 64 or "/" not in cidr:
        return jsonify(error="Provide an IPv4 CIDR string, for example 192.168.10.0/24."), 400

    try:
        network = ipaddress.IPv4Network(cidr.strip(), strict=False)
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError):
        return jsonify(error="Invalid IPv4 CIDR address."), 400

    # Python's hosts() includes both addresses for /31 and the single /32 address.
    usable_count = network.num_addresses if network.prefixlen >= 31 else network.num_addresses - 2
    first_usable = network.network_address if network.prefixlen >= 31 else network.network_address + 1
    last_usable = network.broadcast_address if network.prefixlen >= 31 else network.broadcast_address - 1

    return jsonify(
        input=cidr.strip(),
        network=str(network),
        netmask=str(network.netmask),
        network_address=str(network.network_address),
        broadcast_address=str(network.broadcast_address),
        first_usable=str(first_usable),
        last_usable=str(last_usable),
        usable_hosts=usable_count,
        prefix_length=network.prefixlen,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
