from unittest import TestCase
from unittest import skip

from bs4 import BeautifulSoup
from bs4.testing import SoupTest

from trunity_migrator.fixers import *


class FixersTestCase(SoupTest):

    def test_fix_img_src(self):
        html = '''
        <h1>Hi dude!</h1>
        <p>
            <img alt="" src="/path/to/files/image1.jpg" style="width: 318px; height: 217px;" />
        </p>
        '''

        base_url = 'http://www.trunity.net'

        expected_html = '''
        <h1>Hi dude!</h1>
        <p>
            <img alt="" src="http://www.trunity.net/path/to/files/image1.jpg" style="width: 318px; height: 217px;" />
        </p>
        '''

        result_html = fix_img_src(html, base_url)

        # we use BeautifulSoup to compare html:
        self.assertEqual(
            BeautifulSoup(result_html, "html.parser"),
            BeautifulSoup(expected_html, "html.parser"),
            'html and expected_html are not equal!'
        )

    def test_fix_table_width(self):
        html = '''
        <h2>Change width from 766 to 100%</h2>
        <table border="0" cellpadding="0" cellspacing="0" height="36" style="background-color: rgb(191, 242, 255);" width="766">
            <tbody>
                <tr>
                    <td style="width: 712px;"><strong>The structure of DNA</strong></td>
                    <td style="width: 20px;">&nbsp;</td>
                </tr>
            </tbody>
        </table>
        
        <h2>Change width from 770 to 70%</h2>
        <table border="0" cellpadding="0" cellspacing="0" height="36" style="background-color: rgb(191, 242, 255);" width="770">
            <tbody>
                <tr>
                    <td style="width: 712px;"><strong>The structure of DNA</strong></td>
                    <td style="width: 20px;">&nbsp;</td>
                </tr>
            </tbody>
        </table>
        '''

        expected_html = '''
        <h2>Change width from 766 to 100%</h2>
        <table border="0" cellpadding="0" cellspacing="0" height="36" style="background-color: rgb(191, 242, 255);" width="100%">
            <tbody>
                <tr>
                    <td style="width: 712px;"><strong>The structure of DNA</strong></td>
                    <td style="width: 20px;">&nbsp;</td>
                </tr>
            </tbody>
        </table>

        <h2>Change width from 770 to 70%</h2>
        <table border="0" cellpadding="0" cellspacing="0" height="36" style="background-color: rgb(191, 242, 255);" width="70%">
            <tbody>
                <tr>
                    <td style="width: 712px;"><strong>The structure of DNA</strong></td>
                    <td style="width: 20px;">&nbsp;</td>
                </tr>
            </tbody>
        </table>
        '''

        result_html = fix_table_width(
            html,
            old_widths=["766", "770"],
            new_widths=["100%", "70%"]
        )

        self.assertEqual(
            BeautifulSoup(expected_html, "html.parser"),
            BeautifulSoup(result_html, "html.parser"),
            "Result html is not equal to expected!"
        )

    @skip('Skipped due to not proper formatting style block')
    def test_fix_science_fusion_style(self):
        html = '''
        <style type="text/css">
            iframe {
                -moz-transform: scale(1.00, 1.00);      
                -webkit-transform: scale(1.00, 1.00);      
                -o-transform: scale(1.00, 1.00);     
                -ms-transform: scale(1.00, 1.00);     
                transform: scale(1.00, 1.00);      
                -moz-transform-origin: top left;     
                -webkit-transform-origin: top left;     
                -o-transform-origin: top left;     
                -ms-transform-origin: top left;     
                transform-origin: top left;     
                border: solid #ccc 10px;
            }
        </style>
        <p>
            <iframe align="top" frameborder="0" height="674px" name="iframe_name" 
            offline-link="http://hmh.trunity.net/science_fusion/sdlo/G3_EC_00222.zip" 
            scrolling="no" src="http://www.trunity.net/hmh/science_fusion/sdlo/dlo/v1/G3_EC_00222/" 
            style="border:0px black solid;" width="811px">
            </iframe>
        </p>
        '''

        expected_html = '''
        <style type="text/css">
            iframe {
                max-width:100%!important; 
                -moz-transform-origin: top center; 
                -webkit-transform-origin: top center; 
                -o-transform-origin: top center; 
                -ms-transform-origin: top center; 
                transform-origin: top center;
            }
        </style>
        <p>
            <iframe align="top" allowfullscreen="" frameborder="0" height="674px" name="iframe_name" 
            offline-link="http://hmh.trunity.net/science_fusion/sdlo/G3_EC_00222.zip" 
            scrolling="no" src="http://www.trunity.net/hmh/science_fusion/sdlo/dlo/v1/G3_EC_00222/" 
            style="border:0px black solid;" width="100%">
            </iframe>
        </p>
        '''

        result_html = fix_science_fusion_style(html)
        print("Result: ", result_html)

        self.maxDiff = None

        self.assertSoupEquals(html, expected_html)

        # TODO: try use this: from bs4.testing import SoupTest
        # self.assertSoupEquals