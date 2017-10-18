import os
import unittest
import time
import random
from DKCloudCommand.modules.utils.DKFileUtils import DKFileUtils
from subprocess import Popen, PIPE

BASE_PATH = os.environ.get('DK_CLI_SMOKE_TEST_BASE_PATH', '/home/vagrant')
EMAIL = os.environ.get('DK_CLI_SMOKE_TEST_EMAIL', 'alex@datakitchen.io')


class TestQuickStart(unittest.TestCase):
    # ---------------------------- Test setUp and tearDown methods ---------------------------
    def setUp(self):
        print '\n\n####################### Setup #######################'
        print 'BASE_PATH: %s' % BASE_PATH
        print 'EMAIL: %s' % EMAIL
        pass

    def tearDown(self):
        print '\n####################### Quick Start 1 has finished #######################'

        print '\n\n####################### TearDown #######################'

        if self.master_kitchen is not None:
            print '-> Deleting unit test master kitchen %s' % self.master_kitchen
            self.dk_kitchen_delete(self.master_kitchen)

        print '-> Removing local files from path %s' % self.kitchens_path
        command = 'rm -rf %s' % self.kitchens_path
        self.run_command(command)

        pass

    # ---------------------------- System tests ---------------------------
    def test_quick_start_1(self):
        print '\n\n####################### Starting Quick Start 1 #######################'
        print '\n---- Pre-Heat the Oven ----'

        print '-> Local path prep'
        test_id = 'cli-smoke-test-1-%05d-' % random.randint(0, 10000)
        self.kitchens_path = BASE_PATH+'/CLISmokeTestKitchens'
        kitchens_path = self.kitchens_path
        DKFileUtils.create_dir_if_not_exists(kitchens_path)
        self.set_working_directory(kitchens_path)

        print '-> Make sure CLI is working'
        self.dk_help()

        print '-> Make sure CLI is pointing at dk repo (a +dk email configured)'
        self.dk_config_list()

        print '\n----- The Master Kitchen -----'

        print '-> List current kitchens'
        self.dk_kitchen_list()

        print '-> Create new kitchen master for unit test'
        self.master_kitchen = '%sMaster' % test_id
        self.dk_kitchen_create(self.master_kitchen, parent='master')

        print '-> Create new kitchen unit test Production'
        production_kitchen = '%sProduction' % test_id
        self.dk_kitchen_create(production_kitchen, parent=self.master_kitchen)

        print '-> Create new kitchen unit test Dev-Sprint-1'
        dev_sprint_1_kitchen = '%sDev-Sprint-1' % test_id
        self.dk_kitchen_create(dev_sprint_1_kitchen, parent=production_kitchen)

        print '-> Create new kitchen unit test Feature_Sprint_1'
        feature_sprint_1_kitchen = '%sFeature-Sprint-1' % test_id
        self.dk_kitchen_create(feature_sprint_1_kitchen, parent=dev_sprint_1_kitchen)

        print '-> List kitchens and check the new ones'
        checks = list()
        checks.append(self.master_kitchen)
        checks.append(production_kitchen)
        checks.append(dev_sprint_1_kitchen)
        checks.append(feature_sprint_1_kitchen)
        self.dk_kitchen_list(checks)

        print '\n----- Get Kitchen to Local -----'

        print '-> Get kitchen to local: Feature_Sprint_1'
        self.dk_kitchen_get(feature_sprint_1_kitchen)
        feature_sprint_1_kitchen_local_dir = '%s/%s' % (kitchens_path, feature_sprint_1_kitchen)
        self.assertTrue(os.path.exists(feature_sprint_1_kitchen_local_dir))

        print '\n----- List Recipes -----'

        print '-> Set local working directory as: %s' % feature_sprint_1_kitchen_local_dir
        self.set_working_directory(feature_sprint_1_kitchen_local_dir)

        print '-> Perform a recipe list'
        self.dk_recipe_list(feature_sprint_1_kitchen)

        print '\n----- Create a Recipe -----'

        recipe_name = 'CLI-QS1-Recipe-Template'
        print '-> Creating the recipe \'%s\'' % recipe_name
        self.dk_recipe_create(feature_sprint_1_kitchen, recipe_name)

        print '-> Performing a recipe list checking %s' % recipe_name
        self.dk_recipe_list(feature_sprint_1_kitchen, checks=[recipe_name])

        print '\n----- Get Local Recipe Copy -----'

        print '-> Get the recipe %s' % recipe_name
        expected_paths = list()
        expected_paths.append('%s/resources' % recipe_name)
        expected_paths.append('%s/resources/email-templates' % recipe_name)
        expected_paths.append('%s/placeholder-node1' % recipe_name)
        expected_paths.append('%s/placeholder-node2' % recipe_name)

        checks = list()
        checks.extend(expected_paths)
        self.dk_recipe_get(feature_sprint_1_kitchen, recipe_name, checks=checks)
        for path in expected_paths:
            self.assertTrue(os.path.exists('%s/%s' % (feature_sprint_1_kitchen_local_dir, path)))

        print '\n----- View Recipe Variations -----'

        recipe_template_local_dir = '%s/%s/%s' % (kitchens_path, feature_sprint_1_kitchen, recipe_name)
        print '-> Set local working directory as: %s' % recipe_template_local_dir
        self.assertTrue(os.path.exists(recipe_template_local_dir))
        self.set_working_directory(recipe_template_local_dir)

        print '-> Get recipe variation list'
        self.dk_recipe_variation_list(feature_sprint_1_kitchen, recipe_name)

        print '\n----- Recipe Structure -----'

        print '-> Listing recipe structure'
        checks = list()

        checks.append('description.json')
        checks.append('graph.json')
        checks.append('variables.json')
        checks.append('variations.json')
        checks.append('placeholder-node1')
        checks.append('placeholder-node2')
        checks.append('description.json')
        checks.append('resources')
        checks.append('email-templates')
        checks.append('README.txt')
        checks.append('resources/email-templates')
        checks.append('dk_recipe_done_email_template.html')
        checks.append('dk_recipe_over_duration_email_template.html')
        checks.append('dk_recipe_startup_email_template.html')

        command = 'ls -R *'
        self.run_command(command, checks)

        print '\n----- Which Kitchen? -----'

        print '-> Executing which kitchen command'
        self.dk_kitchen_which(feature_sprint_1_kitchen)

        print '\n----- Recipe Status -----'

        print '-> Executing recipe status command'
        self.dk_recipe_status(feature_sprint_1_kitchen, recipe_name, qty_of_unchanged_files=10)

        print '\n----- Local Recipe Change -----'

        print '-> Changing variables.json with email'
        variables_json_full_path = '%s/variables.json' % recipe_template_local_dir
        file_contents = DKFileUtils.read_file(variables_json_full_path)
        file_contents = file_contents.replace('[YOUR EMAIL HERE]', EMAIL)
        DKFileUtils.write_file(variables_json_full_path, file_contents)

        print '-> Executing recipe status command to verify changes'
        checks = list()
        checks.append('variables.json')
        self.dk_recipe_status(feature_sprint_1_kitchen, recipe_name,
                              qty_of_local_changed_files=1,
                              qty_of_unchanged_files=9,
                              checks=checks)

        print '\n----- Update: Local to Remote -----'
        print '-> Executing file-update for variables.json'
        self.dk_file_update(feature_sprint_1_kitchen, recipe_name,
                            'variables.json',
                            'CLI Smoke Test Quick Start 1 - Push email value update within variables.json')

        print '-> Executing recipe-status to make sure there are no more local changes'
        self.dk_recipe_status(feature_sprint_1_kitchen, recipe_name, qty_of_unchanged_files=10)

        print '\n----- Run an Order -----'
        print '-> Running the order'
        order_id = self.dk_order_run(feature_sprint_1_kitchen, recipe_name, 'Variation1')

        print '\n----- View Order-Run Details -----'

        print '-> Pulling order run status: Start'
        retry_qty = 30
        order_run_completed = False
        seconds = 60
        while not order_run_completed and retry_qty > 0:
            retry_qty = retry_qty - 1
            print '-> Waiting %d seconds ' % seconds
            time.sleep(seconds)

            print '-> Pull order run status'
            order_run_completed = self.dk_order_run_info(feature_sprint_1_kitchen, recipe_name, 'Variation1', order_id)

        self.assertTrue(order_run_completed, msg='Order run has not shown as completed after multiple status fetch')
        print '-> Pulling order run status: Done'

        print '\n----- Merge Parent to Child -----'

        print '-> Reverse merge: Dev_Sprint_1 to Feature_Sprint_1 - Preview'
        self.set_working_directory(kitchens_path)
        source_kitchen = dev_sprint_1_kitchen
        target_kitchen = feature_sprint_1_kitchen

        checks = list()
        checks.append('Nothing to merge.')
        self.dk_kitchen_merge_preview(source_kitchen, target_kitchen, checks=checks)

        print '-> Reverse merge: Dev_Sprint_1 to Feature_Sprint_1 - Actual Merge'
        checks = list()
        checks.append('base already contains the head, nothing to merge')
        self.dk_kitchen_merge(source_kitchen, target_kitchen, checks=checks)

        print '\n----- Merge Child to Parent -----'

        print '-> Before the merge, make sure recipe is not already present in parent kitchen Dev_Sprint_1'
        self.set_working_directory(kitchens_path)
        self.dk_kitchen_get(dev_sprint_1_kitchen)
        dev_sprint_1_kitchen_local_dir = '%s/%s' % (kitchens_path, dev_sprint_1_kitchen)
        self.assertTrue(os.path.exists(dev_sprint_1_kitchen_local_dir))
        self.set_working_directory(dev_sprint_1_kitchen_local_dir)

        command_output = self.dk_recipe_list(dev_sprint_1_kitchen)
        self.assertTrue(recipe_name not in command_output)

        print '-> Switching back to Feature_Sprint_1 path'
        recipe_template_local_dir = '%s/%s/%s' % (kitchens_path, feature_sprint_1_kitchen, recipe_name)
        print '-> Set local working directory as: %s' % recipe_template_local_dir
        self.assertTrue(os.path.exists(recipe_template_local_dir))
        self.set_working_directory(recipe_template_local_dir)

        print '-> Merge: Feature_Sprint_1 to Dev_Sprint_1 - Preview'
        source_kitchen = feature_sprint_1_kitchen
        target_kitchen = dev_sprint_1_kitchen

        checks = list()
        checks.append('      ok		%s/resources/email-templates/dk_recipe_over_duration_email_template.html' % recipe_name)
        checks.append('      ok		%s/resources/email-templates/dk_recipe_startup_email_template.html' % recipe_name)
        checks.append('      ok		%s/resources/email-templates/dk_recipe_done_email_template.html' % recipe_name)
        checks.append('      ok		%s/resources/README.txt' % recipe_name)
        checks.append('      ok		%s/placeholder-node1/description.json' % recipe_name)
        checks.append('      ok		%s/variations.json' % recipe_name)
        checks.append('      ok		%s/description.json' % recipe_name)
        checks.append('      ok		%s/placeholder-node2/description.json' % recipe_name)
        checks.append('      ok		%s/graph.json' % recipe_name)
        checks.append('      ok		%s/variables.json' % recipe_name)
        self.dk_kitchen_merge_preview(source_kitchen, target_kitchen, checks=checks)

        print '-> Merge: Feature_Sprint_1 to Dev_Sprint_1 - Actual Merge'
        checks = list()
        checks.append('description.json')
        checks.append('graph.json')
        checks.append('variables.json')
        checks.append('variations.json')
        checks.append('README.txt')
        checks.append('dk_recipe_done_email_template.html')
        checks.append('dk_recipe_over_duration_email_template.html')
        checks.append('dk_recipe_startup_email_template.html')
        checks.append('10 files changed')

        self.dk_kitchen_merge(source_kitchen, target_kitchen, checks=checks)

        print '-> Checking recipe list in parent kitchen (Dev_Sprint_1) contains new recipe'
        dev_sprint_1_kitchen_local_dir = '%s/%s' % (kitchens_path, dev_sprint_1_kitchen)
        self.set_working_directory(dev_sprint_1_kitchen_local_dir)

        checks = list()
        checks.append(recipe_name)
        self.dk_recipe_list(dev_sprint_1_kitchen, checks=checks)

        print '\n----- Delete Dev Kitchen -----'

        for kitchen_name in [feature_sprint_1_kitchen, dev_sprint_1_kitchen, production_kitchen]:
            print '-> Deleting kitchen %s' % kitchen_name
            self.dk_kitchen_delete(kitchen_name)

            print '-> Checking that %s is not in kitchen list any more' % kitchen_name
            command_output = self.dk_kitchen_list()
            self.assertTrue(kitchen_name not in command_output)

    # ---------------------------- Helper methods ---------------------------
    def dk_kitchen_delete(self, kitchen_name, checks=None):
        if checks is None:
            checks = list()
        checks.append('Child kitchens for kitchen %s' % kitchen_name)
        checks.append('- Deleting kitchen %s' % kitchen_name)
        checks.append('deleted kitchen %s' % kitchen_name)
        command = 'dk kitchen-delete %s --yes' % kitchen_name
        sout = self.run_command(command, checks)
        return sout

    def dk_kitchen_merge_preview(self, source_kitchen, target_kitchen, checks=None):
        if checks is None:
            checks = list()
        checks.append('- Previewing merge Kitchen %s into Kitchen %s' % (source_kitchen, target_kitchen))
        checks.append('Merge Preview Results (only changed files are being displayed):')
        checks.append('--------------------------------------------------------------')
        checks.append('Kitchen merge preview done.')
        command = 'dk kitchen-merge-preview -cpr --source_kitchen %s --target_kitchen %s' % (source_kitchen, target_kitchen)
        sout = self.run_command(command, checks)
        return sout

    def dk_kitchen_merge(self, source_kitchen, target_kitchen, checks=None):
        if checks is None:
            checks = list()
        checks.append('- Merging Kitchen %s into Kitchen %s' % (source_kitchen, target_kitchen))
        checks.append('Calling Merge ...')
        command = 'dk kitchen-merge --source_kitchen %s --target_kitchen %s --yes' % (source_kitchen, target_kitchen)
        sout = self.run_command(command, checks)
        return sout

    def dk_order_run_info(self, kitchen_name, recipe_name, variation, order_id, checks=None):
        if checks is None:
            checks = list()
        checks.append(' - Display Order-Run details from kitchen %s' % kitchen_name)
        checks.append('ORDER RUN SUMMARY')
        checks.append('Order ID:\t%s' % order_id)
        checks.append('Kitchen:\t%s' % kitchen_name)
        checks.append('Variation:\t%s' % variation)
        checks.append('COMPLETED_SERVING')
        command = 'dk orderrun-info'
        try:
            self.run_command(command, checks)
        except Exception:
            return False
        return True

    def dk_order_run(self, kitchen_name, recipe_name, variation, checks=None):
        if checks is None:
            checks = list()
        checks.append(' - Create an Order')
        checks.append('Kitchen: %s' % kitchen_name)
        checks.append('Recipe: %s' % recipe_name)
        checks.append('Variation: %s' % variation)
        checks.append('Order ID is: DKRecipe#dk#%s#%s#%s#' % (recipe_name, variation, kitchen_name))
        command = 'dk order-run %s --yes' % variation
        sout = self.run_command(command, checks)
        aux_string = 'Order ID is: '
        aux_index = sout.find(aux_string)
        order_id = sout[aux_index+len(aux_string):-1]
        return order_id

    def dk_file_update(self, kitchen_name, recipe_name, file_name, message, checks=None):
        if checks is None:
            checks = list()
        checks.append('Updating File(s)')
        checks.append('in Recipe (%s) in Kitchen(%s) with message (%s)' % (recipe_name, kitchen_name, message))
        checks.append('DKCloudCommand.update_file for %s succeeded' % file_name)
        command = 'dk file-update --message "%s" %s' % (message, file_name)
        sout = self.run_command(command, checks)
        return sout

    def dk_recipe_status(self, kitchen_name, recipe_name, qty_of_unchanged_files=None, qty_of_local_changed_files=None, checks=None):
        if checks is None:
            checks = list()

        checks.append('- Getting the status of Recipe \'%s\' in Kitchen \'%s\'' % (recipe_name, kitchen_name))
        if qty_of_unchanged_files is not None:
            checks.append('%d files are unchanged' % qty_of_unchanged_files)
        if qty_of_local_changed_files is not None:
            checks.append('%d files are modified on local' % qty_of_local_changed_files)

        command = 'dk recipe-status'
        sout = self.run_command(command, checks)
        return sout

    def dk_kitchen_which(self, expected_kitchen_name, checks=None):
        if checks is None:
            checks = list()
        checks.append('You are in kitchen \'%s\'' % expected_kitchen_name)
        command = 'dk kitchen-which'
        sout = self.run_command(command, checks)
        return sout

    def dk_recipe_variation_list(self, kitchen_name, recipe_name, checks=None):
        if checks is None:
            checks = list()
        checks.append(' - Listing variations for recipe %s in Kitchen %s' % (recipe_name, kitchen_name))
        checks.append('Variations:')
        checks.append('Variation1')
        command = 'dk recipe-variation-list'
        sout = self.run_command(command, checks)
        return sout

    def dk_recipe_get(self, kitchen_name, recipe_name, checks=None):
        if checks is None:
            checks = list()
        checks.append(' - Getting the latest version of Recipe \'%s\' in Kitchen \'%s\'' % (recipe_name, kitchen_name))
        checks.append('DKCloudCommand.get_recipe has')
        checks.append('sections')
        command = 'dk recipe-get %s' % recipe_name
        sout = self.run_command(command, checks)
        return sout

    def dk_recipe_create(self, kitchen_name, recipe_name, checks=None):
        if checks is None:
            checks = list()
        checks.append('- Creating Recipe %s for Kitchen \'%s\'' % (recipe_name, kitchen_name))
        checks.append('DKCloudCommand.recipe_create created recipe %s' % recipe_name)
        command = 'dk recipe-create %s' % recipe_name
        sout = self.run_command(command, checks)
        return sout

    def dk_recipe_list(self, kitchen_name, checks=None):
        if checks is None:
            checks = list()
        checks.append('- Getting the list of Recipes for Kitchen \'%s\'' % kitchen_name)
        checks.append('DKCloudCommand.list_recipe returned')
        checks.append('recipes')
        command = 'dk recipe-list'
        sout = self.run_command(command, checks)
        return sout

    def dk_kitchen_get(self, kitchen_name, checks=None):
        if checks is None:
            checks = list()
        checks.append(' - Getting kitchen \'%s\'' % kitchen_name)
        checks.append('Got Kitchen \'%s\'' % kitchen_name)
        command = 'dk kitchen-get %s' % kitchen_name
        sout = self.run_command(command, checks)
        return sout

    def dk_kitchen_create(self, kitchen_name, parent='master', checks=None):
        if checks is None:
            checks = list()
        checks.append(' - Creating kitchen %s from parent kitchen %s' % (kitchen_name, parent))
        checks.append('DKCloudCommand.create_kitchen created %s' % kitchen_name)
        command = 'dk kitchen-create -p %s %s' % (parent, kitchen_name)
        sout = self.run_command(command, checks)
        return sout

    def dk_config_list(self, checks=None):
        if checks is None:
            checks = list()
        checks.append('+dk@datakitchen.io')
        checks.append('Username')
        checks.append('Password')
        checks.append('Cloud IP')
        checks.append('Cloud Port')
        checks.append('Cloud File Location')
        checks.append('Merge Tool')
        checks.append('Diff Tool')
        sout = self.run_command('dk config-list', checks)
        return sout

    def dk_help(self, checks=None):
        if checks is None:
            checks = list()
        checks.append('Usage: dk [OPTIONS] COMMAND [ARGS]...')
        checks.append('config-list (cl)')
        checks.append('user-info (ui)')
        sout = self.run_command('dk --help', checks)
        return sout

    def dk_kitchen_list(self, checks=None):
        if checks is None:
            checks = list()
        checks.append('Getting the list of kitchens')
        checks.append('+---- master')
        sout = self.run_command('dk kl', checks)
        return sout

    def run_command(self, command, checks=None):
        if checks is None:
            checks = list()
        p = Popen(['/bin/sh'], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        sout, serr = p.communicate(command+'\n')
        if serr != '':
            message = 'Command %s failed. Standard error is %s' % (command, serr)
            raise Exception(message)
        for s in checks:
            self.assertIn(s, sout)
        return sout

    def set_working_directory(self, path):
        os.chdir(path)
        cwd = os.getcwd()
        self.assertIn(path, cwd)

if __name__ == '__main__':
    print 'Running CLI smoke tests - Quick Start'
    print 'To configure, set this environment variables, otherwise will use default values:'
    print '\tDK_CLI_SMOKE_TEST_BASE_PATH: Default is /home/vagrant'
    print '\tDK_CLI_SMOKE_TEST_EMAIL: Default is alex@datakitchen.io\n'
    unittest.main()
