import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    import telnetlib
from threading import Thread
import time
import json

#
# reread the config for every action, as it could have changed since the last action
#
#
#
#


class VideoHub:
    def __init__(self, ip, port=9990):
        self._ip = ip
        self._port = port
        self.state = None
        # conenct and check the protocol version
        self.protocol_version()


    def _rx(self):
        try:
            connection = telnetlib.Telnet(self._ip, self._port, timeout=2)
            state = connection.read_until(b"END PRELUDE:", timeout=2)
            process_state = state.decode("ascii")  # .split('\n')
            return process_state
        except ConnectionRefusedError as e:
            raise e
        except EOFError as e:
            raise e

    def _tx(self, command):
        try:
            connection = telnetlib.Telnet(self._ip, self._port, timeout=2)
            state = connection.read_until(b"END PRELUDE:", timeout=2)
            # ok have prompt now
            connection.write(command.encode("ascii"))
            connection.write("\n\n".encode("ascii"))
            response = connection.read_until(b"ACK\n\n", timeout=2)
            if b"NAK\n\n" in response:
                raise Exception(f"BAD COMMAND {command}")
        except ConnectionRefusedError as e:
            raise e
        except EOFError as e:
            raise e

    def _get_simple_value(self, key):
        state = self._rx()
        for line in state.split("\n"):
            if line.startswith(key):
                return line.split(": ")[1]

    def _get_multi_value(self, key):
        state = self._rx().split("\n")
        in_config = False
        config = {}
        for line in state:

            if line.startswith(key):
                in_config = True
                continue
            if len(line) == 0 and in_config:
                in_config = False
                break
            if in_config:
                index, value = line.split(" ", 1)
                config[str(index)] = value
        return config

    def _set_simple_value(self, key, value):
        self._tx(f"{key}\n {value}\n\n")

    def _set_multi_value(self, key, values):
        cmd_buffer = f"{key}\n"
        for index, value in values:
            cmd_buffer += f"{index} {value}\n"
        cmd_buffer += "\n\n"
        print(cmd_buffer)
        self._tx(cmd_buffer)

    def protocol_version(self):
        return self._get_simple_value("Version:")

    def get_num_inputs(self):
        return int(self._get_simple_value("Video inputs:"))

    def get_num_outputs(self):
        return int(self._get_simple_value("Video outputs:"))

    def get_model_name(self):
        return self._get_simple_value("Model name:")

    def get_UID(self):
        return self._get_simple_value("Unique ID:")

    def get_MAC(self):  
        return self._get_simple_value("MAC Address:")
    
    def get_is_DHCP(self):
        return self._get_simple_value("Dynamic IP:")
    
    def get_IP(self):
        return self._get_simple_value("Current Addresses:").split("/")[0]
    
    def get_IP_netmask(self):
        return self._get_simple_value("Current Addresses:").split("/")[1]
    
    def get_output_routing(self):
        return self._get_multi_value("VIDEO OUTPUT ROUTING:")

    def get_input_labels(self):
        return self._get_multi_value("INPUT LABELS:")

    def get_output_labels(self):
        return self._get_multi_value("OUTPUT LABELS:")

    def get_output_locks(self):
        return self._get_multi_value("VIDEO OUTPUT LOCKS:")

    def set_output_route(self, src, dest):
        self._set_simple_value(f"VIDEO OUTPUT ROUTING:", f"{src} {dest}")

    def set_bulk_output_route(self, routes):
        self._set_multi_value(f"VIDEO OUTPUT ROUTING:", routes)

    def set_input_label(self, index, label):
        max_index = self.get_num_inputs()
        self._set_simple_value(f"INPUT LABELS:", f"{index} {label}")

    def set_bulk_input_label(self, labels):
        self._set_multi_value(f"INPUT LABELS:", labels)

    def set_output_label(self, index, label):
        self._set_simple_value(f"OUTPUT LABELS:", f"{index} {label}")

    def set_bulk_output_label(self, labels):
        self._set_multi_value(f"OUTPUT LABELS:", labels)
