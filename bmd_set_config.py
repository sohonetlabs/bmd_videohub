import argparse
import json

from bmvideohub import VideoHub

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Set VideoHub config")
    parser.add_argument(
        "--config", dest="config", type=str, help="config file to read", required=True
    )
    parser.add_argument("--ip", dest="ip", type=str, help="ip address", required=True)
    parser.add_argument(
        "--port",
        dest="port",
        type=str,
        help="telnet port",
        required=False,
        default=9990,
    )

    args = parser.parse_args()

    config_file = args.config
    ip = args.ip
    port = args.port
    try:
        vh = VideoHub(ip, port)
        try:
            with open(config_file, "r") as f:
                try:
                    config = json.loads(f.read())
                except json.decoder.JSONDecodeError as e:
                    print(f"Error parsing config file {config_file}")
                    exit(1)

                if "inputs" not in config or "outputs" not in config:
                    print(f"Bad formatting config file {config_file}")
                    exit(1)

                print("=" * 80)
                print("Labeling:")
                bulk_commands = []
                for input in config["inputs"]:
                    bulk_commands.append((input, config["inputs"][input]["label"]))
                    print(f'Input  {input} label -> {config["inputs"][input]["label"]}')

                vh.set_bulk_input_label(bulk_commands)

                bulk_commands = []
                for output in config["outputs"]:
                    bulk_commands.append((output, config["outputs"][output]["label"]))
                    print(
                        f'Output {output} label -> {config["outputs"][output]["label"]}'
                    )
                vh.set_bulk_output_label(bulk_commands)

                print("-" * 40)
                print("Routing:")
                print("Soruce -> Destination")
                print("-" * 40)
                # re read the lables as they have may have changed
                output_labels = vh.get_output_labels()
                input_labels = vh.get_input_labels()
                bulk_commands = []
                for output in output_labels:
                    output_label = output_labels[output]
                    bulk_commands.append((output, config["outputs"][output]["routing"]))

                vh.set_bulk_output_route(bulk_commands)
                output_routing = vh.get_output_routing()
                for output in output_labels:
                    print(
                        f"{input_labels[output_routing[output]]} -> {output_labels[output]} "
                    )
                print("=" * 80)
        except FileNotFoundError as e:
            print(f"Config file {config_file} not found")
            exit(1)
    except ConnectionRefusedError as e:
        print(f"Error connecting to {ip}")
        exit(1)
