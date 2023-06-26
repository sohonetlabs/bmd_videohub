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
        help="process lables, defaults to False, implies --input_label and --output_label",
        required=False,
        default=False,
    )

    parser.add_argument(
        "--input_label",
        "-il",
        dest="apply_input_labels",
        action="store_true",
        help="process input lables, defaults to False",
        required=False,
        default=False,
    )

    parser.add_argument(
        "--output_label",
        "-ol",
        dest="apply_output_labels",
        action="store_true",
        help="process output lables, defaults to False",
        required=False,
        default=False,
    )
    parser.add_argument(
        "--strict",
        "-s",
        dest="strict_mode",
        action="store_true",
        help="Bail if there are more inputs or outputs in the config file than the VideoHub, defaults to False",
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
            with open(config_file, "r") as f:
                try:
                    config = json.loads(f.read())
                except json.decoder.JSONDecodeError as e:
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
                print(
                    f"Config file has {num_config_inputs} inputs and {num_config_outputs} outputs"
                )
                print(
                    f"VideoHub has {num_vh_inputs} inputs and {num_vh_outputs} outputs"
                )
                if num_config_inputs > num_vh_inputs:
                    print(
                        f"Config file has more inputs than VideoHub, skipping additional inputs"
                    )
                    bail = True
                if num_config_outputs > num_vh_outputs:
                    print(
                        f"Config file has more outputs than VideoHub, skipping additional outputs"
                    )
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
                            bulk_commands.append(
                                (input, config["inputs"][input]["label"])
                            )
                            print(
                                f'Input  {input} label -> {config["inputs"][input]["label"]}'
                            )
                    vh.set_bulk_input_label(bulk_commands)
                else:
                    print("-" * 40)
                    print("Skipping input labeling")
                    print("-" * 40)

                if apply_output_labels:
                    bulk_commands = []
                    for output in config["outputs"]:
                        if int(output) < num_vh_outputs:
                            bulk_commands.append(
                                (output, config["outputs"][output]["label"])
                            )
                            print(
                                f'Output {output} label -> {config["outputs"][output]["label"]}'
                            )
                    vh.set_bulk_output_label(bulk_commands)
                else:
                    print("-" * 40)
                    print("Skipping output labeling")
                    print("-" * 40)

                if apply_routes:
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
                        # this might be partial set from the config so might not have all of
                        # the outputs present
                        if output in config["outputs"]:
                            bulk_commands.append(
                                (output, config["outputs"][output]["routing"])
                            )

                    vh.set_bulk_output_route(bulk_commands)
                    output_routing = vh.get_output_routing()
                    for output in output_labels:
                        print(
                            f"{input_labels[output_routing[output]]} -> {output_labels[output]} "
                        )
                else:
                    print("-" * 40)
                    print("Skipping routing")
                    print("-" * 40)

                print("=" * 80)
        except FileNotFoundError as e:
            print(f"Config file {config_file} not found")
            exit(1)
    except (ConnectionRefusedError, OSError) as e:
        print(f"Error connecting to {ip}")
        exit(1)
