#!/usr/bin/env python
from __future__ import print_function
import os
import shutil
import subprocess
import sys
from setuptools import setup


VERSION = "1.0"

TEMP_PATH = "deps"
JARS_TARGET = os.path.join(TEMP_PATH, "jars")

in_secretunicorns_sdk = os.path.isfile("../secretunicorns-spark/build.sbt")


try:  # noqa
    if in_secretunicorns_sdk:
        try:
            os.mkdir(TEMP_PATH)
        except OSError:
            print("Could not create dir {0}".format(TEMP_PATH), file=sys.stderr)
            exit(1)

        p = subprocess.Popen("sbt printClasspath".split(),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             cwd="../secretunicorns-spark/")

        output, errors = p.communicate()

        classpath = []
        for line in output.decode('utf-8').splitlines():
            path = str(line.strip())
            if path.endswith(".jar") and os.path.exists(path):
                classpath.append(path)

        os.mkdir(JARS_TARGET)
        for jar in classpath:
            target_path = os.path.join(JARS_TARGET, os.path.basename(jar))
            if not os.path.exists(target_path):
                shutil.copy(jar, target_path)

        if len(classpath) == 0:
            print("Failed to retrieve the jar classpath. Can't package")
            exit(-1)
    else:
        if not os.path.exists(JARS_TARGET):
            print("You need to be in the secretunicorns-pyspark root folder to package",
                  file=sys.stderr)
            exit(-1)

    setup(
        name="secretunicorns_pyspark",  # TODO: update name
        version=VERSION,
        description="secretunicorns PySpark bindings",  # TODO: update description
        author="Secret Unicorns Union",
        url="https://secretunicorns.org",  # TODO: update url
        download_url="https://github.com/secretunicorns-spark.git",  # TODO: update url
        license="Apache License 2.0",
        zip_safe=False,

        packages=["secretunicorns_pyspark",
                  "secretunicorns_pyspark.jars"],

        package_dir={
            "secretunicorns_pyspark": "src/secretunicorns_pyspark",
            "secretunicorns_pyspark.jars": "deps/jars"
        },
        include_package_data=True,

        package_data={
            "secretunicorns_pyspark.jars": ["*.jar"]
        },

        scripts=["bin/secretunicornspyspark-jars"],

        install_requires=[
            "pyspark",
            "numpy",
        ],

        setup_requires=["pyspark", "pypandoc", "pytest-runner", "numpy"],
        tests_require=["pytest", "pytest-cov", "coverage", "teamcity-messages"]

    )

finally:
    if in_secretunicorns_sdk:
        if os.path.exists(JARS_TARGET):
            shutil.rmtree(JARS_TARGET)

        if os.path.exists(TEMP_PATH):
            os.rmdir(TEMP_PATH)
