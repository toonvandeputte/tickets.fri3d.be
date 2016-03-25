var products = [];
var costs = {
	tickets : {},
	reset : {},
};

function handle_reservation(data) {

	if ($('#email').val() == '') {
		$("#email_reservation_collapse").html('');
		return;
	}

	var reservation = JSON.parse(data);
	var available = Date.now() >= (reservation.available_from*1000);
	var f = '';

	if (!available) {
		var available_date = new Date();
		available_date.setTime(reservation.available_from*1000);
		f += '<div class="row">';
		f += '  <div class="alert alert-danger text-center" role="alert">';
		f += '    <p>Met dit email kan je pas vanaf '+available_date.toLocaleDateString()+' '+available_date.toLocaleTimeString()+' bestellen!</p>';
		f += '  </div>';
		f += '</div>';
	} else if (available && reservation.discount > 0) {
		f += '<div class="row">';
		f += '  <div class="alert alert-success text-center" role="alert">';
		f += '    <p>Met dit email krijg je éénmalig €'+reservation.discount+' korting!</p>';
		f += '  </div>';
		f += '</div>';
	}

	$("#email_reservation_collapse").html(f);

}

$(document).ready(function() {
	$.ajax({
		url : 'api/get_products',
		success: function(data) {
			products = JSON.parse(data);
			for (var i in products) {
				console.log(products[i]);
				if (products[i].max_dob) {
					products[i].max_dob *= 1000;
				}
			}
		},
	});
	$('#email').on('change', function() {
		if ($('#email').val().length > 0) {
			$.ajax({
				url : 'api/get_reservation/' + $('#email').val(),
				success: function(data) {
					handle_reservation(data);
				},
				error: function(data) {
					handle_reservation(data);
				},
			});
		} else {
			handle_reservation('');
		}
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

var tickets_normal = [
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
];
var tickets_billable = [
	{
		name : '8bit ticket',
		price : 256,
		premium : 0,
		dob : Date.now() - 1000 * 3600*24*356*1000,
	},
];

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

function make_cb_dob_change_normal(visitor, year_src, month_src, day_src) {
	return function(e) {
		var dob = new Date($('#'+year_src).val(), $('#'+month_src).val(), $('#'+day_src).val()).getTime();
		var can_volunteer = dob < ticket_volunteering_cutoff;
		var ticket = undefined;
		var f = "";
		for (var t in products) {
			if (products[t].name.indexOf('ticket') == -1) {
				continue;
			}
			if (products[t].billable) {
				continue;
			}
			if (dob >= products[t].max_dob) {
				ticket = products[t];
				break;
			}
		}
		var visitor_ticket_name = visitor + '_display_ticket_name';
		var visitor_ticket_price = visitor + '_display_ticket_price';
		var visitor_premium_toggle = visitor + '_premium_toggle';
		var visitor_cleanup_toggle = visitor + '_cleanup_toggle';
		var visitor_veggy_toggle = visitor + '_veggy_toggle';

		function update_ticket(ticket, show_premium) {
			var name = ticket.display;
			var price = ticket.volunteering_price;

			if (show_premium) {
				name += " (premium)";
				price = ticket.price;
			}
			$('#'+visitor_ticket_name).text(name);
			$('#'+visitor_ticket_price).text("€"+price);
		}

		// this part needs to be shown for every ticket
		f += '<div class="row">';
		f += '  <div class="col-sm-6 col-sm-offset-4">';
		f += '    <p id="'+visitor_ticket_name+'">'+ticket.name+'</p>';
		f += '  </div>';
		f += '  <div class="col-sm-2 text-right">';
		f += '    <p id="'+visitor_ticket_price+'">€'+ticket.price+'</p>';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		f += '  <div class="checkbox col-sm-offset-4 col-sm-4 col-xs-6">';
		f += '    <label>';
		f += '      <input type="checkbox" id="'+visitor_veggy_toggle+'" name="'+visitor_veggy_toggle+'">';
		f += '      Vegetarisch';
		f += '    </label>';
		f += '  </div>';
		if (can_volunteer) {
			f += '  <div class="checkbox col-sm-4 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+visitor_premium_toggle+'" name="'+visitor_premium_toggle+'">';
			f += '      Premium';
			f += '    </label>';
			f += '  </div>';
			f += '  <div class="checkbox col-sm-offset-4 col-sm-8 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+visitor_cleanup_toggle+'" name="'+visitor_cleanup_toggle+'">';
			f += '      Help opkuisen de dag er na (pizza voorzien!)';
			f += '    </label>';
			f += '  </div>';
		}
		f += '</div>';

		// throw it into the DOM so we can add events to it
		$('#'+visitor).html(f);

		update_ticket(ticket, false);

		// wire in needed handlers
		$('#'+visitor_premium_toggle).on('change', function() {
			var premium = this.checked;
			if (premium) {
				update_ticket(ticket, true);
				$('#'+visitor_cleanup_toggle).prop('checked', false);
				$('#'+visitor_cleanup_toggle).prop('disabled', true);
			} else {
				update_ticket(ticket, false);
				$('#'+visitor_cleanup_toggle).prop('disabled', false);
			}
		});

		// and collapse it
		$('#'+visitor).collapse('show');
	}
}

function make_cb_dob_change_billable(visitor, year_src, month_src, day_src) {
	return function(e) {
		var dob = new Date($('#'+year_src).val(), $('#'+month_src).val(), $('#'+day_src).val()).getTime();
		var can_volunteer = dob < ticket_volunteering_cutoff;
		var ticket = undefined;
		var f = "";
		for (var t in products) {
			if (products[t].name.indexOf('ticket') == -1) {
				continue;
			}
			if (!products[t].billable) {
				continue;
			}
			if (dob >= products[t].max_dob) {
				ticket = products[t];
				break;
			}
		}
		var visitor_ticket_name = visitor + '_display_ticket_name';
		var visitor_ticket_price = visitor + '_display_ticket_price';
		var visitor_volunteering_toggle = visitor + '_volunteering_toggle';
		var visitor_cleanup_toggle = visitor + '_cleanup_toggle';
		var visitor_veggy_toggle = visitor + '_veggy_toggle';

		function update_ticket(ticket, show_volunteering) {
			var name = ticket.display;
			var price = ticket.price;

			if (show_volunteering) {
				name += " (volunteering)";
				price += ticket.volunteering_price;
			}
			$('#'+visitor_ticket_name).text(name);
			$('#'+visitor_ticket_price).text("€"+price);
		}

		// this part needs to be shown for every ticket
		f += '<div class="row">';
		f += '  <div class="col-sm-6 col-sm-offset-4">';
		f += '    <p id="'+visitor_ticket_name+'">'+ticket.name+'</p>';
		f += '  </div>';
		f += '  <div class="col-sm-2 text-right">';
		f += '    <p id="'+visitor_ticket_price+'">€'+ticket.price+'</p>';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		f += '  <div class="checkbox col-sm-offset-4 col-sm-4 col-xs-6">';
		f += '    <label>';
		f += '      <input type="checkbox" id="'+visitor_veggy_toggle+'" name="'+visitor_veggy_toggle+'">';
		f += '      Vegetarisch';
		f += '    </label>';
		f += '  </div>';
		if (can_volunteer) {
			f += '  <div class="checkbox col-sm-4 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+visitor_volunteering_toggle+'" name="'+visitor_volunteering_toggle+'">';
			f += '      Help graag mee tijdens kamp';
			f += '    </label>';
			f += '  </div>';
			f += '  <div class="checkbox col-sm-offset-4 col-sm-8 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+visitor_cleanup_toggle+'" name="'+visitor_cleanup_toggle+'">';
			f += '      Help opkuisen de dag er na (pizza voorzien!)';
			f += '    </label>';
			f += '  </div>';
		}
		f += '</div>';

		// throw it into the DOM so we can add events to it
		$('#'+visitor).html(f);

		update_ticket(ticket, false);

		// and collapse it
		$('#'+visitor).collapse('show');
	}
}

$('#ticket_normal').on('change', function() {
	var val = parseInt($("#ticket_normal").val());
	var f = "";

	f += '<div class="row text-center">';
	f += '  <p><h4>Normale tickets:</h4></p>';
	f += '</div>';

	// for each ticket, add some form fields to the collapsible target
	// each of those containing itself a collapsible part on their own,
	// which gets collapsed by datepicking
	for (var i = 0; i < val; i++) {
		var name_id = "ticket_normal_visitors_"+i+"_name";
		var dob_year_id = "ticket_normal_visitors_"+i+"_dob_year";
		var dob_month_id = "ticket_normal_visitors_"+i+"_dob_month";
		var dob_day_id = "ticket_normal_visitors_"+i+"_dob_day";
		var options_id = "ticket_normal_visitors_"+i+"_options";
		f += '<hr/>';
		f += '<div class="form-group">';
		f += '  <label for="'+name_id+'" class="control-label col-sm-3 col-sm-offset-1">Naam</label>';
		f += '  <div class="col-sm-8">';
		f += '    <input class="form-control" id="'+name_id+'" name="'+name_id+'" type=text required aria-required="true">';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		// XXX label for what?
		f += '  <label class="control-label col-sm-3 col-sm-offset-1">Geboortedag</label>';
		f += '  <div class="col-sm-4">';
		f += '   <input id="'+dob_year_id+'" name="'+dob_year_id+'" class="form-control col-sm-2" type="tel" maxlength="4" pattern="[0-9]{4}" required aria-required="true" placeholder="YYYY">';
		f += '  </div>';
		f += '  <div class="col-sm-2">';
		f += '   <input id="'+dob_month_id+'" name="'+dob_month_id+'" class="form-control col-sm-1" type="tel" maxlength="2" pattern="[0-9]{1,2}" required aria-required="true" placeholder="MM">';
		f += '  </div>';
		f += '  <div class="col-sm-2">';
		f += '   <input id="'+dob_day_id+'" name="'+dob_day_id+'" class="form-control col-sm-1" type="tel" maxlength="2" pattern="[0-9]{1,2}" required aria-required="true" placeholder="DD">';
		f += '  </div>';
		f += '</div>';
		f += '<div class="collapsible" id="'+options_id+'">';
		f += '</div>';
	}
	f += '<hr/>';

	// push it into the DOM so we can hook event listeners on it
	$("#ticket_normal_visitors").html(f);

	// for each ticket, add relevant event handlers
	for (var i = 0; i < val; i++) {
		// changing the dob should result in a collapse of the
		// per-ticket options, so wire in the callback giving
		// it the needed parts to fill the per-ticket collapsable
		var options_id = "ticket_normal_visitors_"+i+"_options";
		var dob_year_id = "ticket_normal_visitors_"+i+"_dob_year";
		var dob_month_id = "ticket_normal_visitors_"+i+"_dob_month";
		var dob_day_id = "ticket_normal_visitors_"+i+"_dob_day";
		$("#"+dob_year_id).on('change', make_cb_dob_change_normal(options_id, dob_year_id, dob_month_id, dob_day_id));
		$("#"+dob_month_id).on('change', make_cb_dob_change_normal(options_id, dob_year_id, dob_month_id, dob_day_id));
		$("#"+dob_day_id).on('change', make_cb_dob_change_normal(options_id, dob_year_id, dob_month_id, dob_day_id));
	}

	// and collapse the whole target if a nonzero number of tickets was selected
	if (val) {
		$("#ticket_normal_visitors").collapse('show');
	} else {
		$("#ticket_normal_visitors").collapse('hide');
	}

});

$('#ticket_billable').on('change', function() {
	var val = parseInt($("#ticket_billable").val());
	var f = "";

	f += '<div class="row text-center">';
	f += '  <p><h4>Factureerbare tickets:</h4></p>';
	f += '</div>';

	// for each ticket, add some form fields to the collapsible target
	// each of those containing itself a collapsible part on their own,
	// which gets collapsed by datepicking
	for (var i = 0; i < val; i++) {
		var name_id = "ticket_billable_visitors_"+i+"_name";
		var options_id = "ticket_billable_visitors_"+i+"_options";
		var dob_year_id = "ticket_billable_visitors_"+i+"_dob_year";
		var dob_month_id = "ticket_billable_visitors_"+i+"_dob_month";
		var dob_day_id = "ticket_billable_visitors_"+i+"_dob_day";
		f += '<hr/>';
		f += '<div class="form-group">';
		f += '  <label for="'+name_id+'" class="control-label col-sm-3 col-sm-offset-1">Naam</label>';
		f += '  <div class="col-sm-8">';
		f += '    <input class="form-control" id="'+name_id+'" name="'+name_id+'" type=text required aria-required="true">';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		// XXX label for what?
		f += '  <label class="control-label col-sm-3 col-sm-offset-1">Geboortedag</label>';
		f += '  <div class="col-sm-4">';
		f += '   <input id="'+dob_year_id+'" name="'+dob_year_id+'" class="form-control col-sm-2" type="tel" maxlength="4" pattern="[0-9]{4}" required aria-required="true" placeholder="YYYY">';
		f += '  </div>';
		f += '  <div class="col-sm-2">';
		f += '   <input id="'+dob_month_id+'" name="'+dob_month_id+'" class="form-control col-sm-1" type="tel" maxlength="2" pattern="[0-9]{1,2}" required aria-required="true" placeholder="MM">';
		f += '  </div>';
		f += '  <div class="col-sm-2">';
		f += '   <input id="'+dob_day_id+'" name="'+dob_day_id+'" class="form-control col-sm-1" type="tel" maxlength="2" pattern="[0-9]{1,2}" required aria-required="true" placeholder="DD">';
		f += '  </div>';
		f += '</div>';
		f += '<div class="collapsible" id="'+options_id+'">';
		f += '</div>';
	}
	// for billables, always include the company details (so long as there is a ticket shown)
	if (val > 0) {
		f += '<hr/>';
		f += '<div class="row text-center">';
		f += '  <p><h4>Factuurgegevens:</h4></p>';
		f += '</div>';
		f += '<hr/>';
		f += '<div class="form-group">';
		f += '  <label for="ticket_billable_name" class="control-label col-sm-3 col-sm-offset-1">Bedrijf</label>';
		f += '  <div class="col-sm-8">';
		f += '    <input class="form-control" id="ticket_billable_name" name="ticket_billable_name" type=text required aria-required="true">';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		f += '  <label for="ticket_billable_address" class="control-label col-sm-3 col-sm-offset-1">Adres</label>';
		f += '  <div class="col-sm-8">';
		f += '    <textarea class="form-control" id="ticket_billable_address" name="ticket_billable_address" rows="3" required aria-required="true"></textarea>';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		f += '  <label for="ticket_billable_vat" class="control-label col-sm-3 col-sm-offset-1">BTW</label>';
		f += '  <div class="col-sm-8">';
		f += '    <input class="form-control" id="ticket_billable_vat" name="ticket_billable_vat" type=text required aria-required="true" placeholder="BE 4444.333.333">';
		f += '  </div>';
		f += '</div>';
		f += '<hr/>';
	}

	// push it into the DOM so we can hook event listeners on it
	$("#ticket_billable_visitors").html(f);

	// for each ticket, add relevant event handlers
	for (var i = 0; i < val; i++) {
		var options_id = "ticket_billable_visitors_"+i+"_options";
		var dob_year_id = "ticket_billable_visitors_"+i+"_dob_year";
		var dob_month_id = "ticket_billable_visitors_"+i+"_dob_month";
		var dob_day_id = "ticket_billable_visitors_"+i+"_dob_day";

		// changing the dob should result in a collapse of the
		// per-ticket options, so wire in the callback giving
		// it the needed parts to fill the per-ticket collapsable
		var dob_year_id = "ticket_billable_visitors_"+i+"_dob_year";
		var dob_month_id = "ticket_billable_visitors_"+i+"_dob_month";
		var dob_day_id = "ticket_billable_visitors_"+i+"_dob_day";
		$("#"+dob_year_id).on('change', make_cb_dob_change_billable(options_id, dob_year_id, dob_month_id, dob_day_id));
		$("#"+dob_month_id).on('change', make_cb_dob_change_billable(options_id, dob_year_id, dob_month_id, dob_day_id));
		$("#"+dob_day_id).on('change', make_cb_dob_change_billable(options_id, dob_year_id, dob_month_id, dob_day_id));
	}

	// and collapse the whole target if a nonzero number of tickets was selected
	if (val) {
		$("#ticket_billable_visitors").collapse('show');
	} else {
		$("#ticket_billable_visitors").collapse('hide');
	}

});

