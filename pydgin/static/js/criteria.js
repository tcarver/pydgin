(function( criteria, $, undefined ) {
	
	// get criteria details for criteria section
	criteria.get_criteria_details = function(feature_id, app_name) {
	
		url_ = "/" + app_name + "/criteria/";
		$.ajax({
			type: "POST",
			url: url_,
			data: {'feature_id': feature_id},
		    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
		        }
		    },
			success: function(hits, textStatus, jqXHR) {
				feature_id_ori = feature_id
				feature_id = feature_id.replace(/\./g, '_');
							
				pydgin_utils.add_spinner_before('table-criteria-'+feature_id, "criteria-spinner-"+feature_id);
				var row =  "";
				
				for(var i=0; i<hits.hits.length; i++) {
					var idx =  hits.hits[i]['_index'];
					var type = hits.hits[i]['_type'];
					var meta_info = hits['meta_info'];
					var link_info = hits['link_info'];
					var agg_disease_tags = hits['agg_disease_tags'].sort()

					criteria_desc = meta_info[idx][type];
										
					link_id_type = link_info[idx][type];
					
        			var hit = hits.hits[i]._source;
					var disease_tags = hit.disease_tags.sort()
			
					row += '<tr data-toggle="collapse" data-target="#'+ type +'" class="accordion-toggle"><td><button class="btn btn-default btn-xs"><span class="glyphicon glyphicon-eye-open"></span></button></td>';
					row += '<td>' + criteria_desc + '</td>';
					row += '<td><div class="disease-bar">';
								
					$.each(agg_disease_tags, function( index, dis_code ) {
		     			if($.inArray( dis_code, disease_tags ) >= 0){
							row += '<a class="btn btn-default btn-disease ' + dis_code + '">' + dis_code + '</a>';
						}else{
							row += '<span class="btn btn-disease blank" style="cursor:default">&nbsp;</span>';
						}
					});
					row += '</div></td></tr>';
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

				$('#table-criteria-'+feature_id+' tbody').append(row);

				$("#criteria-spinner-"+feature_id).remove();
	
				
				
			}
		});
	}
	
}( window.criteria = window.criteria || {}, jQuery ));









