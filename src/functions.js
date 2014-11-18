/*
 functions.js
 Javascript functions for PyBBIO BBIOServer library.
*/
var pitchspot="1";
function call_function(function_id, type) {
  /* Interfaces with the BBIOServer request handler to execute
     PyBBIO functions. */
  var params = { "function_id" : function_id };
  if (type == "entry") {
      // Extract the text and add it to the params hash table:
    var text = $('#' + function_id).val()
    if (!text) {
      text += " ";
    }
    params["entry_text"] = text;
  }

  if (type == "bowl") {

	params["bowl"] = 1;
	params["spin"] = $("#spin").val();
	params["speed"] = $("#speed").val();
	params["pitchspot"] = pitchspot;
	showBowlButton();
  	console.log(params)
	console.log('Poling for bat');
  }

  $.get("/cgi-bin/index", params,
  function(return_value){
    if (type == "monitor") {
	// Set the monitor div with the same id as the function 
        // to the return value:
      $('#'+function_id).text(return_value);
    }

    else if (type == "bowl") {
	
	//showBowlButton();
	console.log(return_value);

	switch (return_value) {

	case '1':
		$("#ball").css('left',620);
		$("#ball").css('top',300);
		break;

	 case '2':
                $("#ball").css('left',620);
                $("#ball").css('top',330);
                break;

	 case '3':
                $("#ball").css('left',620);
                $("#ball").css('top',360);
                break;

	 case '4':
		$("#ball").css('left',620);
                $("#ball").css('top',400);
                break;

	 case '5':
                $("#ball").css('left',640);
                $("#ball").css('top',400);
                break;

	 case '6':
                $("#ball").css('left',640);
                $("#ball").css('top',360);
                break;

	 case '7':
                $("#ball").css('left',640);
                $("#ball").css('top',330);
                break;

	 case '8':
                $("#ball").css('left',620);
                $("#ball").css('top',300);
                break;




	}
	//showBowlButton();
    }
  });
};


function start_monitor() {
  /* Called once on page load. Continuously updates monitors. */
  $('.monitor-field').each(function() {
    // The div id is the same as its function's id:
    var function_id = $(this).attr('id');
    call_function(function_id, 'monitor');
  });
  setTimeout(function() { 
    start_monitor();
  }, 200);
} 


function hideElement(id) {
        // Hides the element with the given id
        // TODO: Add error reporting in case no element with given ID is found

        $("#"+id).fadeOut();
}
