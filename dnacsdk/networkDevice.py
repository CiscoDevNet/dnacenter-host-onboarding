"""Sample usage
from dnacsdk.api import Api
from dnacsdk.networkDevice import NetworkDevice

dnacp = Api(ip=DNAC_IP, username=DNAC_USERNAME, password=DNAC_PASSWORD)

devices = NetworkDevice.get_all(dnacp)


"""

from .exceptions import ResourceNotFound

class NetworkDevice(object):
    @classmethod
    def get_all(cls, dnacp):
        devices = dnacp.get("/api/v1/network-device")["response"]
        devices = [NetworkDevice(dnacp, deviceId = device["id"]) for device in devices]
        return devices

    def __init__(self, dnacp,
        deviceId = None,
        managementIpAddress = None,
        hostname = None,
        serialNumber = None):

        if not deviceId is None:
            api = "/api/v1/network-device/{}".format(deviceId)
            # device = dnacp.get(api)["response"]
        elif not serialNumber is None:
            api = "/api/v1/network-device/serial-number/{}".format(serialNumber)
            # device = dnacp.get(api)["response"]
        elif not managementIpAddress is None:
            api = "/api/v1/network-device/ip-address/{}".format(managementIpAddress)
        elif not hostname is None:
            all_devices = NetworkDevice.get_all(dnacp)
            for device in all_devices:
                if hostname == device.hostname:
                    api = "/api/v1/network-device/{}".format(device.id)
                    break

        device = dnacp.get(api)["response"]

        self.id = device["id"]
        self.hostname = device["hostname"]
        self.managementIpAddress = device["managementIpAddress"]
        self.serialNumber = device["serialNumber"]
        self.macAddress = device["macAddress"]
        self.location = device["location"]
        self.family = device["family"]
        self.type = device["type"]

        self.info = device

        self.dnacp = dnacp

        # self.interfaces = {}
        #
        # try:
        #     interfaces_api = "/api/v1/interface/network-device/{}".format(self.id)
        #     interfaces = dnacp.get(interfaces_api)["response"]
        #     for interface in interfaces:
        #         self.interfaces[interface["portName"]] = interface
        # except ResourceNotFound:
        #     pass
        # except:
        #     pass

    @property
    def interfaces(self):
        interfaces_property = {}

        try:
            interfaces_api = "/api/v1/interface/network-device/{}".format(self.id)
            interfaces = self.dnacp.get(interfaces_api)["response"]
            for interface in interfaces:
                interfaces_property[interface["portName"]] = interface
        except ResourceNotFound:
            print("No Interfaces")
            pass
        except:
            pass

        return interfaces_property
