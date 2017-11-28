# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.help_files import helps

# pylint: disable=line-too-long

helps['ml'] = """
            type: group
            short-summary: Module to access Machine Learning commands
            """

helps["ml env"] = """
                type: group
                short-summary: Manage compute environments."""

helps["ml service"] = """
                    type: group
                    short-summary: Manage operationalized services."""

helps["ml account"] = """
                     type: group
                     short-summary: Manage operationalization accounts."""

helps["ml account experimentation"] = """
                     type: group
                     short-summary: Manage experimentation accounts."""

helps["ml account modelmanagement"] = """
                     type: group
                     short-summary: Manage model management accounts"""

helps["ml image"] = """
                  type: group
                  short-summary: Manage operationalization images"""

helps["ml manifest"] = """
                     type: group
                     short-summary: Manage operationalization manifests"""

helps["ml model"] = """
                  type: group
                  short-summary: Manage operationalization models"""

helps["ml manifest create"] = """
                            short-summary: Create an Operationalization Manifest. This command has two different \
                            sets of required arguments, depending on if you want to use previously registered model/s."""

helps["ml image create"] = """
                         short-summary: Create an Operationalization Image. This command has two different sets of \
                         required arguments, depending on if you want to use a previously created manifest."""

helps["ml service create realtime"] = """
                                    short-summary: Create an Operationalization Service. This command has two \
                                    different sets of required arguments, depending on if you want to use a previously \
                                    created image."""
