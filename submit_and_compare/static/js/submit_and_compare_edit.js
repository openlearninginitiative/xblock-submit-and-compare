/* Javascript for Submit and Compare XBlock. */
function SubmitAndCompareXBlockInitEdit(runtime, element) {

    var xmlEditorTextarea = $('.block-xml-editor', element),
        xmlEditor = CodeMirror.fromTextArea(xmlEditorTextarea[0], { mode: 'xml', lineWrapping: true });

    $(element).find('.action-cancel').bind('click', function() {
        runtime.notify('cancel', {});
    });

    $(element).find('.action-save').bind('click', function() {
        var data = {
            'display_name': $('#submit_and_compare_edit_display_name').val(),
            'your_answer_label': $('#submit_and_compare_edit_your_answer_label').val(),
            'our_answer_label': $('#submit_and_compare_edit_our_answer_label').val(),
            'data': xmlEditor.getValue(),
        };
        
        runtime.notify('save', {state: 'start'});
        
        var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
            if (response.result === 'success') {
                runtime.notify('save', {state: 'end'});
                //Reload the page
                //window.location.reload(false);
            } else {
                runtime.notify('error', {msg: response.message})
            }
        });
    });
}

