

def bind_events(control,
                events,
                function):

    for event in events:
        control.bind(event, function)
