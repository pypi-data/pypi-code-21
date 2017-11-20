'''
views.py: part of expfactory package

Copyright (c) 2017, Vanessa Sochat
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

from flask import (
    flash,
    render_template, 
    request, 
    redirect,
    session
)

from expfactory.logger import bot
from werkzeug import secure_filename
from expfactory.utils import (
    convert2boolean, 
    getenv,
    get_post_fields
)

from expfactory.server import app
from random import choice
import os


# INTERACTIVE BATTERY GENERATION ####################################################
# Step 0: User is presented with base interface
@app.route('/battery')
def battery():
    return render_template('battery.html')

# STEP 1: Validation of user input for battery
@app.route('/battery/validate',methods=['POST'])
def validate():
    logo = None
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.iteritems():
            if field == "dbsetupchoice":
                dbsetupchoice = value
            else:
                fields[field] = value

        # DATABASE SETUP ###################################################
        # If the user wants to generate a custom database:
        if dbsetupchoice == "manual":

            # Generate a database url from the inputs
            fields["database_url"] =  generate_database_url(dbtype=fields["dbtype"],
                                                 username=fields["dbusername"],
                                                 password=fields["dbpassword"],
                                                 host=fields["dbhost"],
                                                 table=fields["dbtable"]) 
        else:
            # If generating a folder, use sqlite3
            if fields["deploychoice"] == "folder":
                fields["database_url"] = generate_database_url(template="sqlite3")       
            # Otherwise, use postgres
            else: 
                fields["database_url"] = generate_database_url(template="mysql")       
        
        # LOCAL FOLDER #####################################################
        if fields["deploychoice"] == "folder":

            # Copy the custom logo
            if "file" in request.files and allowed_file(request.files["file"]):
                logo = secure_filename(request.files["file"])
                add_custom_logo(battery_repo="%s/battery" %(app.tmpdir),logo=logo)
    
            # Generate battery folder with config file with parameters
            generate_config("%s/battery" %(app.tmpdir),fields)

        else: 
            prepare_vm(battery_dest=app.tmpdir,fields=fields,vm_type=fields["deploychoice"])

        # Get valid experiments to present to user
        valid_experiments = [{"exp_id":e[0]["exp_id"],"name":e[0]["name"]} for e in app.experiments]

        return render_template('experiments.html',
                                experiments=str(valid_experiments),
                                this_many=len(valid_experiments),
                                deploychoice=fields["deploychoice"])

    return render_template('battery.html')

# STEP 2: User must select experiments
@app.route('/battery/select',methods=['POST'])
def select():
    if request.method == 'POST':
        fields = dict()
        for field,value in request.form.iteritems():
            if field == "deploychoice":
                deploychoice = value
            else:
                fields[field] = value

        # Retrieve experiment folders 
        valid_experiments = app.experiments
        experiments =  [x[0]["exp_id"] for x in valid_experiments]
        selected_experiments = [x for x in fields.values() if x in experiments]
        experiment_folders = ["%s/experiments/%s" %(app.tmpdir,x) for x in selected_experiments]

        # Option 1: A folder on the local machine
        if deploychoice == "folder":

            # Add to the battery
            generate(battery_dest="%s/expfactory-battery"%app.tmpdir,
                     battery_repo="%s/battery"%app.tmpdir,
                     experiment_repo="%s/experiments"%app.tmpdir,
                     experiments=experiment_folders,
                     make_config=False,
                     warning=False)

            battery_dest = "%s/expfactory-battery" %(app.tmpdir)

        # Option 2 or 3: Virtual machine (vagrant) or cloud (aws)
        else:
            specify_experiments(battery_dest=app.tmpdir,experiments=selected_experiments)
            battery_dest = app.tmpdir 

        return render_template('complete.html',battery_dest=battery_dest)
