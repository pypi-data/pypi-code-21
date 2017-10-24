# coding:utf-8
from .exceptions import VarNotExist


class Frame:
    def __init__(self, parent_frame, session):
        self.parent_frame = parent_frame
        self.locals = {}
        self.session = session

    def get_var(self, name):
        current_frame = self
        while current_frame is not None:
            if name in current_frame.locals:
                return current_frame.locals[name]
            current_frame = current_frame.parent_frame
        if name in self.session.globals:
            return self.session.globals[name]
        raise VarNotExist(name)

    def set_var(self, name, value, is_global=False):
        if not is_global:
            self.locals[name] = value
        else:
            self.session.globals[name] = value


def get_var_for_call(name, frame):
    if not isinstance(name, str):
        return name
    if name[0] != "$":
        return name
    return frame.get_var(name[1:])


class Session:
    def __init__(self, loop=None):
        self.root_frame = Frame(None, self)
        self.globals = {}
        self.functions = {}
        self.loop = loop

    async def run(self, script):
        main_flow = script["flows"]["main"]
        await self._run_flow_in_frame(main_flow, self.root_frame)

    async def _run_flow_in_frame(self, flow, frame):
        for instruction in flow:
            action_name = instruction["action"]
            args = [get_var_for_call(x, frame)
                    for x in instruction.get("args", ())]
            kwargs = {x: get_var_for_call(y, frame)
                      for x, y in instruction.get("kwargs", {}).items()}

            func = self.functions[action_name]
            await func(frame, *args, **kwargs)
