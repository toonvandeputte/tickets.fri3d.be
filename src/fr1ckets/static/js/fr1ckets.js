var products = [];

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
		f += '    <p>Met dit email-adres kan je pas vanaf '+available_date.toLocaleDateString()+' '+available_date.toLocaleTimeString()+' bestellen!</p>';
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

function find_ticket_by_dob(dob, billable) {

	var ticket = undefined;
	for (var t in products) {
		if (products[t].name.indexOf('ticket') == -1) {
			continue;
		}
		if (products[t].billable != billable) {
			continue;
		}
		if (dob >= products[t].max_dob) {
			ticket = products[t];
			break;
		}
	}
	console.log("mapped date "+dob+" to ticket "+ticket.name);
	return ticket;

}

function enumerate_choices() {
	var choices = [];

	for (var i in products) {
		if (products[i].name.indexOf('ticket') != -1) {
			// skip tickets
			continue;
		}
		var n = parseInt($('#'+products[i].name).val() || 0);
		if (n == 0) {
			continue;
		}
		var c = {
			n : n,
			price : products[i].price,
			name : products[i].display,
		}
		choices.push(c);
	}

	var n_tickets = parseInt($('#n_tickets').val());

	for (var i = 0; i < n_tickets; i++) {
		var src = 'tickets_'+i;
		var year_src = src + '_dob_year';
		var month_src = src + '_dob_month';
		var day_src = src + '_dob_day';
		var name_src = src + '_name';
		var premium_src = src + '_options_premium';
		var cleanup_src = src + '_options_cleanup_toggle';
		var dob = new Date($('#'+year_src).val(), $('#'+month_src).val(), $('#'+day_src).val()).getTime();
		var ticket = find_ticket_by_dob(dob, false);
		var name = $('#' + name_src).val();
		var volunteering = !$('#'+premium_src).prop('checked') || $('#'+cleanup_src).prop('checked');
		var price = ticket.price;
		if (volunteering) {
			price = ticket.volunteering_price;
		}
		var c = {
			n : 1,
			price : price,
			name : ticket.display + " voor " + name,
		}
		choices.push(c);
	}

	console.dir(choices);

}

