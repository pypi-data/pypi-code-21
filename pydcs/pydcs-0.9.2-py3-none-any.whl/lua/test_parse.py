import unittest
from dcs.lua.parse import loads


class TestNumber(unittest.TestCase):

    def test_integer(self):
        r = loads("int = 3")
        self.assertEqual(r, {"int": 3})

        r = loads("int = 193984")
        self.assertEqual(r, {"int": 193984})

        r = loads("int = -23")
        self.assertEqual(r, {"int": -23})

    def test_decimal(self):
        r = loads("dec = 666.6")
        self.assertEqual(r, {"dec": 666.6})

    def test_string(self):
        s = """
mission =
{
    ["trig"] =
    {
        ["actions"] =
        {
            [1] = "a_(get(\\"ResKey_Action_62\\")); mission.trig.func[1]=nil;",
            [2] = "a_do_script_file(getValueResourceByKey(\\"ResKey_Action_64\\")); mission.trig.func[2]=nil;",
            [3] = "a_out_text_delay(getValueDictByKey(\\"DictKey_ActionText_66\\"), 10, false);a_do_script(getValueDictByKey(\\"DictKey_ActionText_255\\")); mission.trig.func[3]=nil;",
            [4] = "a_add_radio_item(getValueDictByKey(\\"Destroy Red Ground Group\\"), 1500, 1); mission.trig.func[4]=nil;",
            [5] = "a_do_script(getValueDictByKey(\\"DictKey_ActionText_213\\"));a_clear_flag(1500);",
        }, -- end of ["actions"]
    }
}
"""
        r = loads(s)

        r = loads('x = "a_do_script_file(getValueResourceByKey(\\"ResKey_Action_62\\")); mission.trig.func[1]=nil;"')
        self.assertEqual(r, {"x": "a_do_script_file(getValueResourceByKey(\"ResKey_Action_62\")); mission.trig.func[1]=nil;"})

    def test_object(self):
        luas = """
mission=
{
    ["trig"]=
    {
    },

    ["coalitions"]=
    {
        ["blue"]=
        {
            [1]=11,
            [2]=4,
            [3]=6
        }
    }, -- end of ["coalitions"]
    ["maxDictId"]=18,
    ["descriptionBlueTask"]="DictKey_descriptionBlueTask_3"
}
"""
        ref = {'mission': {
            'coalitions': {'blue': {1: 11.0, 2: 4.0, 3: 6.0}},
            'descriptionBlueTask': 'DictKey_descriptionBlueTask_3',
            'trig': {},
            'maxDictId': 18.0}}
        r = loads(luas)
        self.assertEqual(r, ref)

    def test_dictmix(self):
        luas = """
o =
{
    ["callsign"] =
    {
        [1] = 1,
        [2] = 1,
        [3] = 1,
        ["name"] = "Enfield11",
    } -- end of ["callsign"]
}
"""
        ref = {"o": {
            'callsign': {
                1: 1,
                2: 1,
                3: 1,
                "name": "Enfield11"
            }
        }}
        r = loads(luas)
        self.assertEqual(r, ref)

    def test_syntaxerr(self):
        with self.assertRaises(SyntaxError):
            loads("""m=
            {
                ["x"] 12
            }""")


if __name__ == '__main__':
    unittest.main()
