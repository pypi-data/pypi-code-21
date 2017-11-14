class Buttons(object):
    @staticmethod
    def convert_shortcut_buttons(items):
        """
        support shortcut buttons [{'type':'TEXT', 'title':'text', 'value':'PAYLOAD'}]
        """
        if items is not None and isinstance(items, list):
            result = []
            for item in items:
                if isinstance(item, BaseButton):
                    result.append(item)
                elif isinstance(item, dict):
                    if item.get('type') in ['TEXT', 'LINK', 'OPTION']:
                        type = item.get('type')
                        title = item.get('title')
                        value = item.get('value', item.get('url', item.get('code', item.get('buttons'))))

                        if type == 'TEXT':
                            result.append(ButtonText(title=title, code=value))
                        elif type == 'LINK':
                            moburl = item.get('mobileUrl')
                            result.append(ButtonLink(title=title, url=value, moburl=moburl))
                        elif type == 'OPTION':
                            result.append(ButtonOption(title=title, buttons=value))

                    else:
                        raise ValueError('Invalid button type')
                else:
                    raise ValueError('Invalid buttons variables')
            return result
        else:
            return items


class BaseButton(object):
    pass


class ButtonText(BaseButton):
    def __init__(self, title, code):
        self.type = "TEXT"
        self.data = {"title": title, "code": code}


class ButtonLink(BaseButton):
    def __init__(self, title, url, moburl=None):
        self.type = "LINK"
        self.data = {"title":title, "url":url, "mobileUrl":moburl}


class ButtonOption(BaseButton):
    def __init__(self, title, buttons):
        if not isinstance(buttons, list):
            raise ValueError("Buttons in ButtonOption class must be list")
        self.type = "OPTION"
        self.data = {"title":title, "buttonList": Buttons.convert_shortcut_buttons(buttons)}


class BaseTemplate(object):
    pass


class TextContent(BaseTemplate):
    def __init__(self, text, code=None, quick_reply=None):
        self.text = text
        self.code = code
        if quick_reply is not None:
            self.quickReply = quick_reply


class ImageContent(BaseTemplate):
    def __init__(self, url, quick_reply=None):
        self.imageUrl = url
        if quick_reply is not None:
            self.quickReply = quick_reply


class CompositeContent(BaseTemplate):
    def __init__(self, elements, quick_reply=None):
        if not isinstance(elements, list):
            raise ValueError("Elements type in CompositeContent must be List!")
        self.compositeList = elements
        if quick_reply is not None:
            self.quickReply = quick_reply


class Composite(object):
    def __init__(self, title, description=None, image=None, element=None, buttons=None):
        self.title = title
        self.description = description
        self.image = image
        self.elementList = element
        self.buttonList = Buttons.convert_shortcut_buttons(buttons)


class ElementList(object):
    def __init__(self, data):
        if not isinstance(data, list):
            raise ValueError("data type in ElementList must be List !")
        if len(data) > 3:
            raise IndexError("data length must be less than 3")
        self.type = "LIST"
        self.data = data


class ElementData(object):
    def __init__(self, title, description=None, subdescription=None, image=None, button=None):
        if len(title) > 10:
            raise IndexError("Title length must be less than 10")
        self.title = title
        self.description = description
        self.subDescription = subdescription
        self.image = image
        self.button = button


class QuickReply(object):
    def __init__(self, buttons):
        self.buttonList = Buttons.convert_shortcut_buttons(buttons)

