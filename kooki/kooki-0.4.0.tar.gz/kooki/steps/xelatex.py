import subprocess, os, shutil

from kooki.tools import write_file
from kooki.tools.output import Output
from kooki import DocumentException

from . import Step

class Xelatex(Step):

    def __init__(self, config):

        super().__init__(config)

        self._name = 'pdf'

    def __call__(self, name, document):

        Output.start_step(self._name)

        tex_file_name = '{0}.tex'.format(name)
        pdf_file_name = '{0}.pdf'.format(name)

        tex_file_path = os.path.join(self.temp_dir, tex_file_name)
        pdf_file_path = os.path.join(self.temp_dir, pdf_file_name)

        write_file(tex_file_path, document)

        command = 'xelatex -interaction=nonstopmode -halt-on-error -output-directory={1} {0}'.format(tex_file_name, self.temp_dir)
        log_file = os.path.join(self.temp_dir, 'xelatex.log')

        with open(log_file, "w") as f:
            subprocess.call(command, shell=True, stdout=f)
            subprocess.call(command, shell=True, stdout=f)

        if Output.debug:
            Output.info('XeLaTeX output: cat {0}'.format(log_file))

        if os.path.isfile(pdf_file_path):
            shutil.copy(pdf_file_path, os.getcwd())
            Output.info('PDF generated: {0}'.format(pdf_file_name))
        else:
            raise DocumentException('pdf is missing')
