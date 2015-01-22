/* Javascript for submitcompareXBlock. */
function SubmitAndCompareXBlockInitView(runtime, element) {
    
    var handlerUrl = runtime.handlerUrl(element, 'student_submit');
    //alert("handlerUrl is " + handlerUrl);

	function post_submit(result) {
	}
	
    function show_answer() {
       var your_answer = document.getElementById('your_answer');
       your_answer.style.display = 'block';

       var expert_answer = document.getElementById('expert_answer');
       expert_answer.style.display = 'block';
          
       var submit_button = document.getElementById('submit_button');
       submit_button.value = 'Resubmit';

    }

    function hide_answer() {
       var your_answer = document.getElementById('your_answer');
       your_answer.style.display = 'none';

       var expert_answer = document.getElementById('expert_answer');
       expert_answer.style.display = 'none';
          
       var submit_button = document.getElementById('submit_button');
       submit_button.value = 'Submit and Compare';

    }

    $('.submit', element).click(function(eventObject) {

        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({"answer": $(".answer",element).val() }),
            success: post_submit
        });
        show_answer();
	});

    $('.reset', element).click(function(eventObject) {

		$(".answer",element).val("");
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({"answer": "" }),
            success: post_submit
        });
        hide_answer();
	});
	
	if ($(".answer",element).val() != "") {
		show_answer();
	}
	
}


