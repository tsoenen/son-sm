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
LOG = logging.getLogger("fsm-start-stop-configure")
LOG.setLevel(logging.DEBUG)
logging.getLogger("son-mano-base:messaging").setLevel(logging.INFO)


class CssFSM(sonSMbase):

    def __init__(self):

        """
        :param specific_manager_type: specifies the type of specific manager
        that could be either fsm or ssm.
        :param service_name: the name of the service that this specific manager
        belongs to.
        :param function_name: the name of the function that this specific
        manager belongs to, will be null in SSM case
        :param specific_manager_name: the actual name of specific manager
        (e.g., scaling, placement)
        :param id_number: the specific manager id number which is used to
        distinguish between multiple SSM/FSM that are created for the same
        objective (e.g., scaling with algorithm 1 and 2)
        :param version: version
        :param description: description
        """

        self.specific_manager_type = 'fsm'
        self.service_name = 'service1'
        self.function_name = 'function1'
        self.specific_manager_name = 'css'
        self.id_number = '1'
        self.version = 'v0.1'
        self.description = "An FSM that subscribes to start, stop and configuration topic"

        super(self.__class__, self).__init__(specific_manager_type=self.specific_manager_type,
                                             service_name=self.service_name,
                                             function_name=self.function_name,
                                             specific_manager_nam=self.specific_manager_name,
                                             id_number=self.id_number,
                                             version=self.version,
                                             description=self.description)

    def on_registration_ok(self):

        # The fsm registration was successful
        LOG.debug("Received registration ok event.")

        # send the status to the SMR
        status = 'Subscribed to ' + topic ', waiting for alert message'
        message = {'name': self.specific_manager_id,
                   'status': status}
        self.manoconn.publish(topic='specific.manager.registry.ssm.status',
                              message=yaml.dump(message))

        # Subscribing to the topics that the fsm needs to listen on
        topic = "generic.fsm." + str(self.sfuuid)
        self.manoconn.subscribe(self.message_received, topic)
        LOG.debug("Subscribed to " + topic + " topic.")

    def message_received(self, ch, method, props, payload):
        """
        This method handles received messages
        """

        # Decode the content of the message
        content = yaml.load(payload)

        # Create the response
        response = None

        # the 'fsm_type' field in the content indicates for which type of
        # fsm this message is intended. In this case, this FSM functions as
        # start, stop and configure FSM
        if message["fsm_type"] = "start":
            LOG.info("Start event received, content: " + message["content"])
            response = self.start_event(content)

        if message["fsm_type"] = "stop":
            LOG.info("Stop event received, content: " + message["content"])
            response = self.stop_event(content)

        if message["fsm_type"] = "configure":
            LOG.info("Configure event received, content: " + message["content"])
            response = self.configure_event(content)

        # If a response message was generated, send it back to the FLM
        if response is not None:
            # Generated response for the FLM
            topic = "generic.fsm." + str(self.sfuuid)
            corr_id = props.correlation_id
            self.manoconn.notify(topic,
                                 yaml.dump(response),
                                 correlation_id=corr_id)

    def start_event(self, content):
        """
        This method handles a start event.
        """

        # TODO: Add the start logic. The content is a dictionary that contains
        # the required data

        nsr = content['nsr']
        vnfrs = content['vnfrs']

        # Create a response for the FLM
        response = {}
        response['status'] = 'COMPLETED'

        # TODO: complete the response

        return response

    def stop_event(self, content):
        """
        This method handles a stop event.
        """

        # TODO: Add the stop logic. The content is a dictionary that contains
        # the required data

        nsr = content['nsr']
        vnfrs = content['vnfrs']

        # Create a response for the FLM
        response = {}
        response['status'] = 'COMPLETED'

        # TODO: complete the response

        return response

    def configure_event(self, content):
        """
        This method handles a configure event.
        """

        # TODO: Add the configure logic. The content is a dictionary that
        # contains the required data

        nsr = content['nsr']
        vnfrs = content['vnfr']
        nsd = content['nsd']
        vnfds = content['vnfd']

        # Create a response for the FLM
        response = {}
        response['status'] = 'COMPLETED'

        # TODO: complete the response

        return response


def main():
    CssFSM()

if __name__ == '__main__':
    main()
