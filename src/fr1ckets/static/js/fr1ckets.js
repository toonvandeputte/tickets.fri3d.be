var prices = {};

$(document).ready(function() {
	$.ajax({
		url : 'api/get_prices',
		success: function(data) {
			prices = JSON.parse(data);
			for (thing in prices) {
				$('#' + thing).on('change', function() {
					recalc_total();
				});
			}
			recalc_total();
		},
	});
});

function recalc_total() {
	var total = 0;
	for (thing in prices) {
		var n = parseInt($('#'+thing).val());
		total += n * prices[thing];
	}
	$('#price_total').html("€" + total);
}

function mark_paid(id) {
	$.ajax({
		url: "api/purchase_mark_paid/" + id,
		success: function(data) {
			$('#mark_paid_' + id).html("great!");
			$('#remove_' + id).html("great!");
		},
		error: function(data) {
			$('#mark_paid_' + id).html('FAILED!');
		},
	});
}
function purchase_remove(id) {
	$.ajax({
		url: "api/purchase_remove/" + id,
		success: function(data) {
			$('#remove_' + id).html("great!");
		},
		error: function(data) {
			$('#remove_' + id).html('FAILED!');
		},
	});
}
$('#ticket_supporter').on('change', function() {
	var val = parseInt($("#ticket_supporter").val());
	var f = "";
	console.log(val);

	for (var i = 0; i < val; i++) {
		var id = "bar";
		f += '<hr/>';
		f += '<div class="form-group">';
		f += '  <label for="'+id+'" class="control-label col-sm-3 col-sm-offset-1">Naam</label>';
		f += '  <div class="col-sm-8">';
		f += '    <input class="form-control" id="'+id+'" name="'+id+'" type=text required aria-required="true">';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		f += '  <label for="'+id+'" class="control-label col-sm-3 col-sm-offset-1">Geboortedag</label>';
		f += '  <div class="col-sm-8">';
		f += '    <input class="form-control" id="'+id+'" name="'+id+'" type=text required aria-required="true" placeholder="YYYY-MM-DD">';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		f += '  <div class="checkbox col-sm-offset-4 col-sm-4 col-xs-6">';
		f += '    <label>';
		f += '      <input type="checkbox" id="'+id+'" name="'+id+'">';
		f += '      Vegetarisch';
		f += '    </label>';
		f += '  </div>';
		f += '  <div class="checkbox col-sm-offset-4 col-xs-6">';
		f += '    <label>';
		f += '      <input type="checkbox" id="'+id+'" name="'+id+'">';
		f += '      Premium';
		f += '    </label>';
		f += '  </div>';
		f += '</div>';
	}
	f += '<hr/>';

	$("#foo").html(f);
	if (val) {
		$("#foo").collapse('show');
	} else {
		$("#foo").collapse('hide');
	}

});
