from eryx_deploy.assets.web_assets_pipelines.abs_web_assets_pipeline import WebAssetsPipeline


class NullPipeline(WebAssetsPipeline):
    def first_time_setup(self):
        pass  # do nothin

    def run_pipeline(self):
        pass  # do nothin
