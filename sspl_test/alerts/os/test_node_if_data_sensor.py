import json
import os
from time import sleep
import sys

from sspl_test.alerts.os import simulate_network_interface as mock_eth_interface
from sspl_test.default import *
from sspl_test.rabbitmq.rabbitmq_ingress_processor_tests import RabbitMQingressProcessorTests
from sspl_test.rabbitmq.rabbitmq_egress_processor import RabbitMQegressProcessor
from sspl_test.common import check_sspl_ll_is_running

def init(args):
    pass

def test_if_data_sensor(args):
    check_sspl_ll_is_running()
    node_data_sensor_message_request("node:interface:nw")
    if_data_msg = None
    #create dummy interface to get network alerts
    mock_eth_interface.shuffle_nw_interface()
    sleep(4)
    while not world.sspl_modules[RabbitMQingressProcessorTests.name()]._is_my_msgQ_empty():
        ingressMsg = world.sspl_modules[RabbitMQingressProcessorTests.name()]._read_my_msgQ()
        sleep(4)
        print("Received for if_data: {0}".format(ingressMsg))
        try:
            # Make sure we get back the message type that matches the request
            msg_type = ingressMsg.get("sensor_response_type")
            if msg_type["info"]["resource_type"] == "node:interface:nw":
                if_data_msg = msg_type
                break
        except Exception as exception:
            sleep(4)
            print(exception)

    assert(if_data_msg is not None)
    assert(if_data_msg.get("alert_type") is not None)
    assert(if_data_msg.get("alert_id") is not None)
    assert(if_data_msg.get("severity") is not None)
    assert(if_data_msg.get("host_id") is not None)
    assert(if_data_msg.get("info") is not None)
    assert(if_data_msg.get("specific_info") is not None)

    if_data_info = if_data_msg.get("info")
    assert(if_data_info.get("site_id") is not None)
    assert(if_data_info.get("node_id") is not None)
    assert(if_data_info.get("cluster_id") is not None)
    assert(if_data_info.get("rack_id") is not None)
    assert(if_data_info.get("resource_type") is not None)
    assert(if_data_info.get("event_time") is not None)
    assert(if_data_info.get("resource_id") is not None)

    if_data_specific_info = if_data_msg.get("specific_info")
    assert(if_data_specific_info is not None)
    assert(if_data_specific_info.get("localtime") is not None)
    assert(if_data_specific_info.get("interfaces") is not None)


def node_data_sensor_message_request(sensor_type):
    egressMsg = {
        "title": "SSPL Actuator Request",
        "description": "Seagate Storage Platform Library - Actuator Request",

        "username" : "JohnDoe",
        "signature" : "None",
        "time" : "2015-05-29 14:28:30.974749",
        "expires" : 500,

        "message" : {
            "sspl_ll_msg_header": {
                "schema_version": "1.0.0",
                "sspl_version": "1.0.0",
                "msg_version": "1.0.0"
            },
             "sspl_ll_debug": {
                "debug_component" : "sensor",
                "debug_enabled" : True
            },
            "sensor_request_type": {
                "node_data": {
                    "sensor_type": sensor_type
                }
            }
        }
    }

    world.sspl_modules[RabbitMQegressProcessor.name()]._write_internal_msgQ(RabbitMQegressProcessor.name(), egressMsg)


test_list = [test_if_data_sensor]