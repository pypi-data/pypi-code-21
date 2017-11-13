import tempfile
import webbrowser

def browser_preview(string_content):
    """ Creates a temporary html file with the string_content, and opens it in a browser
    The script then waits for user input and when entered cleans up the temporary file"""
    with tempfile.NamedTemporaryFile(suffix='.html', delete=True) as file:
        file.write(str(string_content).encode('utf-8'))
        file.flush()
        print(r'file:\\' + file.name)
        webbrowser.open(r'file:///' + file.name.replace('\\', '/'))
        input("Press Enter to end script and clean up temporary file...")
