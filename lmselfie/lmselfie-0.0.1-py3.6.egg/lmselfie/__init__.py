from guizero import App, Text, TextBox, PushButton

def saludar():
    saludo.set("hola " + mi_nombre.get())

app = App(title="Tutin")
welcome_message = Text(app, text="Hola Mundo")
mi_nombre = TextBox(app)
saludo = Text(app)
boton = PushButton(app, command=saludar, text="dar saludo")
app.display()
