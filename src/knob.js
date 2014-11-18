//Initialize both knobs
$("#spin").knob({
    
    'min':-50,
    'max':50,
    'angleOffset':-125,
    'angleArc':250,
    'lineCap':'round',
    'cursor':true,
    'step':10
    
    
});

$("#speed").knob({
	'min':70,
	'max':120,
	'angleOffset':-125,
	'angleArc':250,
	'fgColor':'#66CC66',
	'inputColor':'#66CC66',
	'lineCap':'round',
	//'cursor':true,
	'step':5
});

// Initialize spin with a zero value (Straight Ball)
$("#spin").val(0).trigger('change');

$("#bowl").click(function() {
    
    //$(this).removeClass("btn-primary");
    //$(this).addClass("btn-danger");
    //$(this).addClass("disabled");
    //$(this).html('Bowling Now ..');
    //$("#preloader").fadeIn();
    //$("#status").delay(150).fadeIn();
    //$("#status1").delay(150).fadeIn()
    
    
});

function showBowlButton() {
    //code
    
    //$("#status").fadeOut();
    //$("#status1").fadeOut();
    //$("#preloader").delay(150).fadeOut();
    $("#myModal").modal('toggle');
    //$("#bowl").removeClass("disabled");
    //$("#bowl").removeClass("btn-danger");
    //$("#bowl").addClass("btn-primary");
    //$("#bowl").html("Bowl");
}

$("#selectable").selectable({

    create:function(event, ui){
        $(event.target).children('#1').addClass('ui-selected');
    },
    
    stop:function(event, ui){
        $(event.target).children('.ui-selected').not(':first').removeClass('ui-selected');
        pitchspot =  $(event.target).children('.ui-selected').attr('id');
    }

});



