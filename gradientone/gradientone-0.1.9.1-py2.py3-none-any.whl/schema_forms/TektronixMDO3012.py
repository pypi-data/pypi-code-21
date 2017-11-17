from common_elements import FORM_BOTTOM

# Todo: populate the defaults from configApp.js
SCHEMA_DICT = {
    "type": "object",
    "title": "Config",
    "properties": {
        "name": {
            "title": "Config Name",
            "type": "string"
        },
        "acquisition": {
            "title": "Acquisition",
            "type": "object",
            "properties": {
                'type': {
                    "title": "Acquisition Mode",
                    "type": "string",
                    "enum": ['normal', 'average', "peak_detect", "envelope",
                             "high_resolution"],
                    "default": "average"
                },
                'start_time': {
                    "title": "Start Time",
                    "type": "number",
                    "default": -4.999999999999996e-06
                },
                'time_per_record': {
                    "title": "Time Per Record",
                    "type": "number",
                    "default": 9.999999999999996e-06
                },
                'number_of_envelopes': {
                    "title": "# of Envelopes",
                    "type": "number",
                    "default": 0
                },
                'number_of_averages': {
                    "default": 512
                },
                'number_of_points_minimum': {
                    "default": 1000
                },

            }
        },
        "horizontal": {
            "title": "Horizontal",
            "type": "object",
            "properties": {
                "mode": {
                    "title": "Horizontal Mode",
                    "type": "string",
                    "enum": ['auto'],
                    "default": "auto"
                },
                "sample_rate": {
                    "title": "Horizontal Sample Rate",
                    "type": "string",
                    "enum": ["400GS/s",
                             "200GS/s",
                             "80GS/s",
                             "40GS/s",
                             "20GS/s",
                             "10GS/s",
                             "5GS/s",
                             "2.5GS/s",
                             "1GS/s",
                             "500MS/s",
                             "200MS/s",
                             "100MS/s",
                             "50MS/s",
                             "20MS/s",
                             "10MS/s",
                             "5MS/s",
                             "2MS/s",
                             "1MS/s",
                             "500Ks/s",
                             "200Ks/s",
                             "100Ks/s",
                             "50Ks/s",
                             "20Ks/s",
                             "10Ks/s",
                             "5kS/s",
                             "2kS/s",
                             "1kS/s",
                             "500S/s",
                             "200S/s",
                             "100S/s",
                             "50S/s",
                             "20S/s",
                             "10S/s",
                             "5S/s"],
                    "default": "50MS/s"
                },
                "scale": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 1,
                    "title": "Horizontal Scale",
                    "default": ["50 microseconds"]

                },

            }
        },
        "trigger": {
            "title": "Trigger",
            "type": "object",
            "properties": {
                "type": {
                    "title": "Type",
                    "type": "string",
                    "enum": ["edge", "runt", "width", "glitch", "tv",
                             "ac_line", "logic", "bus"],
                    "default": "edge"
                },
                "source": {
                    "title": "Source",
                    "type": "string",
                    "default": "ch1"
                },
                "coupling": {
                    "title": "Coupling",
                    "type": "string",
                    "enum": ["ac", "dc", "hf_reject", "if_reject",
                             "noise_reject"],
                    "default": "dc"
                },
                "level": {
                    "title": "Level (V)",
                    "type": "number",
                    "default": 0.288
                }
            }
        },
        "trigger_edge_slope": {
            "title": "Slope",
            "type": "string",
            "enum": ["positive", "negative"],
            "default": "positive"
        },
        "channels": {
            "title": "Channel Settings",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "enabled": {
                        "title": "Enabled",
                        "type": "boolean",
                        "default": True
                    },
                    "range": {
                        "title": "Range (V)",
                        "type": "number",
                        "default": 2
                    },
                    "offset": {
                        "title": "Offset (V)",
                        "type": "number",
                        "default": True
                    },
                    "position": {
                        "title": "Position (V)",
                        "type": "number",
                        "default": 2
                    },
                    "coupling": {
                        "title": "Coupling",
                        "type": "number",
                        "enum": ["dc", "ac"],
                        "default": "dc"
                    },
                },
            },
        },
        "outputs": {
            "title": "AFG Waveform",
            "type": "object",
            "properties": {
                "enabled": {
                    "title": "Enabled",
                    "type": "boolean",
                    "default": False
                },
                "impedence": {
                    "title": "Standard Impedence (e.g. 50)",
                    "type": "number",
                    "default": 50
                }
            }
        },
        "output_noise": {
            "title": "Output Noise",
            "type": "object",
            "properties": {
                "enabled": {
                    "title": "Enabled",
                    "type": "boolean",
                    "default": False
                },
                "percent": {
                    "title": "Noise Percent: (e.g. 50%)",
                    "type": "number",
                    "default": 0
                }
            }
        },
        "standard_waveform": {
            "title": "AFG Settings",
            "type": "object",
            "properties": {
                "waveform": {
                    "title": "Function",
                    "type": "string",
                    "enum": ["sine", "square", "triangle", "ramp_up",
                             "ramp_down", "dc", "pulse", "noise", "sinc",
                             "exprise", "expfall", "cardiac", "gaussian",
                             "expfall", "lorentz", "haversine"],
                    "default": "square"
                },
                "frequency": {
                    "title": "Frequency (Hz)",
                    "type": "number",
                    "default": 2200000
                },
                "amplitude": {
                    "title": "Amplitude",
                    "type": "number",
                    "default": 1
                },
                "dc_offset": {
                    "title": "DC Offset",
                    "type": "number",
                    "default": 0
                },
                "duty_cycle_high": {
                    "title": "Duty Cycle High",
                    "type": "number",
                    "default": 50
                },
                "start_phase": {
                    "title": "Start Phase",
                    "type": "number",
                    "default": 0
                },
                "pulse_width": {
                    "title": "Pulse Width",
                    "type": "number",
                    "default": 1e-6
                },
                "symmetry": {
                    "title": "Symmetry",
                    "type": "number",
                    "default": 50
                }
            }
        }
    },
    "required": [
        "name"
    ]
}

