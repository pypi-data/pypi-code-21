from guizero import App, PushButton, Text

def main3():
    """Entry point for the application script"""
    print("Call your main application code here")

def do_something():
  print("Button was pressed")
  message.set("Button was pressed")

app = App(title="Hello world")
message = Text(app, text="Welcome to the Hello world app!")
button = PushButton(app, command=do_something)
app.display()
