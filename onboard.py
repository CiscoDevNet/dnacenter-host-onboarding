#! /usr/bin/env python
"""


Copyright (c) 2018 Cisco and/or its affiliates.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
from dnacsdk.api import Api
import urllib3
import click
import tabulate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DNAC_IP = os.environ.get("DNAC_IP")
DNAC_USERNAME = os.environ.get("DNAC_USERNAME")
DNAC_PASSWORD = os.environ.get("DNAC_PASSWORD")

if DNAC_IP is None or DNAC_USERNAME is None or DNAC_PASSWORD is None:
    print("DNA Center details must be set via environment variables before running.")
    print("   export DNAC_IP=192.168.100.1")
    print("   export DNAC_USERNAME=admin")
    print("   export DNAC_PASSWORD=password")
    print("")
    exit("1")

dnacp = Api(ip=DNAC_IP, username=DNAC_USERNAME, password=DNAC_PASSWORD)

@click.group()
def cli():
    pass

@click.command()
def device_list():
    """Retrieve and return network devices list.
    """
    click.secho("Retrieving the devices.")

    from dnacsdk.networkDevice import NetworkDevice
    devices = NetworkDevice.get_all(dnacp)

    headers = ["Hostname", "Management IP", "Family"]
    table = list()

    for device in devices:
        tr = [device.hostname, device.managementIpAddress, device.family]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

@click.command()
@click.argument("device")
def interface_list(device):
    """Retrieve the list of interfaces on a device.

    Requires the hostname of the device to retrieve interfaces from.
    """
    click.secho("Retrieving the interfaces for {}.".format(device))

    from dnacsdk.networkDevice import NetworkDevice
    device = NetworkDevice(dnacp, hostname = device)

    headers = ["Port Name", "Status", "Description", "VLAN", "Voice VLAN"]
    table = list()

    for interface in device.interfaces.values():
        tr = [
                interface["portName"],
                "{}/{}".format(interface["adminStatus"], interface["status"]),
                interface["description"],
                interface["vlanId"],
                interface["voiceVlan"]
            ]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

@click.command()
def template_list():
    """Retrieve the deployment templates that are available.
    """
    click.secho("Retrieving the templates avaailable")

    from dnacsdk.templateProgrammer import Template
    templates = Template.get_all(dnacp)

    headers = ["Template Name", "Parameters", "Content", "Device Types"]
    table = list()

    for template in templates:
        tr = []
        tr.append(template.name)
        tr.append("\n".join(
                ["{}".format(param["parameterName"])
                    for param in template.info["templateParams"]
                ]
            )
        )
        tr.append(template.info["templateContent"])
        tr.append("\n".join(
            [type["productFamily"] for type in template.info["deviceTypes"]]
            )
        )
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))


@click.command()
@click.option("--template", help="Name of the template to deploy")
@click.option("--target", help="Hostname of target network device.")
@click.argument("parameters", nargs=-1)
def deploy(template, target, parameters):
    """Function to onboard a new network attached host

    """
    from dnacsdk.networkDevice import NetworkDevice
    from dnacsdk.templateProgrammer import Template

    device = NetworkDevice(dnacp, hostname = target)
    template = Template(dnacp, name = template)

    deploy_params = dict([param.split("=", maxsplit=1) for param in parameters])

    # Deploy Template
    deployment = template.deploy(
                                    dnacp,
                                    target_device_ip = device.managementIpAddress,
                                    params = deploy_params
                                )

    print("Deployment Status: {}".format(
        Template.deployment_status(dnacp, deployment)["devices"][0]["status"])
    )

cli.add_command(deploy)
cli.add_command(device_list)
cli.add_command(interface_list)
cli.add_command(template_list)

if __name__ == '__main__':
    cli()
