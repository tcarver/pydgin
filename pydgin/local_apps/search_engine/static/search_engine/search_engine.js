(function( search_engine, $, undefined ) { 

	search_engine.autocomplete = function (searchId) {
		$( "#" + searchId ).autocomplete({
	        source: function( request, response ) {
	          $.ajax({
	            url: "/search/suggest",
	            contentType: 'application/json',
	            data: {
	              term: request.term,
	              idx: $( "#idx" ).val(),
	            },
	            success: function( data ) {
	              response( data.data );
	            }
	          });
	        },
	        minLength: 2,
	        open: function() {
	          $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
	        },
	        close: function() {
	          $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
	        },
	        select: function(event, ui) {
	        	// enter key triggers submit
	        	if (event.keyCode === 13){
	        		$( "#" + searchId ).trigger('submit');
	        	}
	        }
	      });
	}

}( window.search_engine = window.search_engine || {}, jQuery ));
