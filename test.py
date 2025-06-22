import json

from bmvideohub import VideoHub

if __name__ == "__main__":
    vh = VideoHub("10.110.10.108")

    print(vh.protocol_version())
    print(vh.get_num_inputs())
    print(vh.get_num_outputs())
    print(vh.get_model_name())
    print("-")

    print(vh.get_output_routing())
    print("-")
    print(vh.get_input_labels())
    print("-")

    print(vh.get_output_labels())
    print(vh.get_output_locks())
    vh.set_output_route(0, 1)
    vh.set_bulk_output_route([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 0)])
    vh.set_input_label(0, "Test")
    input_label = "FOO"
    vh.set_bulk_input_label(
        [
            (0, "Goose"),
            (1, "Test"),
            (2, "Test"),
            (3, "Test"),
            (4, "Test"),
            (5, "Test"),
            (6, "Test"),
            (7, "Test"),
            (8, "Test"),
            (9, "Test"),
        ]
    )
    vh.set_bulk_output_route(
        [
            (1, 0),
            (2, 1),
            (3, 2),
            (4, 3),
            (5, 4),
            (6, 5),
            (7, 6),
            (8, 7),
            (9, 8),
            (11, 9),
        ]
    )
    vh.set_bulk_output_label(
        [
            (0, "Moose"),
            (1, "Test"),
            (2, "Test"),
            (3, "Test"),
            (4, "Test"),
            (5, "Test"),
            (6, "Test"),
            (7, "Test"),
            (8, "Test"),
            (9, "Test"),
        ]
    )
    vh.set_input_label(0, "Test1")

    inputs = {
        0: {"label": "Test1"},
        1: {"label": "Test2"},
        2: {"label": "Test3"},
        3: {"label": "Test4"},
        4: {"label": "Test5"},
        5: {"label": "Test6"},
        6: {"label": "Test7"},
        7: {"label": "Test8"},
        8: {"label": "Test9"},
        9: {"label": "Test10"},
    }

    input_source = 2

    outputs = {
        0: {"label": "Test1 with spaces", "routing": input_source},
        1: {"label": "Test2", "routing": input_source},
        2: {"label": "Test3", "routing": input_source},
        3: {"label": "Test4", "routing": input_source},
        4: {"label": "Test5", "routing": input_source},
        5: {"label": "Test6", "routing": input_source},
        6: {"label": "Test7", "routing": input_source},
        7: {"label": "Test8", "routing": input_source},
        8: {"label": "Test9", "routing": input_source},
        9: {"label": "Test10", "routing": input_source},
    }

    config = {"inputs": inputs, "outputs": outputs}


test_config = json.dumps(config, indent=2)

config = json.loads(test_config)
print(config)

for input in config["inputs"]:
    print(input, config["inputs"][input]["label"])
    vh.set_input_label(input, config["inputs"][input]["label"])

for output in config["outputs"]:
    print(output, config["outputs"][output]["label"])
    vh.set_output_label(output, config["outputs"][output]["label"])
    vh.set_output_route(output, config["outputs"][output]["routing"])
    print(vh.get_output_routing())

print(json.dumps(config, indent=2))

with open("config.json", "w") as f:
    f.write(json.dumps(config, indent=2))
