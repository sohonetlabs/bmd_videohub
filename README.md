# Lib to talk to blackmagic vdieohubs

## usage

    import from bmvideohub import VideoHub

    vh = VideoHub("192.168.1.24")
    input_labels = vh.input_labels = vh.get_input_labels()
    print(input_labels)

## examples
### get_config
        python get_config.py --help
        usage: get_config.py [-h] --config CONFIG --ip IP [--port PORT]

        Set VideoHub config

        options:
        -h, --help       show this help message and exit
        --config CONFIG  config file to write
        --ip IP          ip address
        --port PORT      telnet port

#### example
        get_config.py --config ./examples/test_lab_quad_link.json --ip 192.168.1.24
        {'0': 'Resolve Port 1', '1': 'Resolve Port 2', '2': 'Resolve Port 3', '3': 'Resolve Port 4', '4': 'LON-01 Port 1', '5': 'LON-01 Port 2', '6': 'LON-01 Port 3', '7': 'LON-01 Port 4', '8': 'SPARE', '9': 'DEAD PORT'}
        {
        "inputs": {
            "0": {
            "label": "Resolve Port 1"
            },
            "1": {
            "label": "Resolve Port 2"
            },
            "2": {
            "label": "Resolve Port 3"
            },
            "3": {
            "label": "Resolve Port 4"
            },
            "4": {
            "label": "LON-01 Port 1"
            },
            "5": {
            "label": "LON-01 Port 2"
            },
            "6": {
            "label": "LON-01 Port 3"
            },
            "7": {
            "label": "LON-01 Port 4"
            },
            "8": {
            "label": "SPARE"
            },
            "9": {
            "label": "DEAD PORT"
            }
        },
        "outputs": {
            "0": {
            "label": "LON-02 Port 1",
            "routing": "0"
            },
            "1": {
            "label": "LON-02 Port 2",
            "routing": "1"
            },
            "2": {
            "label": "LON-02 Port 3",
            "routing": "2"
            },
            "3": {
            "label": "LON-02 Port 4",
            "routing": "3"
            },
            "4": {
            "label": "MAC-01 Port 1",
            "routing": "4"
            },
            "5": {
            "label": "MAC-01 Port 2",
            "routing": "5"
            },
            "6": {
            "label": "MAC-01 Port 3",
            "routing": "6"
            },
            "7": {
            "label": "MAC-01 Port 4",
            "routing": "7"
            },
            "8": {
            "label": "MAC-01 4K",
            "routing": "0"
            },
            "9": {
            "label": "Monitor",
            "routing": "0"
            }
        },
        "metadata": {
            "mac": "7c:2e:0d:a6:e3:3d",
            "model": "Blackmagic Videohub 10x10 12G",
            "UID": "2D1968E7F82E46AEB02C22BEAEA196F6",
            "ip": "192.168.1.24",
            "netmask": "255.255.255.0"
        }
        }

### set_config -- read json and write to videohub (labels and routes)

        set_config.py --help
        usage: set_config.py [-h] --config CONFIG --ip IP [--port PORT]

        Set VideoHub config

        options:
        -h, --help       show this help message and exit
        --config CONFIG  config file to read
        --ip IP          ip address
        --port PORT      telnet port

#### example

        set_config.py --config ./examples/test_lab_quad_link.json --ip 192.168.1.24
        ================================================================================
        Labeling:
        Input  0 label -> Resolve Port 1
        Input  1 label -> Resolve Port 2
        Input  2 label -> Resolve Port 3
        Input  3 label -> Resolve Port 4
        Input  4 label -> LON-01 Port 1
        Input  5 label -> LON-01 Port 2
        Input  6 label -> LON-01 Port 3
        Input  7 label -> LON-01 Port 4
        Input  8 label -> SPARE
        Input  9 label -> DEAD PORT
        Output 0 label -> LON-02 Port 1
        Output 1 label -> LON-02 Port 2
        Output 2 label -> LON-02 Port 3
        Output 3 label -> LON-02 Port 4
        Output 4 label -> MAC-01 Port 1
        Output 5 label -> MAC-01 Port 2
        Output 6 label -> MAC-01 Port 3
        Output 7 label -> MAC-01 Port 4
        Output 8 label -> MAC-01 4K
        Output 9 label -> Monitor
        ----------------------------------------
        Routing:
        Soruce -> Destination
        ----------------------------------------
        Resolve Port 1 -> LON-02 Port 1
        Resolve Port 2 -> LON-02 Port 2
        Resolve Port 3 -> LON-02 Port 3
        Resolve Port 4 -> LON-02 Port 4
        LON-01 Port 1 -> MAC-01 Port 1
        LON-01 Port 2 -> MAC-01 Port 2
        LON-01 Port 3 -> MAC-01 Port 3
        LON-01 Port 4 -> MAC-01 Port 4
        Resolve Port 1 -> MAC-01 4K
        Resolve Port 1 -> Monitor
        ================================================================================