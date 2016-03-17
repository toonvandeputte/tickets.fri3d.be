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

var tickets = [
	{
		name : '3bit ticket',
		price : 8,
		premium : 0,
		dob : Date.now() - 3 * 3600*24*356*1000,
	},
	{
		name : '4bit ticket',
		price : 16,
		premium : 0,
		dob : Date.now() - 6 * 3600*24*356*1000,
	},
	{
		name : '5bit ticket',
		price : 32,
		premium : 0,
		dob : Date.now() - 12 * 3600*24*356*1000,
	},
	{
		name : '6bit ticket',
		price : 64,
		premium : 8,
		dob : Date.now() - 24 * 3600*24*356*1000,
	},
	{
		name : '7bit ticket',
		price : 128,
		premium : 16,
		dob : Date.now() - 1000 * 3600*24*356*1000,
	},
]
var ticket_volunteering_cutoff = Date.now() - 16 * 3600*24*356*1000;
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

function mk_details_handler(details_target) {
	return function(e) {
		console.log("hello there! details_target and e are:");
		console.log(details_target);
		console.log(e);
		var dob = e.date.getTime();
		var can_volunteer = dob < ticket_volunteering_cutoff;
		var ticket = undefined;
		var f = "";
		for (var t in tickets) {
			if (dob >= tickets[t].dob) {
				ticket = tickets[t];
				break;
			}
		}
		var details_target_ticket_name = details_target + '_ticket_name';
		var details_target_ticket_price = details_target + '_ticket_price';
		var details_target_premium_toggle = details_target + '_volunteering_toggle';
		var details_target_cleanup_toggle = details_target + '_cleanup_toggle';
		var details_target_veggy_toggle = details_target + '_veggy_toggle';

		function update_ticket(ticket, show_premium) {
			var name = ticket.name;
			var price = ticket.price;

			if (show_premium) {
				name += " (premium)";
				price += ticket.premium;
			}
			$('#'+details_target_ticket_name).text(name);
			$('#'+details_target_ticket_price).text(price);
		}

		// this part needs to be shown for every ticket
		f += '<div class="row">';
		f += '  <div class="col-sm-6 col-sm-offset-4">';
		f += '    <p id="'+details_target_ticket_name+'">'+ticket.name+'</p>';
		f += '  </div>';
		f += '  <div class="col-sm-2 text-right">';
		f += '    <p id="'+details_target_ticket_price+'">€'+ticket.price+'</p>';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		f += '  <div class="checkbox col-sm-offset-4 col-sm-4 col-xs-6">';
		f += '    <label>';
		f += '      <input type="checkbox" id="'+details_target_veggy_toggle+'" name="'+details_target_veggy_toggle+'">';
		f += '      Vegetarisch';
		f += '    </label>';
		f += '  </div>';
		if (can_volunteer) {
			f += '  <div class="checkbox col-sm-4 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+details_target_premium_toggle+'" name="'+details_target_premium_toggle+'">';
			f += '      Premium';
			f += '    </label>';
			f += '  </div>';
			f += '  <div class="checkbox col-sm-offset-4 col-sm-8 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+details_target_cleanup_toggle+'" name="'+details_target_cleanup_toggle+'">';
			f += '      Help opkuisen de dag er na (pizza voorzien!)';
			f += '    </label>';
			f += '  </div>';
		}
		f += '</div>';

		// throw it into the DOM so we can add events to it
		$('#'+details_target).html(f);

		update_ticket(ticket, false);

		// wire in needed handlers
		$('#'+details_target_premium_toggle).on('change', function() {
			var premium = this.checked;
			if (premium) {
				update_ticket(ticket, true);
				$('#'+details_target_cleanup_toggle).prop('checked', false);
				$('#'+details_target_cleanup_toggle).prop('disabled', true);
			} else {
				update_ticket(ticket, false);
				$('#'+details_target_cleanup_toggle).prop('disabled', false);
			}
		});

		// and collapse it
		$('#'+details_target).collapse('show');
	}
}

$('#ticket_supporter').on('change', function() {
	var val = parseInt($("#ticket_supporter").val());
	var f = "";

	// for each ticket, add some form fields to the collapsible target
	// each of those containing itself a collapsible part on their own,
	// which gets collapsed by datepicking
	for (var i = 0; i < val; i++) {
		var name_id = "ticket_supporter_name_"+i;
		var dob_id = "ticket_supporter_dob_"+i;
		var details_id = "ticket_supporter_details_"+i;
		f += '<hr/>';
		f += '<div class="form-group">';
		f += '  <label for="'+name_id+'" class="control-label col-sm-3 col-sm-offset-1">Naam</label>';
		f += '  <div class="col-sm-8">';
		f += '    <input class="form-control" id="'+name_id+'" name="'+name_id+'" type=text required aria-required="true">';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		f += '  <label for="'+dob_id+'" class="control-label col-sm-3 col-sm-offset-1">Geboortedag</label>';
		f += '  <div class="col-sm-8">';
		f += '   <input id="'+dob_id+'" name="'+dob_id+'" class="form-control" type="text" required aria-required="true">';
		f += '  </div>';
		f += '</div>';
		f += '<div class="collapsible" id="'+details_id+'">';
		f += '</div>';
	}
	f += '<hr/>';

	// push it into the DOM so we can hook event listeners on it
	$("#ticket_details").html(f);

	// for each ticket, add relevant event handlers
	for (var i = 0; i < val; i++) {
		var details_target = 'ticket_supporter_details_'+i;
		// instantiate datepicker, hand the callback the per-ticket
		// collapsible area to handle
		$("#ticket_supporter_dob_"+i).datepicker({
				format : 'yyyy-mm-dd',
				autoclose : true
		}).on('changeDate', mk_details_handler(details_target));
	}

	// and collapse the whole target if a nonzero number of tickets was selected
	if (val) {
		$("#ticket_details").collapse('show');
	} else {
		$("#ticket_details").collapse('hide');
	}

});