$(document).ready(function() {
	$.ajax({
		url : 'api/get_products',
		success: function(data) {
			products = JSON.parse(data);
			for (var i in products) {
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

var showing_business_info = false;
function display_business_info() {

	var n_tickets = parseInt($('#n_tickets').val());
	var n_tickets_billable = 0;

	console.log("checking");
	for (var i = 0; i < n_tickets; i++) {
		var fmt = "tickets_"+i;
		var billable_id = fmt+"_billable";
		var billable = Boolean($('#'+billable_id).prop('checked'));
		if (billable) {
			n_tickets_billable++;
		}
	}

	if (!n_tickets_billable && showing_business_info) {
		// hide
		showing_business_info = false;
		$('#business_info').html('');
		$('#business_info').collapse('hide');
	} else if (n_tickets_billable && !showing_business_info) {
		// display
		showing_business_info = true;
		var f = '';
		f += '<div class="row text-center">';
		f += '  <p><h4>Factuurgegevens:</h4></p>';
		f += '</div>';
		f += '<hr/>';
		f += '<div class="form-group">';
		f += '  <label for="business_name" class="control-label col-sm-3 col-sm-offset-1">Bedrijf</label>';
		f += '  <div class="col-sm-8">';
		f += '    <input class="form-control" id="business_name" name="business_name" type=text required aria-required="true">';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		f += '  <label for="business_address" class="control-label col-sm-3 col-sm-offset-1">Adres</label>';
		f += '  <div class="col-sm-8">';
		f += '    <textarea class="form-control" id="business_address" name="business_address" rows="3" required aria-required="true"></textarea>';
		f += '  </div>';
		f += '</div>';
		f += '<div class="form-group">';
		f += '  <label for="business_vat" class="control-label col-sm-3 col-sm-offset-1">BTW</label>';
		f += '  <div class="col-sm-8">';
		f += '    <input class="form-control" id="business_vat" name="business_vat" type=text required aria-required="true" placeholder="BE 4444.333.333">';
		f += '  </div>';
		f += '</div>';
		f += '<hr/>';
		$('#business_info').html(f);
		$('#business_info').collapse('show');
	}

}

function mk_cb_update_visitor_options(index) {
	return function(e) {
		var fmt = "tickets_"+index;
		var name_id = fmt+"_name";
		var dob_year_id = fmt+"_dob_year";
		var dob_month_id = fmt+"_dob_month";
		var dob_day_id = fmt+"_dob_day";
		var billable_id = fmt+"_billable";
		var options_id = fmt+"_options";

		if ($('#'+dob_year_id).val() == '' &&
			$('#'+dob_month_id).val() == '' &&
			$('#'+dob_day_id).val() == '') {
			return;
		}
		var dob = new Date($('#'+dob_year_id).val(), $('#'+dob_month_id).val(), $('#'+dob_day_id).val()).getTime();
		var billable = Boolean($('#'+billable_id).prop('checked'));
		var can_volunteer = Boolean(dob < ticket_volunteering_cutoff);

		var ticket = find_ticket_by_dob(dob, billable);

		var ticket_name_id = fmt + "_options_ticket_name";
		var ticket_price_id = fmt + "_options_ticket_price";
		var vegitarian_id = fmt + "_options_vegitarian";

		var f = '';
		// this part needs to be shown for every ticket
		if (ticket) {
			f += '<div class="row">';
			f += '  <div class="col-sm-6 col-sm-offset-4">';
			f += '    <p id="'+ticket_name_id+'">'+ticket.display+'</p>';
			f += '  </div>';
			f += '  <div class="col-sm-2 text-right">';
			f += '    <p id="'+ticket_price_id+'">€'+ticket.price+'</p>';
			f += '  </div>';
			f += '</div>';
			f += '<div class="form-group">';
			f += '  <div class="checkbox col-sm-offset-4 col-sm-4 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+vegitarian_id+'" name="'+vegitarian_id+'">';
			f += '      Vegetarisch';
			f += '    </label>';
			f += '  </div>';
		}
		if (billable && can_volunteer) {
			var volunteering_id = fmt + "_options_volunteers_during";
			var cleanup_id = fmt + "_options_volunteers_after";
			f += '  <div class="checkbox col-sm-4 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+volunteering_id+'" name="'+volunteering_id+'">';
			f += '      Help graag mee tijdens kamp';
			f += '    </label>';
			f += '  </div>';
			f += '  <div class="checkbox col-sm-offset-4 col-sm-8 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+cleanup_id+'" name="'+cleanup_id+'">';
			f += '      Help opkuisen de dag er na (pizza voorzien!)';
			f += '    </label>';
			f += '  </div>';
		} else if (!billable && can_volunteer) {
			var premium_id = fmt + "_options_premium";
			var cleanup_id = fmt + "_options_volunteers_after";
			f += '  <div class="checkbox col-sm-4 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+premium_id+'" name="'+premium_id+'">';
			f += '      Premium';
			f += '    </label>';
			f += '  </div>';
			f += '  <div class="checkbox col-sm-offset-4 col-sm-8 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+cleanup_id+'" name="'+cleanup_id+'">';
			f += '      Help opkuisen de dag er na (pizza voorzien!)';
			f += '    </label>';
			f += '  </div>';
		}
		f += '</div>';
		// throw it into the DOM so we can add events to it
		$('#'+options_id).html(f);
		if (billable && can_volunteer) {
			;
		} else if (!billable && can_volunteer) {
			var premium_id = fmt + "_options_premium";
			var cleanup_id = fmt + "_options_volunteers_after";
			$('#'+premium_id).on('change', function() {
				var display_name = '';
				var display_price = 0;
				var is_premium = Boolean(this.checked);
				if (is_premium) {
					display_name = ticket.display + ' (premium)';
					display_price = ticket.price;
				} else {
					display_name = ticket.display;
					display_price = ticket.volunteering_price;
				}
				$('#'+ticket_name_id).text(display_name);
				$('#'+ticket_price_id).text('€'+display_price);
			});
		}

		/*
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
		*/
		// and collapse it
		$('#'+options_id).collapse('show');

	}
}

$('#n_tickets').on('change', display_business_info);
$('#n_tickets').on('change', function() {
	var val = parseInt($("#n_tickets").val());
	var f = "";

	f += '<div class="row text-center">';
	f += '  <p><h4>Individuele tickets:</h4></p>';
	f += '</div>';

	// for each ticket, add some form fields to the collapsible target
	// each of those containing itself a collapsible part on their own,
	// which gets collapsed by datepicking
	for (var i = 0; i < val; i++) {
		var fmt = 'tickets_'+i
		var name_id = fmt+"_name";
		var dob_year_id = fmt+"_dob_year";
		var dob_month_id = fmt+"_dob_month";
		var dob_day_id = fmt+"_dob_day";
		var billable_id = fmt+"_billable";
		var options_id = fmt+"_options";
		f += '<hr/>';
		// name box
		f += '<div class="form-group">';
		f += '  <label for="'+name_id+'" class="control-label col-sm-3 col-sm-offset-1">Naam</label>';
		f += '  <div class="col-sm-8">';
		f += '    <input class="form-control" id="'+name_id+'" name="'+name_id+'" type=text required aria-required="true">';
		f += '  </div>';
		f += '</div>';
		// dob box
		f += '<div class="form-group">';
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
		// bill box
		f += '<div class="form-group">';
		f += '  <label class="control-label col-sm-3 col-sm-offset-1 for="'+billable_id+'">Met factuur (€256+BTW)</label>';
		f += '  <div class="col-sm-8">';
		f += '    <input type="checkbox" id="'+billable_id+'" name="'+billable_id+'">'
		f += '  </div>';
		f += '</div>';
		// collapse for options depending on input above
		f += '<div class="collapsible" id="'+options_id+'">';
		f += '</div>';
	}
	f += '<hr/>';

	// push it into the DOM so we can hook event listeners on it
	$("#tickets").html(f);

	// for each ticket, add relevant event handlers
	for (var i = 0; i < val; i++) {
		// changing the dob should result in a collapse of the
		// per-ticket options, so wire in the callback giving
		// it the needed parts to fill the per-ticket collapsable
		var fmt = "tickets_"+i;
		var name_id = fmt+"_name";
		var dob_year_id = fmt+"_dob_year";
		var dob_month_id = fmt+"_dob_month";
		var dob_day_id = fmt+"_dob_day";
		var billable_id = fmt+"_billable";
		var options_id = fmt+"_options";
		var cb = mk_cb_update_visitor_options(i);
		$("#"+dob_year_id).on('change', cb);
		$("#"+dob_month_id).on('change', cb);
		$("#"+dob_day_id).on('change', cb);
		$("#"+billable_id).on('change', display_business_info);
		$("#"+billable_id).on('change', cb);
	}

	// and collapse the whole target if a nonzero number of tickets was selected
	if (val) {
		$("#tickets").collapse('show');
	} else {
		$("#tickets").collapse('hide');
	}

});

