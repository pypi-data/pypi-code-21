import numpy
import unittest

import pytest

import ws_sheets
import ws_sheets.exception

@pytest.mark.asyncio
async def test_SetScriptPreTest(settings):
 
    b = ws_sheets.Book(settings)

    b.set_script_pre('import os')
    b.do_all()
    
    print('output')
    print(b.script_pre.output)

    assert isinstance(
            b.script_pre.exec_exc,
            ws_sheets.exception.NotAllowedError)

    b.set_script_pre("a = 1\n")

    b.set_cell('0', 0, 0, "a")
    
    assert b['0'][0, 0] == 1

