'''
Tests for the Submit-and-Compare XBlock
'''

import json
import sys

from openedx.tests.xblock_integration.xblock_testcase import XBlockTestCase


# pylint: disable=abstract-method
class TestSubmitAndCompare(XBlockTestCase):
    """
    Basic tests for the Submit and Compare XBlocks. We set up a page
    with the block, make sure the page renders, submit an answer, make
    sure we stored it, pull a few hints, and call it quits.
    """

    olx_scenarios = {  # Currently not used
    }

    # This is a stop-gap until we can load OLX and/or OLX from
    # normal workbench scenarios
    test_configuration = [
        {
            "urlname": "submit_and_compare_test_case",
            "xblocks": [  # Stopgap until we handle OLX
                {
                    'blocktype': 'submit-and-compare',
                    'urlname': 'submit_0'
                }
            ]
        }
    ]

    def student_submit(self, block, answer):
        """
        Make an AJAX call to the XBlock, and assert the state is as
        desired.
        """
        resp = self.ajax('student_submit', block, {'answer': answer})
        self.assertEqual(resp.status_code, 200)
        # pylint: disable=no-member
        self.assertEqual(resp.data, {'success': True,
                                     'answer': answer})

    # pylint: disable=unused-argument
    def check_response(self, block_urlname, expected_string, present):
        """
        Confirm that we have a 200 response code (no server error)

        Confirm that a string is either present or not present in the
        response
        """
        response = self.render_block(block_urlname)
        self.assertEqual(response.status_code, 200)

        if present:
            self.assertTrue(expected_string in response.content)
        else:
            self.assertFalse(expected_string in response.content)


    def test_submit_compare(self):
        """
        We submit something, pull a few hints, and submit again.
        """
        self.select_student(0)
        # We confirm we don't have errors rendering the student view
        self.check_response('submit_0', "Before you begin the simulation", True)
        self.check_response('submit_0', "because. Yeah", False)
        self.student_submit('submit_0',
                            "I think because. Yeah. Because")
        self.check_response('submit_0', "because. Yeah", True)
        self.student_submit('submit_0',
                            "No. Another reason")
        self.check_response('submit_0', "because. Yeah", False)
        self.check_response('submit_0', "Another reason", True)
