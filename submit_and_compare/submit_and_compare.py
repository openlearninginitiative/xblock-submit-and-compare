"""  Submit and Compare XBlock main Python class"""

import pkg_resources
from django.template import Context, Template

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment

from lxml import etree
from xml.etree import ElementTree as ET

from StringIO import StringIO

class SubmitAndCompareXBlock(XBlock):

    '''
    Icon of the XBlock. Values : [other (default), video, problem]
    '''
    icon_class = "problem"

    '''
    Fields
    '''
    display_name = String(display_name="Display Name",
        default="Submit and Compare",
        scope=Scope.settings,
        help="This name appears in the horizontal navigation at the top of the page")

    student_answer = String(
        default="", 
        scope=Scope.user_state,
        help="This is the student's answer to the question",
    )

    question_xml = etree.Element('question')
    body = etree.SubElement(question_xml, 'body')
    our_answer = etree.SubElement(body, 'p')
    our_answer.text = 'Before you begin the simulation, think for a minute about your hypothesis.  What do you expect the outcome of the simulation will be?  What data do you need to gather in order to prove or disprove your hypothesis?'
    explanation = etree.SubElement(question_xml, 'explanation')
    expert_answer = etree.SubElement(explanation, 'p')
    expert_answer.text = 'We would expect the simulation to show that there is no difference between the two scenarios.  Relevant data to gather would include time and temperature.'

    question_string =  String(help="Default question content ", 
        default=etree.tostring(question_xml, encoding="unicode", pretty_print=True), 
        scope=Scope.content
    )

    '''
    Main functions
    '''
    def student_view(self, context=None):
        """
        The primary view of the XBlock, shown to students
        when viewing courses.
        """
        prompt = self._get_body(self.question_string)
        explanation = self._get_explanation(self.question_string)

        attributes = ""
        html = self.resource_string("static/html/submit_and_compare_view.html")
        frag = Fragment(html.format(prompt = prompt, 
                                    student_answer = self.student_answer, 
                                    explanation = explanation, 
                                    attributes = attributes
                                    ))
        frag.add_css(self.resource_string("static/css/submit_and_compare.css"))
        frag.add_javascript(self.resource_string("static/js/submit_and_compare_view.js"))
        frag.initialize_js('SubmitAndCompareXBlockInitView')
        return frag

    def studio_view(self, context=None):
        """
        The secondary view of the XBlock, shown to teachers
        when editing the XBlock.
        """
        context = {
            'display_name': self.display_name,
            'xml_data': self.question_string,
        }
        html = self.render_template('static/html/submit_and_compare_edit.html', context)
        
        frag = Fragment(html)
        frag.add_javascript(self.load_resource('static/js/submit_and_compare_edit.js'))
        frag.initialize_js('SubmitAndCompareXBlockInitEdit')
        return frag

    @XBlock.json_handler
    def student_submit(self, submissions, suffix=''):
        """
        Save student answer
        """
        self.student_answer = submissions['answer']
        return {"success":True}
        

    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):
        """
        Save studio edits
        """
        self.display_name = submissions['display_name']
        self.question_string = submissions['data']

        return {
            'result': 'success',
        }

    '''
    Util functions
    '''
    def load_resource(self, resource_path):
        """
        Gets the content of a resource
        """
        resource_content = pkg_resources.resource_string(__name__, resource_path)
        return unicode(resource_content)

    def render_template(self, template_path, context={}):
        """
        Evaluate a template by resource path, applying the provided context
        """
        template_str = self.load_resource(template_path)
        return Template(template_str).render(Context(context))

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def _get_body(self, xmlstring):
        """
        Helper method
        """
        etree.parse(StringIO(xmlstring))
        xmltree = etree.fromstring(xmlstring)
        body = xmltree[0]
        
        return etree.tostring(body, encoding="unicode")

    def _get_explanation(self, xmlstring):
        """
        Helper method
        """
        etree.parse(StringIO(xmlstring))
        xmltree = etree.fromstring(xmlstring)
        explanation = xmltree[1]
        
        return etree.tostring(explanation, encoding="unicode")
