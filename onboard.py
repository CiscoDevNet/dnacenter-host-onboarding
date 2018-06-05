#! /usr/bin/env python
"""Command Line Interface Tool for Deploying Templates to DNA Center.


Copyright (c) 2018 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import os
from dnacsdk.api import Api
import urllib3
import click
import tabulate

__author__ = "Hank Preston <hapresto@cisco.com>"
__copyright__ = "Copyright (c) 2018 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

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
    """Command line tool for deploying templates to DNA Center.
    """
    pass

@click.command()
def device_list():
    """Retrieve and return network devices list.

        Returns the hostname, management IP, and family of each device.

        Example command:

            ./onboard.py device_list

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

        Returns the port name, status, description, and vlan information.

        Example command:

            ./onboard.py inteface_list switch1

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

        Returns the template name, parameters, content, and device types.

        Example command:

            ./onboard.py template_list
    """
    click.secho("Retrieving the templates available")

    from dnacsdk.templateProgrammer import Template
    templates = Template.get_all(dnacp)

    headers = ["Template Name", "Parameters", "Deploy Command", "Content", "Device Types"]
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
        cmd = "./onboard.py deploy \\\n --template {} \\\n --target {} ".format(
                template.name,
                "DEVICE"
            )
        params_cmd = " ".join(
            [
                '\\\n "{}=VALUE"'.format(param["parameterName"])
                for param in template.info["templateParams"]
            ]
        )
        cmd = cmd + params_cmd
        tr.append(cmd)
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
    """Deploy a template with DNA Center.

        Provide all template parameters and their values as arguements in the format of: "PARAMTER=VALUE"

        You can find the list of parameters using:
          ./onboard.py template_list

        Example command:

          ./onboard.py deploy --template VLANSetup --target switch1 \\\n"VLANID=3001" "VLANNAME=Data"
    """
    click.secho("Attempting deployment.")

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
