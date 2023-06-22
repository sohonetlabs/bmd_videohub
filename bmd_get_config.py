import argparse
import json

from bmvideohub import VideoHub

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set VideoHub config")
    parser.add_argument(
        "--config", dest="config", type=str, help="config file to write", required=True
    )
    parser.add_argument("--ip", dest="ip", type=str, help="ip address", required=True)
    parser.add_argument(
        "--port",
        dest="port",
        type=str,
        help="telnet port defaults to 9990",
        required=False,
        default=9990,
    )

    args = parser.parse_args()

    config_file = args.config
    ip = args.ip
    port = args.port
    try:
        vh = VideoHub(ip, port=port)

        config = {
            "inputs": {},
            "outputs": {},
            "metadata": {},
        }
        print("Getting input labels")
        input_labels = vh.get_input_labels()
        for input in input_labels:
            config["inputs"][str(input)] = {}
            config["inputs"][str(input)]["label"] = input_labels[str(input)]
        print("Getting output labels")
        output_labels = vh.get_output_labels()
        print("Getting routing")
        output_routing = vh.get_output_routing()
        for output in output_labels:
            config["outputs"][str(output)] = {}
            config["outputs"][str(output)]["label"] = output_labels[str(output)]
            config["outputs"][str(output)]["routing"] = output_routing[str(output)]
        print("Getting metadata")
        config["metadata"]["mac"] = vh.get_MAC()
        config["metadata"]["model"] = vh.get_model_name()
        config["metadata"]["UID"] = vh.get_UID()
        config["metadata"]["ip"] = vh.get_IP()
        config["metadata"]["netmask"] = vh.get_IP_netmask()

        print(json.dumps(config, indent=2))

        with open(config_file, "w") as f:
            f.write(json.dumps(config, indent=2))
    except (ConnectionRefusedError, OSError) as e:
        print(f"Connection refused to {ip}")
        exit(1)