FORM_DICT = [
                {
                    "key": "name",
                    "placeholder": "Tek"
                },
                "acquisition",
                {
                    "key": "acquisition[number_of_averages]",
                    "title": "# of Averages",
                    "type": "select",
                    "titleMap": [
                        {
                            "value": 2,
                            "name": "2"
                        },
                        {
                            "value": 4,
                            "name": "4"
                        },
                        {
                            "value": 8,
                            "name": "8"
                        },
                        {
                            "value": 16,
                            "name": "16"
                        },
                        {
                            "value": 32,
                            "name": "32"
                        },
                        {
                            "value": 64,
                            "name": "64"
                        },
                        {
                            "value": 128,
                            "name": "128"
                        },
                        {
                            "value": 256,
                            "name": "256"
                        },
                        {
                            "value": 512,
                            "name": "512"
                        }
                    ]
                },
                {
                    "key": "acquisition[number_of_points_minimum]",
                    "title": "Minimum Number of Points",
                    "type": "select",
                    "titleMap": [
                        {
                            "value": 1000,
                            "name": "1000"
                        },
                        {
                            "value": 10000,
                            "name": "10000"
                        },
                        {
                            "value": 100000,
                            "name": "100000"
                        },
                        {
                            "value": 1000000,
                            "name": "1000000"
                        },
                        {
                            "value": 5000000,
                            "name": "5000000"
                        },
                        {
                            "value": 10000000,
                            "name": "10000000"
                        }
                    ]
                },
                "trigger",
                {
                    "key": "channels",
                    "items": [
                        "channels[].enabled",
                        "channels[].range",
                        {
                            "key": "channels[0].name",
                            "title": "ch1",
                            "condition": "scope.showSchemaFormField",
                            "default": "ch1"
                        },
                        {
                            "key": "channels[1].name",
                            "title": "ch2",
                            "condition": "scope.showSchemaFormField",
                            "default": "ch2",
                        },
                        {
                            "key": "channels[1].enabled",
                            "default": True,
                        }

                    ],
                    "add": None,
                },
                "outputs",
                "output_noise",
                "standard_waveform",
                "timebase",
                "g1_measurements"
            ] + FORM_BOTTOM
