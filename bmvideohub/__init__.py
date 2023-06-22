import asyncio
import json
import logging
import sys
import time
import warnings

import telnetlib3

#
# reread the config for every action, as it could have changed since the last action
# no state is stored in the library other than the IP address, port
#
#
#
# logging.basicConfig(level=logging.DEBUG)


async def _read_until(ip, port, prompt, tx_command=b"", timeout=2):

    output = ""
    # Establish a Telnet connection, connect_minwait=2seconds is the default,
    # reduce it to 10ms to speed up
    reader, writer = await telnetlib3.open_connection(
        host=ip, port=port, connect_minwait=0.01
    )

    try:
        if tx_command:
            # eat the preamable on connect as it is not needed
            data = await asyncio.wait_for(
                reader.readuntil(b"\n\n"), timeout=timeout
            )

            writer.write(tx_command.decode("ascii"))
            await writer.drain()
        data = await asyncio.wait_for(reader.readuntil(prompt), timeout=timeout)

        output = data.decode("ascii")

    except asyncio.exceptions.TimeoutError as e:
        print(f"Timeout reading from {ip}:{port}")
        raise e

    finally:
        reader.close()
        writer.close()
    return output


class VideoHub:
    def __init__(self, ip, port=9990):
        """Connect to a Blackmagic VideoHub takes an IP address and port number
        port is optional and defaults to 9990"""
        self._ip = ip
        self._port = port
        # check we can connect
        self.ping()

    def _rx(self):
        result = asyncio.run(_read_until(self._ip, self._port, b"END PRELUDE:\n\n"))
        return result

    def _tx(self, command):

        try:
            command = command.encode("ascii")
            # can be ACK\n\n or NAK\n\n
            state = asyncio.run(_read_until(self._ip, self._port, b"K\n\n", command))

            if "\nNAK" in state:
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
        raise Exception(f"Key {key} not found")

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

    def ping(self):
        """Pings the VideoHub, basically a no-op"""
        self._tx("PING:\n\n")

    def protocol_version(self):
        """Returns the protocol version of the VideoHub as string"""
        return self._get_simple_value("Version:")

    def get_num_inputs(self):
        """Returns the number of inputs as int"""
        return int(self._get_simple_value("Video inputs:"))

    def get_num_outputs(self):
        """Returns the number of outputs as int"""
        return int(self._get_simple_value("Video outputs:"))

    def get_model_name(self):
        """Returns the model name of the VideoHub as string eg Blackmagic Videohub 10x10 12G"""
        return self._get_simple_value("Model name:")

    def get_friendly_name(self):
        """Returns the firendly name of the VideoHub as string eg Blackmagic Videohub 10x10 12G"""
        return self._get_simple_value("Friendly name:")

    def get_UID(self):
        """Returns the unique ID of the VideoHub as string"""
        return self._get_simple_value("Unique ID:")

    def get_MAC(self):
        """Returns the MAC address of the VideoHub as string"""
        return self._get_simple_value("MAC Address:")

    def get_is_DHCP(self):
        """Returns True if the VideoHub is using DHCP"""
        value = self._get_simple_value("Dynamic IP:")
        if value == "true":
            return True
        else:
            return False

    def get_IP(self):
        """Returns the IP address of the VideoHub as string"""
        return self._get_simple_value("Current Addresses:").split("/")[0]

    def get_IP_netmask(self):
        """Returns the IP netmask of the VideoHub as string"""
        return self._get_simple_value("Current Addresses:").split("/")[1]

    def get_output_routing(self):
        """Returns the output routing as dict indexed by output number
        eg {'1': '1', '2': '2', '3': '3', '4': '4', '5': '5',}"""
        return self._get_multi_value("VIDEO OUTPUT ROUTING:")

    def get_input_labels(self):
        """Returns the input labels as dict indexed by input number"""
        return self._get_multi_value("INPUT LABELS:")

    def get_output_labels(self):
        """Returns the output labels as dict indexed by output number"""
        return self._get_multi_value("OUTPUT LABELS:")

    def get_output_locks(self):
        """Returns the output locks as dict indexed by output number
        Each port has a lock status of “O” for ports that are owned by the current client
        (i.e., locked from the same IP address), “L” for ports that are locked from a
        different client, or “U” for unlocked."""
        return self._get_multi_value("VIDEO OUTPUT LOCKS:")

    def get_take_mode(self):
        """Returns the take mode as dict indexed by output number"""
        take_mode = self._get_multi_value("TAKE MODE:")
        bool_take_mode = {}
        for key, value in take_mode.items():
            if value == "true":
                bool_take_mode[key] = True
            else:
                bool_take_mode[key] = False
        return bool_take_mode

    def set_output_route(self, src, dest):
        """Sets the output route for a single output"""
        self._set_simple_value(f"VIDEO OUTPUT ROUTING:", f"{src} {dest}")

    def set_bulk_output_route(self, routes):
        """Sets the output route for multiple outputs takes a list of tuples
        eg [(1,1),(2,2),(3,3),(4,4),(5,5)]"""
        self._set_multi_value(f"VIDEO OUTPUT ROUTING:", routes)

    def set_input_label(self, index, label):
        """Sets the input label for a single input"""
        self._set_simple_value(f"INPUT LABELS:", f"{index} {label}")

    def set_bulk_input_label(self, labels):
        """Sets the input label for multiple inputs takes a list of tuples
        eg [(1,1),(2,2),(3,3),(4,4),(5,5)]"""
        self._set_multi_value(f"INPUT LABELS:", labels)

    def set_output_label(self, index, label):
        """Sets the output label for a single output"""
        self._set_simple_value(f"OUTPUT LABELS:", f"{index} {label}")

    def set_bulk_output_label(self, labels):
        """Sets the output label for multiple outputs takes a list of tuples"""
        self._set_multi_value(f"OUTPUT LABELS:", labels)

    def set_output_lock(self, index, state):
        """Sets the output lock for a single output
        Each port has a lock status of “O” for ports that are owned by the current client
        (i.e., locked from the same IP address), “L” for ports that are locked from a
        different client, or “U” for unlocked.
        Can only be set to O or U
        """
        if state not in ["O", "U"]:
            raise Exception("OUTPUT LOCK must be O, or U, not {state}")
        self._set_simple_value(f"VIDEO OUTPUT LOCKS:", f"{index} {state}")

    def set_bulk_output_lock(self, locks):
        """Sets the output lock for multiple outputs takes a list of tuples.
        Each port has a lock status of “O” for ports that are owned by the current client
        (i.e., locked from the same IP address), “L” for ports that are locked from a
        different client, or “U” for unlocked.
        Can only be set to O or U
        """
        for index, state in locks:
            if state not in ["O", "U"]:
                raise Exception("OUTPUT LOCK must be O, U, not {index}, {state}")
        self._set_multi_value(f"VIDEO OUTPUT LOCKS:", locks)

    def set_take_mode(self, index, mode):
        """Sets the take mode for a single output takes bool eg true or false"""
        if mode:
            mode = "true"
        else:
            mode = "false"
        self._set_simple_value(f"TAKE MODE:", f"{index} {mode}")

    def set_bulk_take_mode(self, modes):
        """Sets the take mode for multiple outputs takes a list of tuples eg true or false"""
        str_modes = []
        for index, mode in modes:
            if mode:
                str_mode = "true"
            else:
                str_mode = "false"
            str_modes.append((index, str_mode))
        self._set_multi_value(f"TAKE MODE:", str_modes)
