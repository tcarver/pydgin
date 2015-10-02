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
	        				         hit.interactors[j].pubmed+'</a></td>';
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
        			genes = add_genes(hit.pathway_name, ens_id, hit.gene_sets);
        			row += hit.gene_sets.length+')<td>'+genes+'</td></tr>';
         			$('#table-genesets-'+ens_id+' tbody').append(row);
				}
				$('#table-genesets-'+ens_id).DataTable();
				$("#gs-spinner-"+ens_id).remove();
			}
		});
	}
	
	// get gene sets for pathway gene sets section
	gene_page.get_study_details = function(ens_id) {
		$.ajax({
			type: "POST",
			url: "/gene/studies/",
			data: {'ens_id': ens_id},
		    beforeSend: function(xhr, settings) {
		        if (!this.crossDomain) {
		            xhr.setRequestHeader("X-CSRFToken", pydgin_utils.getCookie('csrftoken'));
		        }
		    },
			success: function(hits, textStatus, jqXHR) {
				pydgin_utils.add_spinner_before('table-study-'+ens_id, "study-spinner-"+ens_id);
				for(var i=0; i<hits.hits.length; i++) {
        			var hit = hits.hits[i]._source;
        			var row = '<tr><td>'+hit.dil_study_id+'</td>';
        			row +='<td><a href="http://www.ncbi.nlm.nih.gov/pubmed/'+hit.pmid+'?dopt=abstract" target="_blank">'+hit.pmid+'</td>';
        			row +='<td>'+hit.disease+'</td>';
        			row +='<td>'+hit.chr_band;
        			if(hit.notes !== null) {
        				row += ' <a name="'+hit.dil_study_id+'" class="popoverData" data-placement="top" href="#" rel="popover" data-trigger="hover">&dagger;</a>';
        				row += '<div id="popover-content-'+hit.dil_study_id+'" class="hide">'+hit.notes+'</div>';
        			}
        			row += '</td>';
        			row +='<td><a href="/marker/?m='+hit.marker+'">'+hit.marker+'</a></td>';

        			var or = hit.odds_ratios.combined.or;
        			if(or === null) {
        				or = hit.odds_ratios.discovery.or;
        				if(or === null) {
        					or = "";
        				}
        			}

        			row +='<td><span class="label '+(or < 1 ? 'label-primary': 'label-danger')+'">'+hit.alleles.major+'>'+hit.alleles.minor+'</span></td>';
        			var pval = hit.p_values.combined;
        			row +='<td nowrap>'+parseFloat((pval !== null? pval : hit.p_values.discovery)).toExponential()+'</td>';
        			row +='<td>'+or+'</td>';
        			row +='<td>'+(hit.alleles.maf !== null ? hit.alleles.maf : "")+'</td>';
        			row +='<td class="visible-lg">';
        			row += add_genes(hit.dil_study_id, ens_id, hit.genes);
        			row +='</td>';
        			row += '</tr>';
         			$('#table-study-'+ens_id+' tbody').append(row);
				}
				$('.popoverData').popover({ 
				    html : true,
				    content: function() {
				      return $("#popover-content-"+$(this).attr('name')).html();
				    }
				});
				var paginate = true;
				if(hits.hits.length < 12)
					paginate = false;
				$('#table-study-'+ens_id).dataTable({
					"bPaginate": paginate,
					"bInfo": paginate,
					"aoColumns": [null,
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false},
					     {"bSortable":false}],
			        "aaSorting": [[ 0, "asc" ]]
			    });
				$("#study-spinner-"+ens_id).remove();
			}
		});
	}

	add_genes = function(hit_name, ens_id, genes) {
		var count = 0;
		var row = "";
		$.each(genes, function(key,value) {
			if(count == 14) {
				more_id = hit_name+'_more';
				row += 
'<a role="button" data-toggle="collapse" href="#'+more_id+'" aria-expanded="false" aria-controls="mappingFilters">'+
' <i class="fa fa-caret-square-o-down"></i></a>';
				row += '<div class="collapse" id="'+more_id+'">';
			} else if(count > 0) {
				row += ', ';
			}
			row += (key !== ens_id ? '<a href="/gene/?g='+key+'">'+value+"</a>" : value)
			count++;
		});
		return row;
	}
}( window.gene_page = window.gene_page || {}, jQuery ));
