"""Sample usage
from dnacsdk.api import Api
from dnacsdk.templateProgrammer import Template

sample_template_name = "NetworkDeviceOnboarding"
sample_target_device = "10.32.250.6"

dnacp = Api(ip=DNAC_IP, username=DNAC_USERNAME, password=DNAC_PASSWORD)

templates = Template.get_all(dnacp)
template = Template(dnacp, name = sample_template_name)

deploy_params = {
        "INTERFACE": "GigabitEthernet1/1/3",
        "INTERFACE_DESCRIPTION": "TEST FROM API",
        "VLAN": "1022"
    }

deployment = template.deploy(dnacp, sample_target_device, deploy_params)
"""


class Template(object):

    @classmethod
    def get_all(cls, dnacp):
        templates = dnacp.get("/api/v1/template-programmer/template")
        return [Template(dnacp, templateId = template["templateId"]) for template in templates]

    @classmethod
    def __get_id__(cls, name, dnacp):
        templates = cls.get_all(dnacp)
        for template in templates:
            if name == template.name:
                return template.id


    def __init__(self, dnacp, templateId = None, name = None):
        if not templateId is None:
            pass
        elif not name is None:
            templateId = Template.__get_id__(name = name, dnacp = dnacp)

        template = dnacp.get("/api/v1/template-programmer/template/{}"
            .format(templateId))

        self.info = template
        self.id = self.info["id"]
        self.name = self.info["name"]

        self.versions = dnacp.get("/api/v1/template-programmer/template/version/{}"
            .format(templateId))[0]["versionsInfo"]
        self.latest_version = self.versions[1]
        self.input_params = [param["parameterName"] for param in self.info["templateParams"] ]

    def deploy(self, dnacp, target_device_ip, params):

        if not self.__deploy_param_check__(params):
            raise ValueError("Provided deploy parameters invalid.")

        body = {
          "targetInfo": [
            {
              "id": target_device_ip,
              "type": "MANAGED_DEVICE_IP",
              "params": params
            }
          ],
          "templateId": self.latest_version["id"]
        }

        deployment = dnacp.post("/api/v1/template-programmer/template/deploy",
                body
            )

        return deployment["deploymentId"]

    @classmethod
    def deployment_status(cls, dnacp, deploymentId):
        api = "/api/v1/template-programmer/template/deploy/status/{}".format(
            deploymentId
        )
        return dnacp.get(api)

    def __deploy_param_check__(self, params):
        return sorted(self.input_params) == sorted(list(params.keys()))
