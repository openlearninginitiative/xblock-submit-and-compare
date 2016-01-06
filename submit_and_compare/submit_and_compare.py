'''  Submit and Compare XBlock main Python class'''

import pkg_resources
from django.template import Context, Template

from xblock.core import XBlock
from xblock.fields import Scope, String, List
from xblock.fragment import Fragment

from lxml import etree
from xml.etree import ElementTree as ET

from StringIO import StringIO

import textwrap

class SubmitAndCompareXBlock(XBlock):

    '''
    Icon of the XBlock. Values : [other (default), video, problem]
    '''
    icon_class = 'problem'

    '''
    Fields
    '''
    display_name = String(display_name='Display Name',
        default='Submit and Compare',
        scope=Scope.settings,
        help='This name appears in the horizontal navigation at the top of the page')

    student_answer = String(
        default='', 
        scope=Scope.user_state,
        help='This is the student\'s answer to the question',
    )
    
    your_answer_label = String(
        default='Your Answer:', 
        scope=Scope.settings,
        help='Label for the text area containing the student\'s answer',
    )

    our_answer_label = String(
        default='Our Answer:', 
        scope=Scope.settings,
        help='Label for the \'expert\' answer',
    )
    
    submit_button_label = String(
        default='Submit and Compare', 
        scope=Scope.settings,
        help='Label for the submit button',
    )
    
    hints = List(
        default=[],
        scope=Scope.content,
        help='Hints for the question',
    )
    
    question_string =  String(help='Default question content ', 
        scope=Scope.content,
        #default=etree.tostring(question_xml, encoding='unicode', pretty_print=True), 
        default=textwrap.dedent('''
            <submit_and_compare schema_version='1'>
                <body>
                    <p>Before you begin the simulation, think for a minute about your hypothesis.  What do you expect the outcome of the simulation will be?  What data do you need to gather in order to prove or disprove your hypothesis?</p>
                </body>
                <explanation>
                    <p>We would expect the simulation to show that there is no difference between the two scenarios.  Relevant data to gather would include time and temperature.</p>
                </explanation>
                <demandhint>
                    <hint>A hypothesis is a proposed explanation for a phenomenon.  In this case, the hypothesis is what we think the simulation will show.</hint>
                    <hint>Once you've decided on your hypothesis, which data would help you determine if that hypothesis is correct or incorrect?</hint>
                </demandhint>
            </submit_and_compare>
        '''
        ))


    '''
    Main functions
    '''
    def student_view(self, context=None):
        '''
        The primary view of the XBlock, shown to students
        when viewing courses.
        '''
        prompt = self._get_body(self.question_string)
        explanation = self._get_explanation(self.question_string)
        
        attributes = ''
        html = self.resource_string('static/html/submit_and_compare_view.html')
        frag = Fragment(html.format(display_name = self.display_name,
        							prompt = prompt, 
                                    student_answer = self.student_answer, 
                                    explanation = explanation, 
                                    your_answer_label = self.your_answer_label,
                                    our_answer_label = self.our_answer_label,
                                    submit_button_label = self.submit_button_label,
                                    attributes = attributes
                                    ))
        frag.add_css(self.resource_string('static/css/submit_and_compare.css'))
        frag.add_javascript(self.resource_string('static/js/submit_and_compare_view.js'))
        frag.initialize_js('SubmitAndCompareXBlockInitView')
        return frag

    def studio_view(self, context=None):
        '''
        The secondary view of the XBlock, shown to teachers
        when editing the XBlock.
        '''
        context = {
            'display_name': self.display_name,
            'xml_data': self.question_string,
            'your_answer_label': self.your_answer_label,
            'our_answer_label': self.our_answer_label,
            'submit_button_label': self.submit_button_label,
        }
        html = self.render_template('static/html/submit_and_compare_edit.html', context)
        
        frag = Fragment(html)
        frag.add_javascript(self.load_resource('static/js/submit_and_compare_edit.js'))
        frag.initialize_js('SubmitAndCompareXBlockInitEdit')
        return frag

    @XBlock.json_handler
    def student_submit(self, submissions, suffix=''):
        '''
        Save student answer
        '''
        self.student_answer = submissions['answer']
        return {'success':True}

    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):
        '''
        Save studio edits
        '''
        self.display_name = submissions['display_name']
        self.your_answer_label = submissions['your_answer_label']
        self.our_answer_label = submissions['our_answer_label']
        self.submit_button_label = submissions['submit_button_label']
        xml_content = submissions['data']

        try:
            etree.parse(StringIO(xml_content))
            self.question_string = xml_content
        except etree.XMLSyntaxError as e:
            return {
                'result': 'error',
                'message': e.message
            }

        return {
            'result': 'success',
        }

    @XBlock.json_handler
    def send_hints(self, submissions, suffix=''):
        
		tree = etree.parse(StringIO(self.question_string))
		raw_hints = tree.xpath('/submit_and_compare/demandhint/hint')
		
		decorated_hints = list()
		
		if len(raw_hints) == 1:
			hint = 'Hint: ' + etree.tostring(raw_hints[0], encoding='unicode')
			decorated_hints.append(hint)
		else:
			for i in range(len(raw_hints)):
				hint = 'Hint (' + str(i+1) + ' of ' + str(len(raw_hints)) + '): ' + etree.tostring(raw_hints[i], encoding='unicode')
				decorated_hints.append(hint)
		
		hints = decorated_hints	

		return {
			'result': 'success',
			'hints': hints,
		}

    @XBlock.json_handler
    def publish_event(self, data, suffix=''):
        try:
            event_type = data.pop('event_type')
        except KeyError:
            return {'result': 'error', 'message': 'Missing event_type in JSON data'}

        data['user_id'] = self.scope_ids.user_id
        data['component_id'] = self._get_unique_id()
        self.runtime.publish(self, event_type, data)

        return {'result': 'success'}

    '''
    Util functions
    '''
    def load_resource(self, resource_path):
        '''
        Gets the content of a resource
        '''
        resource_content = pkg_resources.resource_string(__name__, resource_path)
        return unicode(resource_content)

    def render_template(self, template_path, context={}):
        '''
        Evaluate a template by resource path, applying the provided context
        '''
        template_str = self.load_resource(template_path)
        return Template(template_str).render(Context(context))

    def resource_string(self, path):
        '''Handy helper for getting resources from our kit.'''
        data = pkg_resources.resource_string(__name__, path)
        return data.decode('utf8')

    def _get_body(self, xmlstring):
        '''
        Helper method
        '''
        tree = etree.parse(StringIO(xmlstring))
        body = tree.xpath('/submit_and_compare/body')
        
        return etree.tostring(body[0], encoding='unicode')

    def _get_explanation(self, xmlstring):
        '''
        Helper method
        '''
        tree = etree.parse(StringIO(xmlstring))
        explanation = tree.xpath('/submit_and_compare/explanation')
        
        return etree.tostring(explanation[0], encoding='unicode')

    def _get_unique_id(self):
        try:
            unique_id = self.location.name
        except AttributeError:
            # workaround for xblock workbench
            unique_id = 'workbench-workaround-id'
        return unique_id
