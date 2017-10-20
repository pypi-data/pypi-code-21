from common_elements import gen_channel


COMMON_PROPERTIES = {
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
                "title": "# of Averages",
                "type": "number",
                "default": 512
            },
            'number_of_points_minimum': {
                "title": "Minimum Number of Points",
                "type": "number",
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
        "type": "object",
        "properties": gen_channel(4),
    }
}