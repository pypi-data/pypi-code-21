from eryx_deploy.assets.web_assets_pipelines.abs_web_assets_pipeline import WebAssetsPipeline


class SassCompileWithGrunt(WebAssetsPipeline):
    def first_time_setup(self):
        self._host_machine.install_sass()

    def run_pipeline(self):
        with self._host_machine.cd_project():
            self._host_machine.run("./node_modules/.bin/grunt sass")
