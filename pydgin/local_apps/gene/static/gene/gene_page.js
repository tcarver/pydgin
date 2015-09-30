(function( gene_page, $, undefined ) {
	// retrieve publications for publications section
	gene_page.get_publication_details = function(pubid, pmids) {
		$.ajax({
			type: "POST",
			url: "/gene/publications/",
			data: {'pmids': pmids},
		    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
		        }
		    },
			success: function(hits, textStatus, jqXHR) {
				pydgin_utils.add_spinner_before(pubid, pubid+"-spinner");
				for(var i=0; i<hits.hits.length; i++) {
        			var hit = hits.hits[i]._source;
        			var row =  '<tr><td><a href="http://www.ncbi.nlm.nih.gov/pubmed/' + hit.pmid + '?dopt=abstract" target="_blank">'+ hit.pmid +
        					'</a></td>';
        			row += '<td>' + hit.title + '</td>';
        			if (hit.authors[0] === undefined) {
        				row += '<td>n/a</td>';
        			} else {
        				row += '<td>' + hit.authors[0].name + '</td>';
        			}
        			row += '<td>' + hit.journal + '</td>';
        			if(hit.tags.disease) {
        				var disease = hit.tags.disease;
        				var diseaseArray = $.map(disease, function(item, index) {
        				    return item.toUpperCase();
        				});
        				row += '<td>' + diseaseArray + '</td>';
        			} else {
        				row += '<td>N/A</td>';
        			}
        			row += '<td>' + hit.date + '</td></tr>';
        			$('#'+pubid+' tbody').append(row);
				}
				$('#'+pubid).DataTable();
				$("#"+pubid+"-spinner").remove();
			}
		});
	}

	// get interaction details for interation section
	gene_page.get_interaction_details = function(ens_id) {
		$.ajax({
			type: "POST",
			url: "/gene/interactions/",
			data: {'ens_id': ens_id},
		    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
		        }
		    },
			success: function(hits, textStatus, jqXHR) {
				pydgin_utils.add_spinner_before('table-interactor-'+ens_id, "interactor-spinner-"+ens_id);
				for(var i=0; i<hits.hits.length; i++) {
        			var hit = hits.hits[i]._source;
        			var row =  "";
        			for(var j=0; j<hit.interactors.length; j++) {
        				row += '<tr><td><a href="/gene/?g=' + hit.interactors[j].interactor + '">'+hit.interactors[j].symbol+'</a></td>';
        				if(hit.interactors[j].pubmed) {
	        				row += '<td><a href="http://www.ncbi.nlm.nih.gov/pubmed/' + 
	        				         hit.interactors[j].pubmed + '?dopt=abstract" target="_blank">'+
	        				         hit.interactors[j].pubmed+' </a></td>';
        				} else {
        					row += '<td></td>';
        				}
        				row += '<td>' + hit.interaction_source + '</td></tr>';
        			}
        			$('#table-interactor-'+ens_id+' tbody').append(row);
				}
				$('#table-interactor-'+ens_id).DataTable();
				$("#interactor-spinner-"+ens_id).remove();
			}
		});
	}

	// get gene sets for pathway gene sets section
	gene_page.get_genesets_details = function(ens_id) {
		$.ajax({
			type: "POST",
			url: "/gene/genesets/",
			data: {'ens_id': ens_id},
		    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
		        }
		    },
			success: function(hits, textStatus, jqXHR) {
				pydgin_utils.add_spinner_before('table-genesets-'+ens_id, "gs-spinner-"+ens_id);
				for(var i=0; i<hits.hits.length; i++) {
        			var hit = hits.hits[i]._source;
        			var row = '<tr><td><a href="' + hit.pathway_url + '" target="_blank">'+
        			          hit.pathway_name.replace(/_/g, ' ')+'</a> (';
        			var genes = '';
        			var count = 0;
        			$.each(hit.gene_sets, function(key,value) {
        				if(count == 14) {
        					more_id = hit.pathway_name+'_more';
        					genes += 
        	'<a role="button" data-toggle="collapse" href="#'+more_id+'" aria-expanded="false" aria-controls="mappingFilters">'+
        	'<i class="fa fa-caret-square-o-down"></i></a>';
        					genes += '<div class="collapse" id="'+more_id+'">';
        				}
        				genes += '<a href="/gene/?g='+key+'">'+value+"</a> ";
        				count++;
        			});
        			row += count+')<td>'+genes+'</td></tr>';
         			$('#table-genesets-'+ens_id+' tbody').append(row);
				}
				$('#table-genesets-'+ens_id).DataTable();
				$("#gs-spinner-"+ens_id).remove();
			}
		});
	}

}( window.gene_page = window.gene_page || {}, jQuery ));
