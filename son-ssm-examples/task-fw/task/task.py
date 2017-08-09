"""
Copyright (c) 2015 SONATA-NFV
ALL RIGHTS RESERVED.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Neither the name of the SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.

This work has been performed in the framework of the SONATA project,
funded by the European Commission under Grant number 671517 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the SONATA
partner consortium (www.sonata-nfv.eu).
"""

import logging
import yaml
from sonsmbase.smbase import sonSMbase

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("ssm-task-1")
LOG.setLevel(logging.DEBUG)
logging.getLogger("son-mano-base:messaging").setLevel(logging.INFO)


class TaskSSM(sonSMbase):

    def __init__(self):

        """
        :param specific_manager_type: specifies the type of specific manager that could be either fsm or ssm.
        :param service_name: the name of the service that this specific manager belongs to.
        :param function_name: the name of the function that this specific manager belongs to, will be null in SSM case
        :param specific_manager_name: the actual name of specific manager (e.g., scaling, placement)
        :param id_number: the specific manager id number which is used to distinguish between multiple SSM/FSM
        that are created for the same objective (e.g., scaling with algorithm 1 and 2)
        :param version: version
        :param description: description
        """
        self.specific_manager_type = 'ssm'
        self.service_name = 'service1'
        self.specific_manager_name = 'task'
        self.id_number = '1'
        self.version = 'v0.1'
        self.counter = 0
        self.nsd = None
        self.vnfs = None
        self.description = "An empty SSM"

        super(self.__class__, self).__init__(specific_manager_type= self.specific_manager_type,
                                             service_name= self.service_name,
                                             specific_manager_name = self.specific_manager_name,
                                             id_number = self.id_number,
                                             version = self.version,
                                             description = self.description)

    def on_registration_ok(self):
        LOG.info("Received registration ok event.")
        self.manoconn.publish(topic='specific.manager.registry.ssm.status', message=yaml.dump(
                                  {'name':self.specific_manager_id,'status': 'UP and Running'}))

        # Subscribe to the topic that the SLM will be sending on
        topic = 'generic.ssm.' + self.sfuuid
        self.manoconn.subscribe(self.received_request, topic)

    def received_request(self, ch, method, prop, payload):
        """
        This method is called when the SLM is reaching out
        """
        content = yaml.load(payload)

        # Don't react to self-sent messages
        if prop.app_id == self.specific_manager_id:
            LOG.info("Received self-sent message, ignoring...")
            return

        # Don't react to messages that are not a request
        if 'ssm_type' not in content.keys():
            LOG.info("Received message that is not a request, ignoring...")
            return

        # Only react on messages intended for the task SSM
        if str(content['ssm_type']) == 'task':
            LOG.info("Received a task request")
            self.task_request(prop.correlation_id, content)
            return

        if str(content['ssm_type']) == 'configure':
            LOG.info("Received a configure request")
            self.configure_request(prop.correlation_id, content)
            return

        if str(content['ssm_type']) == 'monitor':
            LOG.info("Received a monitor request")
            self.monitor_request(prop.correlation_id, content)
            return

        # If the request type field doesn't match any of the above
        LOG.info("type " + str(content['ssm_type']) + " not covered by SSM")

    def task_request(self, corr_id, content):
        """
        This method handles a task request.
        """

        # Update the received schedule
        schedule = content['schedule']
        schedule.remove('vnfs_start')
#        schedule.remove('vnf_chain')
#        schedule.remove('wan_configure')

        schedule.insert
        schedule.insert(7, 'vnfs_start')
        schedule.insert(7, 'vnfs_config')
        schedule.insert(7, 'configure_ssm')

        response = {'schedule': schedule, 'status': 'COMPLETED'}

        LOG.info("task request responded to: " + str(response))

        # Sending a response
        topic = 'generic.ssm.' + self.sfuuid
        self.manoconn.notify(topic,
                             yaml.dump(response),
                             correlation_id=corr_id)

    def configure_request(self, corr_id, content):
        """
        This method handles a configuration request.
        """

        if content["workflow"] == 'instantiation':
            msg = "Received a configure request for the instantiation workflow"
            LOG.info(msg)
            self.configure_instantiation(corr_id, content)

    def configure_instantiation(self, corr_id, content):
        """
        This method creates the configure response for the instantiation
        workflow.
        """
        response = {}
        response['vnf'] = []

        for vnf in content['functions']:
            vnfd = vnf["vnfd"]
            if vnfd['name'] == 'vtc-vnf':
                new_entry = {}
                new_entry['id'] = vnf['id']
                new_entry['start'] = {'trigger': True,
                                      'payload': {'foo': 'bar',
                                                  'vnfr': 'bar'}}
                response['vnf'].append(new_entry)
            if vnfd['name'] == 'fw-vnf':
                new_entry = {}
                new_entry['id'] = vnf['id']
                new_entry['start'] = {'trigger': False,
                                      'payload': {}}
                response['vnf'].append(new_entry)

        LOG.info("Generated response: " + str(response))
        # Sending a response
        topic = 'generic.ssm.' + self.sfuuid
        self.manoconn.notify(topic,
                             yaml.dump(response),
                             correlation_id=corr_id)

    def monitor_request(self, corr_id, content):
        """
        This method handels the reception of monitor data
        """
        if 'nsd' in content.keys():
            LOG.info("Received descriptors")
            self.nsd = content['nsd']
            self.vnfs = content['vnfs']

        else:
            if self.counter == 0:
                message = {}
                message['foo'] = 'bar'
                message['service_instance_id'] = self.sfuuid
                message['workflow'] = 'termination'

                # message['schedule'] = ['vnfs_scale']
                # message['vnf'] = []

                # for vnf in self.vnfs:
                #     if vnf['vnfd']['name'] == 'vtc-vnf':
                #         new_entry = {}
                #         new_entry['id'] = vnf['id']
                #         new_entry['scale'] = {'trigger': True,
                #                               'payload': {'foo': 'bar',
                #                                           'vnfr': 'bar'}}
                #         message['vnf'].append(new_entry)
                topic = 'monitor.ssm.' + self.sfuuid
                self.manoconn.notify(topic, yaml.dump(message))
                self.counter = 1
                LOG.info("Responded to monitoring request")


def main():
    TaskSSM()

if __name__ == '__main__':
    main()
