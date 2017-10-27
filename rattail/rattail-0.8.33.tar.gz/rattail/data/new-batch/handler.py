# -*- coding: utf-8; -*-
# -*- coding: utf-8; -*-
"""
Handler for ${model_title} batches
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model
from rattail.batch import BatchHandler


class ${model_name}Handler(BatchHandler):
    """
    Handler for ${model_title} batches.
    """
    batch_model_class = model.${model_name}

    def refresh_data(self, session, batch, progress=None):
        """
        Refresh all data for the batch.
        """
        super(${model_name}Handler, self).refresh_data(session, batch, progress=progress)

    def cognize_row(self, session, row):
        """
        Inspect a single row from the batch, and set its attributes based on
        various lookups and business rules, as needed.
        """

    def execute(self, batch, **kwargs):
        """
        Execute the batch, whatever that means in your context.
        """
        return True
