def _main ():
    import time
    lines = [
        "I'd like to place an order for delivery",
        "Aku",
        "I think I'm in the computer",
        "Yes! That's it",
        "I'd like a large...",
        "What?!",
        "Huh? ...",
        "EXTRA THICK :)",
        "Thirty minutes or it's free??",
        "Excellent!",
        "HA HA HA HA HA HA HA HA",
    ]
    for i, line in enumerate(lines):
        if i:
            time.sleep(1.5)
        print(line)

try:
    _main()
except KeyboardInterrupt:
    pass
