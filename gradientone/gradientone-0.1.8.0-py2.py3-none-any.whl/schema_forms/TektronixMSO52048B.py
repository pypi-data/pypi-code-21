from common_elements import gen_channel, FORM_BOTTOM

HORIZONTAL_SCALES = [{"value": value, "name": value,
                      "category": "400GS/s"} for value in
                     ["10us", "5us", "2us",
                      "1us", "500ns", "200ns", "100ns", "50ns", "20ns", "10ns",
                      "5ns", "2.5ns", "1ns", "500ps", "250ps"]] + \
                    [{"value": value, "name": value,
                      "category": "200GS/s"} for value in
                     ["20us", "10us", "5us", "2us",
                      "1us", "500ns", "200ns", "100ns", "50ns", "20ns", "10ns",
                      "5ns", "2.5ns", "1ns", "500ps"]] + \
                    [{"value": value, "name": value,
                      "category": "80GS/s"} for value in
                     ["50us", "20us", "10us", "5us",
                      "2us", "1us", "500ns", "200ns", "100ns", "50ns", "20ns",
                      "10ns", "5ns", "2.5ns"]] + \
                    [{"value": value, "name": value,
                      "category": "40GS/s"} for value in
                     ["100us", "50us", "20us", "10us",
                      "5us", "2us", "1us", "500ns", "200ns", "100ns", "50ns",
                      "20ns", "10ns", "5ns", "2.5ns"]] + \
                    [{"value": value, "name": value,
                      "category": "20GS/s"} for value in
                     ["200us", "100us", "50us", "20us", "10us", "5us", "2us",
                      "1us", "500ns", "200ns", "100ns", "50ns", "20ns", "10ns",
                      "5ns"]] + \
                    [{"value": value, "name": value,
                      "category": "10GS/s"} for value in
                     ["500us", "200us", "100us", "50us", "20us", "10us", "5us",
                      "2us", "1us", "500ns", "200ns", "100ns", "50ns", "20ns",
                      "10ns"]] + \
                    [{"value": value, "name": value,
                      "category": "5GS/s"} for value in
                     ["1ms", "500us", "200us", "100us", "50us", "20us", "10us",
                      "5us", "2us", "1us", "500ns", "200ns", "100ns", "50ns",
                      "20ns"]] + \
                    [{"value": value, "name": value,
                      "category": "2.5GS/s"} for value in
                     ["1ms", "500us", "200us", "100us", "50us", "20us", "10us",
                      "5us", "2us", "1us", "500ns", "200ns", "100ns",
                      "50ns"]] + \
                    [{"value": value, "name": value,
                      "category": "1GS/s"} for value in
                     ["5ms", "1ms", "500us", "200us", "100us", "50us", "20us",
                      "10us", "5us", "2us", "1us", "500ns", "200ns",
                      "100ns"]] + \
                    [{"value": value, "name": value,
                      "category": "500MS/s"} for value in
                     ["10ms", "5ms", "1ms", "500us", "200us", "100us", "50us",
                      "20us", "10us", "5us", "2us", "1us", "500ns", "200ns"]] + \
                    [{"value": value, "name": value,
                      "category": "200MS/s"} for value in
                     ["20ms", "10ms", "5ms", "1ms", "500us", "200us", "100us",
                      "50us", "20us", "10us", "5us", "2us", "1us", "500ns"]] + \
                    [{"value": value, "name": value,
                      "category": "100MS/s"} for value in
                     ["50ms", "20ms", "10ms", "5ms", "1ms", "500us", "200us",
                      "100us", "50us", "20us", "10us", "5us", "2us", "1us"]] + \
                    [{"value": value, "name": value,
                      "category": "50MS/s"} for value in
                     ["100ms", "50ms", "20ms", "10ms", "5ms", "1ms", "500us",
                      "200us", "100us", "50us", "20us", "10us", "5us",
                      "2us"]] + \
                    [{"value": value, "name": value,
                      "category": "20MS/s"} for value in
                     ["200ms", "100ms", "50ms", "20ms", "10ms", "5ms", "1ms",
                      "500us", "200us", "100us", "50us", "20us", "10us",
                      "5us"]] + \
                    [{"value": value, "name": value,
                      "category": "10MS/s"} for value in
                     ["500ms", "200ms", "100ms", "50ms", "20ms", "10ms", "5ms",
                      "1ms", "500us", "200us", "100us", "50us", "20us",
                      "10us"]] + \
                    [{"value": value, "name": value,
                      "category": "5MS/s"} for value in
                     ["1s", "500ms", "200ms", "100ms", "50ms", "20ms", "10ms",
                      "5ms", "1ms", "500us", "200us", "100us", "50us",
                      "20us"]] + \
                    [{"value": value, "name": value,
                      "category": "2MS/s"} for value in
                     ["2s", "1s", "500ms", "200ms", "100ms", "50ms", "20ms",
                      "10ms", "5ms", "1ms", "500us", "200us", "100us",
                      "50us"]] + \
                    [{"value": value, "name": value,
                      "category": "1MS/s"} for value in
                     ["5s", "2s", "1s", "500ms", "200ms", "100ms", "50ms",
                      "20ms", "10ms", "5ms", "1ms", "500us", "200us",
                      "100us"]] + \
                    [{"value": value, "name": value,
                      "category": "500KS/s"} for value in
                     ["10s", "5s", "2s", "1s", "500ms", "200ms", "100ms",
                      "50ms", "20ms", "10ms", "5ms", "1ms", "500us",
                      "200us"]] + \
                    [{"value": value, "name": value,
                      "category": "200KS/s"} for value in
                     ["20s", "10s", "5s", "1s", "500ms", "200ms", "100ms",
                      "50ms", "20ms", "10ms", "5ms", "1ms", "500us"]] + \
                    [{"value": value, "name": value,
                      "category": "100KS/s"} for value in
                     ["50s", "20s", "10s", "5s", "1s", "500ms", "200ms",
                      "100ms", "50ms", "20ms", "10ms", "5ms", "1ms"]] + \
                    [{"value": value, "name": value,
                      "category": "50KS/s"} for value in
                     ["100s", "50s", "20s", "10s", "5s", "1s", "500ms",
                      "200ms", "100ms", "50ms", "20ms", "10ms", "5ms"]] + \
                    [{"value": value, "name": value,
                      "category": "20KS/s"} for value in
                     ["200s", "100s", "50s", "20s", "10s", "5s", "1s", "500ms",
                      "200ms", "100ms", "50ms", "20ms", "10ms"]] + \
                    [{"value": value, "name": value,
                      "category": "10KS/s"} for value in
                     ["500s", "200s", "100s", "50s", "20s", "10s", "5s", "1s",
                      "500ms", "200ms", "100ms", "50ms", "20ms"]] + \
                    [{"value": value, "name": value,
                      "category": "5KS/s"} for value in
                     ["1ks", "500s", "200s", "100s", "50s", "20s", "10s", "5s",
                      "1s", "500ms", "200ms", "100ms", "50ms"]] + \
                    [{"value": value, "name": value,
                      "category": "2KS/s"} for value in
                     ["1ks", "500s", "200s", "100s", "50s", "20s", "10s", "5s",
                      "1s", "500ms", "200ms", "100ms"]] + \
                    [{"value": value, "name": value,
                      "category": "1KS/s"} for value in
                     ["1ks", "500s", "200s", "100s", "50s", "20s", "10s", "5s",
                      "1s", "500ms", "200ms"]] + \
                    [{"value": value, "name": value,
                      "category": "500S/s"} for value in
                     ["1ks", "500s", "200s", "100s", "50s", "20s", "10s", "5s",
                      "1s", "500ms", "200ms"]] + \
                    [{"value": value, "name": value,
                      "category": "200S/s"} for value in
                     ["1ks", "500s", "200s", "100s", "50s", "20s", "10s", "5s",
                      "1s", "500ms", "200ms"]] + \
                    [{"value": value, "name": value,
                      "category": "100S/s"} for value in
                     ["1ks", "500s", "200s", "100s", "50s", "20s", "10s", "5s",
                      "1s", "500ms"]] + \
                    [{"value": value, "name": value,
                      "category": "50S/s"} for value in
                     ["1ks", "500s", "200s", "100s", "50s", "20s", "10s", "5s",
                      "1s"]] + \
                    [{"value": value, "name": value,
                      "category": "20S/s"} for value in
                     ["1ks", "500s", "200s", "100s", "50s", "20s", "10s",
                      "5s"]] + \
                    [{"value": value, "name": value,
                      "category": "10S/s"} for value in
                     ["1ks", "500s", "200s", "100s", "50s", "20s", "10s"]] + \
                    [{"value": value, "name": value,
                      "category": "5S/s"} for value in
                     ["1ks", "500s", "200s", "100s", "50s", "20s"]]

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
                    "default": "normal"

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
        },
        "outputs": {
            "title": "AFG Waveform",
            "type": "object",
            "properties": {
                "enabled": {
                    "title": "Enabled",
                    "type": "boolean",
                    "default": True
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
                "horizontal.title", #WV-I dont think this is doing anything
                "horizontal.mode",
                "horizontal.sample_rate",
                {
                    "key": "horizontal.scale",
                    "type": "strapselect",
                    "default": "50 microseconds",
                    "options": {
                        "multiple": "true",
                        "filterTriggers": ["model.horizontal.sample_rate"],
                        "filter": "item.category.indexOf(model.horizontal.sample_rate) > -1"
                    },
                    "titleMap": HORIZONTAL_SCALES
                },
                "trigger",
                "channels",
                "outputs",
                "output_noise",
                "timebase",
                "g1_measurements"
            ] + FORM_BOTTOM
