import argparse
import json

from bmvideohub import VideoHub

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set VideoHub config")
    parser.add_argument("--config", dest="config", type=str, help="config file to read", required=True)
    parser.add_argument("--ip", dest="ip", type=str, help="ip address", required=True)
    parser.add_argument(
        "--port",
        dest="port",
        type=int,
        help="telnet port",
        required=False,
        default=9990,
    )
    parser.add_argument(
        "--route",
        "-r",
        dest="apply_routes",
        action="store_true",
        help="process routes, defaults to False",
        required=False,
        default=False,
    )
    parser.add_argument(
        "--label",
        "-l",
        dest="apply_labels",
        action="store_true",
        help="process labels (implies --input_label and --output_label)",
        required=False,
        default=False,
    )

    parser.add_argument(
        "--input_label",
        "-il",
        dest="apply_input_labels",
        action="store_true",
        help="process input labels, defaults to False",
        required=False,
        default=False,
    )

    parser.add_argument(
        "--output_label",
        "-ol",
        dest="apply_output_labels",
        action="store_true",
        help="process output labels, defaults to False",
        required=False,
        default=False,
    )
    parser.add_argument(
        "--strict",
        "-s",
        dest="strict_mode",
        action="store_true",
        help="Bail if config has more inputs/outputs than VideoHub, defaults to False",
        required=False,
        default=False,
    )
    args = parser.parse_args()

    config_file = args.config
    ip = args.ip
    port = args.port
    apply_routes = args.apply_routes
    apply_labels = args.apply_labels
    apply_input_labels = args.apply_input_labels
    apply_output_labels = args.apply_output_labels
    strict_mode = args.strict_mode
    bail = False
    if apply_labels:
        apply_input_labels = True
        apply_output_labels = True

    try:
        vh = VideoHub(ip, port)
        try:
            with open(config_file) as f:
                try:
                    config = json.loads(f.read())
                except json.decoder.JSONDecodeError:
                    print(f"Error parsing config file {config_file}")
                    exit(1)

                if "inputs" not in config or "outputs" not in config:
                    print(f"Bad formatting config file {config_file}")
                    exit(1)

                num_config_inputs = len(config["inputs"])
                num_config_outputs = len(config["outputs"])
                num_vh_inputs = vh.get_num_inputs()
                num_vh_outputs = vh.get_num_outputs()

                print("=" * 80)
                print(f"Config: {num_config_inputs} inputs, {num_config_outputs} outputs")
                print(f"VideoHub has {num_vh_inputs} inputs and {num_vh_outputs} outputs")
                if num_config_inputs > num_vh_inputs:
                    print("Config has more inputs than VideoHub, skipping extras")
                    bail = True
                if num_config_outputs > num_vh_outputs:
                    print("Config has more outputs than VideoHub, skipping extras")
                    bail = True
                if strict_mode and bail:
                    print("Strict mode enabled, exiting")
                    exit(1)

                print("-" * 40)
                print("Labeling:")
                print("-" * 40)

                if apply_input_labels:
                    bulk_commands = []
                    for input in config["inputs"]:
                        if int(input) < num_vh_inputs:
                            bulk_commands.append((input, config["inputs"][input]["label"]))
                            print(f"Input {input} -> {config['inputs'][input]['label']}")
                    vh.set_bulk_input_label(bulk_commands)
                else:
                    print("-" * 40)
                    print("Skipping input labeling")
                    print("-" * 40)

                if apply_output_labels:
                    bulk_commands = []
                    for output in config["outputs"]:
                        if int(output) < num_vh_outputs:
                            bulk_commands.append((output, config["outputs"][output]["label"]))
                            print(f"Out {output} -> {config['outputs'][output]['label']}")
                    vh.set_bulk_output_label(bulk_commands)
                else:
                    print("-" * 40)
                    print("Skipping output labeling")
                    print("-" * 40)

                if apply_routes:
                    print("-" * 40)
                    print("Routing:")
                    print("Source -> Destination")
                    print("-" * 40)
                    # re read the labels as they may have changed
                    output_labels = vh.get_output_labels()
                    input_labels = vh.get_input_labels()
                    bulk_commands = []
                    for output in output_labels:
                        output_label = output_labels[output]
                        # partial config might not have all outputs
                        # the outputs present
                        if output in config["outputs"]:
                            bulk_commands.append((output, config["outputs"][output]["routing"]))

                    vh.set_bulk_output_route(bulk_commands)
                    output_routing = vh.get_output_routing()
                    for output in output_labels:
                        print(f"{input_labels[output_routing[output]]} -> {output_labels[output]}")
                else:
                    print("-" * 40)
                    print("Skipping routing")
                    print("-" * 40)

                print("=" * 80)
        except FileNotFoundError:
            print(f"Config file {config_file} not found")
            exit(1)
    except (ConnectionRefusedError, OSError):
        print(f"Error connecting to {ip}")
        exit(1)
