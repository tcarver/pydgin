(function( gene_page, $, undefined ) {
	
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
	        				         hit.interactors[j].pubmed+'</a>';
	        				row += ' <i class="fa fa-info-circle pmidinfo" data-toggle="popover" data-trigger="manual" data-poload="'+hit.interactors[j].pubmed+'"></i></td>';
	        				row += '</td>';
        				} else {
        					row += '<td></td>';
        				}
        				row += '<td>' + hit.interaction_source + '</td></tr>';
        			}
        			$('#table-interactor-'+ens_id+' tbody').append(row);
				}
				sections.add_pmid_popover('#table-interactor-'+ens_id);
				$('#table-interactor-'+ens_id).DataTable({'dom': 'Bfrtip',"buttons": ['copy', 'csv', 'excel', 'pdf', 'print']});
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
        			var ngenes = Object.keys(hit.gene_sets).length;
        			var row = '<tr><td><a href="' + hit.pathway_url + '" target="_blank">'+
        			          hit.pathway_name.replace(/_/g, ' ')+'</a> (';
        			var genes = add_genes(hit.pathway_name, ens_id, hit.gene_sets);
        			row += ngenes+')<td>'+genes+'</td></tr>';
         			$('#table-genesets-'+ens_id+' tbody').append(row);
				}
				$('#table-genesets-'+ens_id).DataTable({'dom': 'Bfrtip',"buttons": ['copy', 'csv', 'excel', 'pdf', 'print']});
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
        			var row = '<tr><td>'+hit.dil_study_id.replace('GDXHsS00', '')+'</td>';
        			row +='<td>'+add_pub(hit.pmid)+'</td>';
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
        			row +='<td class="visible-md visible-lg" nowrap>'+parseFloat((pval !== null? pval : hit.p_values.discovery)).toExponential()+'</td>';
        			row +='<td class="visible-md visible-lg">'+or+'</td>';
        			row +='<td class="visible-md visible-lg">'+(hit.alleles.maf !== null ? hit.alleles.maf : "")+'</td>';
        			row +='<td class="visible-md visible-lg">';
        			row += add_genes(hit.dil_study_id, ens_id, hit.genes);
        			row +='</td>';
        			row += '</tr>';
         			$('#table-study-'+ens_id+' tbody').append(row);
				}
				$('#table-study-'+ens_id+' .popoverData').popover({ 
				    html : true,
				    content: function() {
				      return $("#popover-content-"+$(this).attr('name')).html();
				    }
				});
				sections.add_pmid_popover('#table-study-'+ens_id);
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
			        "aaSorting": [[ 0, "asc" ]],
			        'dom': 'Bfrtip',
			        "buttons": ['copy', 'csv', 'excel', 'pdf', 'print']
			    });
				$("#study-spinner-"+ens_id).remove();
			}
		});
	}
	
	add_pub = function(pub) {
		var row ='<a href="http://www.ncbi.nlm.nih.gov/pubmed/'+pub.pmid+'?dopt=abstract" target="_blank">';
		if ($(window).width() > 768) {
			row += (pub.author ? pub.author : pub.pmid) + ' ' + (pub.journal ? '(<i>'+pub.journal+'</i>)' : '');
			row += '</a> ';
			row += '<i class="fa fa-info-circle pmidinfo" data-toggle="popover" data-trigger="manual" data-poload="'+pub.pmid+'"></i>';
		} else {
			row += (pub.author ? pub.author : pub.pmid) + '</a> ';
		}
		return row;
	}

	add_genes = function(hit_name, ens_id, genes) {
		var count = 0;
		var row = "";
		$.each(genes, function(key,value) {
			if(count == 14) {
				var more_id = hit_name+'_more';
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
