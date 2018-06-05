# dnacenter-host-onboarding
Sample code and application to simplifying on-boarding new hosts to the network with DNA Center 

# Making Onboarding Easy 
The goal of this application is to make it easy to leverage the deployment templates from DNA Center in a scriptable and automated fashion.  The main application is a CLI tool that users can use to deploy any template available in DNA Center to any device.  

**Example Usage:** 

```bash
./onboard.py deploy --template NetworkDeviceOnboarding \
  --target cat_9k_1.abc.inc \
  "INTERFACE=GigabitEthernet1/1/1" \
  "VLAN=3001" \
  "INTERFACE_DESCRIPTION=My new interface" 
```

# Requirements 
To leverage this applicaiton you will need: 

* Python 3.6+
* DNA Center 1.2+ with the DNA Center Platform API package installed.  
* A DNA Center account with permissions to deploy templates. 


# Install and Setup 

Clone down the code.  

    https://github.com/CiscoDevNet/dnacenter-host-onboarding
    cd dnacenter-host-onboarding 

Setup Python Virtual Environment (requires Python 3.6+)

    python3.6 -m venv venv 
    source venv/bin/activate
    pip install -r requirements.txt 

> Pipfiles are also included if you prefer to use `pipenv`

Setup local environment variables for your DNA Center.  *Provide the info for your DNA Center*

    # Examples 
    export DNAC_IP=192.168.139.73
    export DNAC_USERNAME=admin
    export DNAC_PASSWORD=Cisco123

> The file `src_dnac.example` is provided in the repo.  You can create a local `src_dnac` file with your information and then `source src_dnac` to simplify the env setup.  

# Using the Application 
Once installed and setup, you can now get started.  

Investigate the built in help with the tool. 

    ./onboard.py --help
    
    # OUTPUT
    Usage: onboard.py [OPTIONS] COMMAND [ARGS]...
    
      Command line tool for deploying templates to DNA Center.
    
    Options:
      --help  Show this message and exit.
    
    Commands:
      deploy          Deploy a template with DNA Center.
      device_list     Retrieve and return network devices list.
      interface_list  Retrieve the list of interfaces on a device.
      template_list   Retrieve the deployment templates that are...
      
Look at the available templates.  Each template will provide the required parameters, what will be configured, and give an example deploy command.  

    ./onboard.py template_list
    
    # OUTPUT
    Retrieving the templates available
    ╒═════════════════════════╤═══════════════════════╤═══════════════════════════════════════╤══════════════════════════════════════╤═══════════════════╕
    │ Template Name           │ Parameters            │ Deploy Command                        │ Content                              │ Device Types      │
    ╞═════════════════════════╪═══════════════════════╪═══════════════════════════════════════╪══════════════════════════════════════╪═══════════════════╡
    │ ChangeTZ                │                       │ ./onboard.py deploy \                 │ clock timezone +10                   │ Switches and Hubs │
    │                         │                       │  --template ChangeTZ \                │                                      │ Routers           │
    │                         │                       │  --target DEVICE                      │                                      │                   │
    ├─────────────────────────┼───────────────────────┼───────────────────────────────────────┼──────────────────────────────────────┼───────────────────┤
    │ NetworkDeviceOnboarding │ VLAN                  │ ./onboard.py deploy \                 │ interface $INTERFACE                 │ Switches and Hubs │
    │                         │ INTERFACE_DESCRIPTION │  --template NetworkDeviceOnboarding \ │   description $INTERFACE_DESCRIPTION │                   │
    │                         │ INTERFACE             │  --target DEVICE \                    │   switchport mode access             │                   │
    │                         │                       │  "VLAN=VALUE" \                       │   switchport access vlan $VLAN       │                   │
    │                         │                       │  "INTERFACE_DESCRIPTION=VALUE" \      │   no shut                            │                   │
    │                         │                       │  "INTERFACE=VALUE"                    │                                      │                   │
    ├─────────────────────────┼───────────────────────┼───────────────────────────────────────┼──────────────────────────────────────┼───────────────────┤
    │ ChangeDescription       │ interface             │ ./onboard.py deploy \                 │ interface $interface                 │ Switches and Hubs │
    │                         │ description           │  --template ChangeDescription \       │   ! added by DNAC                    │                   │
    │                         │                       │  --target DEVICE \                    │   description $description           │                   │
    │                         │                       │  "interface=VALUE" \                  │                                      │                   │
    │                         │                       │  "description=VALUE"                  │                                      │                   │
    ╘═════════════════════════╧═══════════════════════╧═══════════════════════════════════════╧══════════════════════════════════════╧═══════════════════╛    

    
If needed, retrieve the list of devices (with `./onboard.py device_list`) or interfaces (with `./onboard.py interface_list DEVICE_NAME`).  

    $ ./onboard.py device_list
    
    # OUTPUT
    Retrieving the devices.
    ╒═══════════════════╤═════════════════╤═══════════════════╕
    │ Hostname          │ Management IP   │ Family            │
    ╞═══════════════════╪═════════════════╪═══════════════════╡
    │ asr1001-x.abc.inc │ 10.10.22.74     │ Routers           │
    ├───────────────────┼─────────────────┼───────────────────┤
    │ cat_9k_1.abc.inc  │ 10.10.22.66     │ Switches and Hubs │
    ├───────────────────┼─────────────────┼───────────────────┤
    │ cat_9k_2.abc.inc  │ 10.10.22.70     │ Switches and Hubs │
    ├───────────────────┼─────────────────┼───────────────────┤
    │ cs3850.abc.inc    │ 10.10.22.69     │ Switches and Hubs │
    ╘═══════════════════╧═════════════════╧═══════════════════╛
    
Deploy a template with the tool.  (Remember the template list includes a sample for how to format the command). 

    ./onboard.py deploy --template NetworkDeviceOnboarding \
      --target cat_9k_1.abc.inc \
      "INTERFACE=GigabitEthernet1/1/1" \
      "VLAN=3001" \
      "INTERFACE_DESCRIPTION=My new interface" 
      
    # OUTPUT
    Attempting deployment.
    Deployment Status: IN_PROGRESS