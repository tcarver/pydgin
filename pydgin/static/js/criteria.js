(function( criteria, $, undefined ) {
	
	// get criteria details for criteria section
	criteria.get_criteria_details = function(feature_id) {
		console.log('Feature id ' + feature_id)
		$.ajax({
			type: "POST",
			url: "/gene/criteria/",
			data: {'feature_id': feature_id},
		    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
		        }
		    },
			success: function(hits, textStatus, jqXHR) {
	
				pydgin_utils.add_spinner_before('table-criteria-'+ens_id, "criteria-spinner-"+ens_id);
				var row =  "";
				
				for(var i=0; i<hits.hits.length; i++) {
					var idx =  hits.hits[i]['_index'];
					var type = hits.hits[i]['_type'];
					var meta_info = hits['meta_info'];
					var link_info = hits['link_info'];
					var agg_disease_tags = hits['agg_disease_tags']
					console.log(agg_disease_tags)
					criteria_desc = meta_info[idx][type];
					
					link_id_type = link_info[idx][type];
					
        			var hit = hits.hits[i]._source;
					var disease_tags = hit.disease_tags.sort()
					row += '<tr data-toggle="collapse" data-target="#'+ type +'" class="accordion-toggle"><td><button class="btn btn-default btn-xs"><span class="glyphicon glyphicon-eye-open"></span></button></td>';
					row += '<td>' + criteria_desc + '</td>';
					row += '<td>';
					$.each(agg_disease_tags, function( index, dis_code ) {
						if($.inArray( dis_code, disease_tags ) >= 0){
						row += '<button class="btn btn-default btn-disease ' + dis_code + '">' + dis_code + '</button>';
						}else{
						row += '<button class="btn btn-default btn-disease">&nbsp;&nbsp;&nbsp;&nbsp;</button>';	
						}
					});
					row += '</td></tr>';
					row += '<tr>'
					row += '<td colspan="3" class="hiddenRow">';
					row += '<div id="'+type+'" class="accordian-body collapse" style="height: 0px;">';
					row += '<table class="table table-striped">';
					row += '<thead>';
					row += '<tr>';
					$.each(disease_tags, function( index, dis_code ) {
						 row += '<th>'+ dis_code+ '</th>';
						});
					row += '</tr>';
					row += '</thead>';
					row += '<tbody>';
					row += '<tr>';
					
					$.each(disease_tags, function( index, dis_code ) {
						notes_list = hits.hits[i]['_source'][dis_code]
						row += '<td>';
						$.each(notes_list, function( index, notes_dict ) {
							 row += '<a href="/' + link_id_type +'/' + notes_dict['fid'] + '/">';
							 row += notes_dict['fname'] ;
							 row += '</a>';
							 row += '<br/>';
						});
						 row += '</td>';
						
					});
					
					row += '</tr>';
					row += '</tbody>';
					row += '</table>';
					row += '</div>';
					row += '</td>';
					row += '</tr>';
        								
				}

				$('#table-criteria-'+ens_id+' tbody').append(row);

				$("#criteria-spinner-"+ens_id).remove();
	
				
				
			}
		});
	}
	
}( window.criteria = window.criteria || {}, jQuery ));









