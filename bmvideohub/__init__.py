import warnings
import asyncio, telnetlib3

from threading import Thread
import time
import json

#
# reread the config for every action, as it could have changed since the last action
#
#
#
#


async def _read_until(ip, port, prompt, tx_command=b"", timeout=2):

    output = ""
    # Establish a Telnet connection with timeout
    reader, writer = await telnetlib3.open_connection(host=ip, port=port)

    try:
        if tx_command:
            # eat the preamable
            data = await asyncio.wait_for(
                reader.readuntil(b"END PRELUDE:\n\n"), timeout=timeout
            )

            writer.write(tx_command.decode("ascii"))
            await writer.drain()
        data = await asyncio.wait_for(reader.readuntil(prompt), timeout=timeout)

        output = data.decode("ascii")

    except asyncio.exceptions.TimeoutError as e:
        print(f"timeout reading from {ip}:{port}")
        raise e

    finally:
        reader.close()
        writer.close()
    return output


class VideoHub:
    def __init__(self, ip, port=9990):
        self._ip = ip
        self._port = port
        self.state = None

    def _rx(self):
        result = asyncio.run(
            _read_until(self._ip, self._port, b"END PRELUDE:\n\n")
        )
        return result

    def _tx(self, command):

        try:
            command = command.encode("ascii")
            # can be ACK\n\n or NAK\n\n
            state = asyncio.run(_read_until(self._ip, self._port, b"K\n\n", command))

            if "NAK\n\n" in state:
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
        cmd_buffer += "\n"
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
