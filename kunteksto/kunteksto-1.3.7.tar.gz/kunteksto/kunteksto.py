"""
Main entry point for the Kunteksto application.
"""
import sys
import os
from subprocess import run
import click
import configparser
import sqlite3

from .analyze  import analyze
from .generate  import make_model, make_data
from .catalogmgr import  get_catalog
from .modeledit import edit_model
from .recordedit import edit_record

@click.command()
@click.option('--mode', '-m', type=click.Choice(['all', 'editdb', 'generate']), help="See the documentation. If you don't know then use: all", prompt="Enter a valid mode")
@click.option('--infile', '-i', help='Full path and filename of the input CSV file.', prompt="Enter a valid CSV file")
@click.option('--dbfile', '-db', help='Full path and filename of the existing model database file.', prompt=False)
@click.option('--outdir', '-o', help='Full path to the output directory for writing the database and other files. Overrides the config file default value.')
@click.option('--delim', '-d', type=click.Choice([',', ';', ':', '|', '$']), help=' Overrides the config file default value.')
@click.option('--analyzelevel', '-a', type=click.Choice(['simple', 'full']), help=' Overrides the config file default value.')
def main(mode, infile, outdir, delim, analyzelevel, dbfile):
    """Kunteksto (ˈkänˌteksto) adds validation and semantics to your data."""

    # Setup config info based on the current working directory
    config = configparser.ConfigParser()
    config.read('kunteksto.conf')
            
    # override the delimiter and/or analyzelevel if provided
    if not delim:
        delim = config['KUNTEKSTO']['delim']
    if not analyzelevel:
        analyzelevel = config['KUNTEKSTO']['analyzelevel']
    
    if outdir is None:
        if config['KUNTEKSTO']['outdir'].lower() in ['output', 'none']:
            config['KUNTEKSTO']['outdir'] = 'output'
            outdir = os.getcwd() + os.path.sep + config['KUNTEKSTO']['outdir']
        else:
            print("You must supply a writable output directory.")
            exit(code=1)

    if not infile:
        print("You must supply a readable CSV input file.")
        exit(code=1)

    if not mode:
        click.echo("You must supply a mode.")
        exit(code=1)
        
    elif mode == 'all':
        dname, fname = os.path.split(infile)
        outdir += os.path.sep + fname[:fname.index('.')] 
        prjname = fname[:fname.index('.')]
        get_catalog(outdir, prjname)
        if not dbfile:
            outDB = analyze(infile, delim, analyzelevel, outdir)
            edit_model(outDB)
            edit_record(outDB)
            modelName = make_model(outDB, outdir)
            datagen(modelName, outDB, infile, delim, outdir, config)
        else:
            outDB = dbfile
            modelName = make_model(outDB, outdir)
            datagen(modelName, outDB, infile, delim, outdir, config)
            
        
            
    elif mode == 'generate':
        if not dbfile:
            click.echo("You must supply a full path and name of an existing model database.")
            exit(code=1)
            
        dname, fname = os.path.split(dbfile)
        prjname = fname[:fname.index('.')]
        dbName =  prjname + '.db'
        get_catalog(outdir, prjname)        
        conn = sqlite3.connect(dbfile)
        c = conn.cursor()
        c.execute("SELECT * FROM model")
        row = c.fetchone()
        dmID = row[5].strip()
        outdir = outdir + os.path.sep + prjname        
        modelName = outdir + '/dm-' + dmID + '.xsd'
        datagen(modelName, dbfile, infile, delim, outdir, config)
        
    elif mode == 'editdb':
        dname, fname = os.path.split(infile)
        dbName = fname[:fname.index('.')] + '.db'
        db_file = outdir + os.path.sep + dbName
        edit_model(db_file)
        edit_record(db_file)
                
    return(True)

def datagen(modelName, outDB, infile, delim, outdir, config):
    """
    Generate XML, JSON and RDF data from the CSV. 
    """
    
    # open a connection to the RDF store if one is defined and RDF is to be generated.  
    if config['KUNTEKSTO']['rdf']:
        if config['ALLEGROGRAPH']['status'].upper() == "ACTIVE":
            try:
                from franz.openrdf.connect import ag_connect
                connRDF = ag_connect(config['ALLEGROGRAPH']['repo'], host=config['ALLEGROGRAPH']['host'], port=config['ALLEGROGRAPH']['port'],  user=config['ALLEGROGRAPH']['user'], password=config['ALLEGROGRAPH']['pw'])
            except:
                connRDF = None
                print('RDF Connection Error', 'Could not create connection to Allegrograph.')
        else:
            connRDF = None

    # open a connection to the XML DB if one is defined and XML is to be generated.
    if config['KUNTEKSTO']['xml']:
        if config['BASEX']['status'].upper() == "ACTIVE":
            try:
                import BaseXClient
                connXML = BaseXClient.Session(config['BASEX']['host'], int(config['BASEX']['port']), config['BASEX']['user'], config['BASEX']['pw'])
                connXML.execute("create db " + config['BASEX']['dbname'])
            except:
                connXML = None
                print('XML Connection Error', 'Could not create connection to BaseX.')
        else:
            connXML = None

    # open a connection to the JSON DB if one is defined and JSON is to be generated.      
    if config['KUNTEKSTO']['json']:
        if config['MONGODB']['status'].upper() == "ACTIVE":
            try:
                from pymongo import MongoClient
                # default MongoDB has no authentication requirements.
                client = MongoClient(config['MONGODB']['host'], int(config['MONGODB']['port']))
                connJSON = client[config['MONGODB']['dbname']]
            except:
                connJSON = None
                print('JSON Connection Error', 'Could not create connection to MongoDB.')
        else:
            connJSON = None

    # generate the data
    if modelName:
        make_data(modelName, outDB, infile,  delim, outdir, connRDF, connXML, connJSON)

        if connRDF:
            connRDF.close()
        if connXML:
            connXML.close()
        print('\n\nData Generation: ', 'Completed.')

    else:
        print('\n\nProcedure Error: ', 'Missing model DB or no selected output directory.')

    return(True)


if __name__ == '__main__':
    print('\n Kunteksto started ...\n\n')
    main()
