import os

class Step():

    def __init__(self, config):
        self.temp_dir = config.temp_dir

    def load_files_in_directory(self, handler, directory, extension):

        content = ''
        files = []

        for file in sorted(os.listdir(directory)):

            if file.endswith(extension):

                extension_name = os.path.splitext(file)[0]

                content += handler(os.path.join(directory, file))
                files.append({'path': os.path.join(directory, file)})

            else:

                sub_directory = os.path.join(directory, file)

                if os.path.isdir(sub_directory):

                    sub_content, sub_files = self.load_files_in_directory(handler, sub_directory, extension)
                    content += sub_content
                    files += sub_files

        return content, files
