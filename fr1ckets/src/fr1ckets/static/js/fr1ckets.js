var products = [];
var vouchers = {}
const VOUCHERS_MAX = 10;
const VOUCHER_LEN = 10;

$('.no_js_warning').hide();

function vouchers_add(voucher)
{

	vouchers[voucher.code] = voucher;

}

function vouchers_reset()
{

	vouchers = {}

}

function vouchers_discount()
{

	var discount = 0;

	for (var code in vouchers) {
		discount += vouchers[code].discount;
	}

	return discount;

}

function vouchers_present()
{

	return Object.keys(vouchers).length > 0;

}

$('#overview_order').on('click', function() {
	var root = location.protocol + '//' + location.hostname;
	if (location.port) {
		root += ':' + location.port;
	}

	function order_inflight(b) {
		$('#overview_order').prop('disabled', b);
		$('#overview_cancel').prop('disabled', b);
		if (b) {
			$('#overview_spinner').removeClass('hidden');
		} else {
			$('#overview_spinner').addClass('hidden');
		}
	}

	order_inflight(true);

	$.ajax({
		url : root + '/api/tickets_register',
		type : 'post',
		dataType : 'json',
		data : $('form#ticket_form').serialize(),
		success : function(resp) {
			if (resp.status == 'SUCCESS') {
				if (resp.redirect) {
					window.location.href = resp.redirect;
				}
			} else if (resp.status == 'FAIL') {
				if (resp.message) {
					$('#outcome_content').text(resp.message);
					$('#outcome_modal').modal('show');
				}
			}
			order_inflight(false);
		},
		error : function(resp) {
			order_inflight(false);
			$('#outcome_content').text("Er is een fout opgetreden, waarschijnlijk overbelasting. Probeer het nog eens.");
			$('#outcome_modal').modal('show');
		},
		statusCode : {
			502 : function() {
				order_inflight(false);
				$('#outcome_content').text("Er is een fout opgetreden, waarschijnlijk overbelasting. Probeer het nog eens.");
				$('#outcome_modal').modal('show');
			},
		},
	});
});

function is_safari() {
	return navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1;
}
$('#ticket_form').submit(function(e) {
	e.preventDefault();

	errors = validate_choices();
	if (errors.length > 0) {
		var f = '<p>Er zijn nog enkele onvolledigheden in de ingave, gelieve deze te corrigeren:</p>';
		f += '<ul>';
		for (var e in errors) {
			f += '<li>'+errors[e]+'</li>';
		}
		f += '</ul>'
		$('#validation_content').html(f);
		$('#validation_modal').modal('show');
		return;
	}

	$('#overview_content').html(update_overview());
	$('#overview_modal').modal('show');
});
$('#show_tshirt_sizes_k').on('click', function(e) {
	e.preventDefault();
	$('#tshirt_sizes').attr('src', '/static/img/maattabel_k.png');
	$('#sizes_modal').modal('show');
});
$('#show_tshirt_sizes_f').on('click', function(e) {
	e.preventDefault();
	$('#tshirt_sizes').attr('src', '/static/img/maattabel_f.png');
	$('#sizes_modal').modal('show');
});
$('#show_tshirt_sizes_m').on('click', function(e) {
	e.preventDefault();
	$('#tshirt_sizes').attr('src', '/static/img/maattabel_m.png');
	$('#sizes_modal').modal('show');
});
function update_overview() {

	var choices = enumerate_choices();
	var f = '';

	f += '<table class="table">';
	f += '  <thead>';
	f += '    <tr>';
	f += '      <th>Wat</th>';
	f += '      <th>Eenheidsprijs</th>';
	f += '      <th>Hoeveel</th>';
	f += '      <th>Totale prijs</th>';
	f += '    </tr>';
	f += '  </thead>';
	f += '  <tbody>';
	for (var i = 0; i < choices.length; i++) {
		f += '    <tr>';
		f += '      <td>'+choices[i].name+'</td>';
		f += '      <td>€'+choices[i].price+'</td>';
		f += '      <td>'+choices[i].n+'</td>';
		f += '      <td>€'+(choices[i].price*choices[i].n)+'</td>';
		f += '    </tr>';
	}
	//if (vouchers_present()) {
	for (var code in vouchers) {
		var v = vouchers[code];
		f += '    <tr class="success">';
		f += '      <td>Voucher '+v.reason+'</td>';
		f += '      <td>-€'+v.discount+'</td>';
		f += '      <td></td>';
		f += '      <td>-€'+v.discount+'</td>';
		f += '    </tr>';
	}
	f += '    <tr>';
	f += '      <td><strong>Totaal</strong></td>';
	f += '      <td></td>';
	f += '      <td></td>';
	f += '      <td><strong>€'+calculate_total()+'</strong></td>';
	f += '    </tr>';
	f += '  </tbody>';
	f += '</table>';
	if (get_n_tickets() == 0) {
		f += '<div class="alert alert-warning" role="alert">';
		f += '  <p>';
		f += '    Je hebt geen tickets besteld, als je in een andere order nog tickets bestelt leggen we alles klaar voor je op het kamp, anders kan je deze bestelling afhalen op de Open Garage te Borsbeek.</p>';
		f += '  </p>';
		f += '</div>';
	}

	return f;

}

function handle_voucher(i, data) {

	console.dir("handle_voucher(i="+i+" data="+data+")");

	var voucher = JSON.parse(data);
	var f = '';

	if (voucher.code == 'none') {
		$('.form-group-voucher_code_'+i).addClass("badvoucher");
		f += '  <div class="voucher-alert alert alert-danger text-center" role="alert">';
		f += '    <p>Deze voucher is niet (meer) geldig.</p>';
		f += '  </div>';
		f += '</div>';
	} else if (voucher.discount > 0) {
		$('.form-group-voucher_code_'+i).addClass("goodvoucher");
		f += '<div class="row">';
		f += '  <div class="voucher-alert alert alert-success text-center" role="alert">';
		if (voucher.reason.length > 0) {
			f += '    <p>Met deze voucher krijg je éénmalig €'+voucher.discount+' korting! Reden: "'+voucher.reason+'"</p>';
		} else {
			f += '    <p>Met deze voucher krijg je éénmalig €'+voucher.discount+' korting!</p>';
		}
		f += '  </div>';
	} else if (available) {
		$('.form-group-voucher_code_'+i).removeClass("badvoucher");
		$('.form-group-voucher_code_'+i).removeClass("goodvoucher");
		f = '';
	}

	if (voucher.code != 'none') {
		vouchers_add(voucher);
		update_price_total_display();
	}

	$("#voucher_"+i+"_message_collapse").html(f);

}

function handle_reservation(data) {

	var reservation = JSON.parse(data);
	var available = Date.now() >= (reservation.available_from*1000);
	var f = '';

	if (!available) {
		var s = moment(reservation.available_from*1000).format('YYYY-MM-DD HH:mm:ss');
		f += '<div class="row">';
		f += '  <div class="alert alert-danger text-center" role="alert">';
		f += '    <p>Met dit email-adres kan je pas vanaf '+s+' bestellen! Je kan het formulier tot 24 uur op voorhand invullen. Als je vermoedt dat je een reservatie op een ander email-adres hebt, gelieve ons te <a href="mailto:tickets@fri3d.be">mailen</a>.</p>';
		f += '  </div>';
		f += '</div>';
	} else if (!reservation.is_default) {
		f += '<div class="row">';
		f += '  <div class="alert alert-success text-center" role="alert">';
		f += '    <p>Reservatie gevonden! Let op, deze reservatie is slechts goed voor één bestelling. Eens de publieke verkoop start kan je natuurlijk bijbestellen.</p>';
		f += '  </div>';
		f += '</div>';
	}

	$("#reservation_message_collapse").html(f);

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
	return ticket;

}

function get_n_tickets() {
	return parseInt($('#n_tickets').val());
}

function validate_choices() {
	var errors = []

	// alert("validity="+$('#ticket_form')[0].checkValidity());
	var n_tickets = parseInt($('#n_tickets').val());
	var need_business_info = false;

	if ($('#email').val().length == 0) {
		errors.push("Email-adres");
	}
	for (var i = 0; i < n_tickets; i++) {
		var src = 'tickets_'+i;
		var year_src = src + '_dob_year';
		var month_src = src + '_dob_month';
		var day_src = src + '_dob_day';
		var name_src = src + '_name';
		var billable_src = src + "_billable";
		var now = new Date();

		var dob_year = parseInt($('#'+year_src).val());
		var dob_month = parseInt($('#'+month_src).val());
		var dob_day = parseInt($('#'+day_src).val());
		var name = $('#' + name_src).val();
		var billable = Boolean($('#'+billable_src).prop('checked'));

		if (!dob_year || ((dob_year < 1900) || (dob_year > now.getFullYear()))) {
			errors.push("Geboortejaar ticket "+(i+1));
		}
		if (!dob_month || (dob_month < 1) || (dob_month > 12)) {
			errors.push("Geboortemaand ticket "+(i+1));
		}
		if (!dob_day || (dob_day < 1) || (dob_day > 31)) {
			errors.push("Geboortedag ticket "+(i+1));
		}
		if (name.length == 0) {
			errors.push("Naam ticket "+(i+1));
		}
		if (billable) {
			need_business_info = true;
		}
	}
	if (need_business_info) {
		var business_name = $('#business_name').val();
		var business_address = $('#business_address').val();
		var business_vat = $('#business_address').val();

		if ((business_name.length == 0) || (business_address.length == 0) || (business_vat.length == 0)) {
			errors.push("Bedrijfs-informatie");
		}
	}

	if (!$('#terms_payment').prop('checked') || !$('#terms_supervision').prop('checked') || !$('#terms_excellent').prop('checked')) {
		errors.push("Termen en condities");
	}
	return errors

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
		var not_volunteering_src = src + "_options_not_volunteering_during";
		var cleanup_src = src + "_options_volunteers_after";
		var billable_src = src + "_billable";

		var dob = new Date($('#'+year_src).val(), $('#'+month_src).val(), $('#'+day_src).val()).getTime();
		var billable = Boolean($('#'+billable_src).prop('checked'));
		var ticket = find_ticket_by_dob(dob, billable);
		if (!ticket)
			continue;
		var name = $('#' + name_src).val();
		var volunteering_during = !Boolean($('#'+not_volunteering_src).prop('checked'))
		var volunteering_after = Boolean($('#'+cleanup_src).prop('checked'));
		var ticket_price = ticket.volunteering_price;
		var ticket_name = ticket.display + " voor " + name;
		var can_volunteer = Boolean(dob < ticket_volunteering_cutoff);
		if (can_volunteer && !billable && !volunteering_during) {
			ticket_price = ticket.price;
			ticket_name = ticket_name + " (premium)";
		}
		var c = {
			n : 1,
			price : ticket_price,
			name : ticket_name,
		}
		choices.push(c);
	}

	return choices;

}

function calculate_total() {

	var choices = enumerate_choices();
	var total = 0;

	for (var i = 0; i < choices.length; i++) {
		console.dir(choices[i]);
		total += choices[i].n * choices[i].price;
	}

	total = Math.max(0, total - vouchers_discount());

	return total;

}

function update_price_total_display() {

	$("#price_total").html('€'+calculate_total());

}

function showhide_vouchers() {
	for (var i = 0; i < VOUCHERS_MAX; i++) {
		nextfield = i+1;
		console.log("voucher "+i+": contents="+$('#voucher_code_'+i).val());
		if ( !$('#voucher_code_'+i).val() ) {
			console.log('hide next empty field');
			if (!$('.form-group-voucher_code_'+nextfield+' input.form-control').val()) {
				$('.form-group-voucher_code_'+nextfield).removeClass("showfield");
			}
		} else {
			console.log('show next empty field');
			$('.form-group-voucher_code_'+nextfield).addClass("showfield");
		}
	}
}

function update_voucher(i) {
	var code = $('#voucher_code_'+i).val() ? $('#voucher_code_'+i).val() : 'unknown';
	$.ajax({
		url : 'api/get_voucher/' + code,
		success: function(data) {
			handle_voucher(i, data);
		},
		error: function(data) {
			handle_voucher(i, data);
		},
	});

}

$(document).ready(function() {
	$.ajax({
		url : '/api/get_products',
		success: function(data) {
			products = JSON.parse(data);
			for (var i in products) {
				if (products[i].max_dob) {
					products[i].max_dob *= 1000;
				}
				$('#'+products[i].name).on('change', update_price_total_display);
			}
		},
	});
	$('#email').on('change', function() {
		var email = $('#email').val();
		if (email.length > 0) {
			$.ajax({
				url : 'api/get_reservation/'+email,
				success : function(data) {
					handle_reservation(data);
				},
				error : function(data) {
					handle_reservation(data);
				},
			});
		} else {
			handle_reservation('');
		}
	});
	$('#have_voucher').on('change', function() {
		var have = $('#have_voucher').prop('checked');
		var f = '';
		if (have) {
			for (var i = 0; i < VOUCHERS_MAX; i++) {
				f += '<div class="form-group form-group-voucher_code form-group-voucher_code_'+i+'"><div class="row">';
				f += '  <label for="voucher_code_'+i+'" class="control-label col-sm-3 col-sm-offset-1">Voucher</label>';
				f += '  <div class="col-sm-8">';
				f += '    <input class="form-control" id="voucher_code_'+i+'" name="voucher_code_'+i+'" type=text>';
				f += '  </div></div>';
				f += '<div class="row"><div class="col-sm-offset-4 col-sm-8 collapsible" id="voucher_'+i+'_message_collapse">';
				f += '  </div></div>';
				f += '</div>';
			}
		} else {
			vouchers_reset();
		}
		$('#voucher').html(f);

		if (have) {
			$("#voucher").collapse('show');
		} else {
			$("#voucher").collapse('hide');
		}

		for (var i = 0; i < VOUCHERS_MAX; i++) {
			(function(i) {
				$('#voucher_code_'+i).on('change keyup paste', function() {
					showhide_vouchers();
					if ($('#voucher_code_'+i).val().length == VOUCHER_LEN) {
						update_voucher(i);
					}
				});
				$('#voucher_code_'+i).on('focusout', function() {
					if ($('#voucher_code_'+i).val().length) {
						update_voucher(i);
					}
				});
			})(i);
		}
	});

	$('#n_tickets').on('change', update_price_total_display);
	update_price_total_display();

});

var ticket_volunteering_cutoff = new Date(2000, 8, 13).getTime();

var showing_business_info = false;
function display_business_info() {

	var n_tickets = parseInt($('#n_tickets').val());
	var n_tickets_billable = 0;

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
		var ef = '';
		// this part needs to be shown for every ticket
		if (ticket) {
			f += '<div class="row ticketinfo" >';
			f += '  <div class="col-sm-6 col-sm-offset-4 ticketname">';
			f += '    <p id="'+ticket_name_id+'"><i class="glyphicon glyphicon-ok"></i> '+ticket.display+'</p>';
			f += '  </div>';
			f += '  <div class="col-sm-2 text-right ticketprice">';
			f += '    <p id="'+ticket_price_id+'">€'+ticket.volunteering_price+'</p>';
			f += '  </div>';
			f += '</div>';
			f += '<div class="form-group">';
			f += '  <div class="checkbox col-sm-offset-4 col-sm-4 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+vegitarian_id+'" name="'+vegitarian_id+'">';
			f += '      Vegetarisch';
			f += '    </label>';
			f += '  </div>';
		} else {
			f += '<div class="row">';
			f += '  <div class="col-sm-8 col-sm-offset-4">';
			f += '    <p>Ongeldige datum!</p>';
			f += '  </div>';
			f += '</div>';
		}
		if (ticket && can_volunteer) {
			var volunteering_id = fmt + "_options_not_volunteering_during";
			var cleanup_id = fmt + "_options_volunteers_after";
			var buildup_id = fmt + "_options_volunteers_before";
			f += '  <div class="checkbox col-sm-4 col-xs-6">';
			f += '    <label>';
			if (billable) {
				ef = 'checked="checked"';
			}
			f += '      <input type="checkbox" id="'+volunteering_id+'" name="'+volunteering_id+'" '+ef+' data-toggle="popover" data-placement="top" data-trigger="focus" data-content="Om het kamp te doen lukken, hopen we dat iedereen vanaf 16 jaar minstens één volunteer-shift van een drietal uurtjes kan bijdragen. Als dit niet voor je lukt, kan je dit aanvinken, je betaalt dan wel iets meer.">';
			f += '      Kan géén vrijwilligers-shift doen (<i>premium</i>).';
			f += '    </label>';
			f += '  </div>';
			f += '  <div class="checkbox col-sm-offset-4 col-sm-4 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+buildup_id+'" name="'+buildup_id+'" data-toggle="popover" data-placement="top" data-trigger="focus" data-content="We zoeken mensen die vanaf donderdag graag mee het kamp komen opbouwen. Good karma!">';
			f += '      Helpt mee opbouwen voor het kamp.';
			f += '    </label>';
			f += '  </div>';
			f += '  <div class="checkbox col-sm-4 col-xs-6">';
			f += '    <label>';
			f += '      <input type="checkbox" id="'+cleanup_id+'" name="'+cleanup_id+'" data-toggle="popover" data-placement="top" data-trigger="focus" data-content="We zoeken een twintigtal mensen die graag een nachtje langer bijven kamperen en op dinsdag 21 augustus 2018 helpen opruimen. Good karma!">';
			f += '      Helpt opkuisen op 21 augustus';
			f += '    </label>';
			f += '  </div>';
		}
		f += '</div>';
		// throw it into the DOM so we can add events to it
		$('#'+options_id).html(f);
		$('[data-toggle="popover"]').popover();
		if (can_volunteer) {
			if (!billable) {
				var volunteering_id = fmt + "_options_not_volunteering_during";
				var cleanup_id = fmt + "_options_volunteers_after";
				$('#'+volunteering_id).on('change', function() {
					var display_name = '';
					var display_price = 0;
					var is_not_volunteering = Boolean(this.checked);
					if (is_not_volunteering) {
						display_name = ticket.display + ' (premium)';
						display_price = ticket.price;
					} else {
						display_name = ticket.display;
						display_price = ticket.volunteering_price;
					}
					$('#'+ticket_name_id).text(display_name);
					$('#'+ticket_price_id).text('€'+display_price);
					update_price_total_display();
				});
			}
		}

		// and collapse it
		$('#'+options_id).collapse('show');

		// update main total
		update_price_total_display();

	}
}

$('#n_tickets').on('change', display_business_info);
$('#n_tickets').on('change', function() {
	var val = parseInt($("#n_tickets").val());
	var f = "";

	f += '<div class="row text-center">';
	f += '  <p><h4>Jouw tickets:</h4></p>';
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
		f += '   <input id="'+dob_year_id+'" name="'+dob_year_id+'" class="form-control col-sm-2" type="tel" maxlength="4" pattern="(19|20|21)[0-9]{2}" required aria-required="true" placeholder="YYYY">';
		f += '  </div>';
		f += '  <div class="col-sm-2">';
		f += '   <input id="'+dob_month_id+'" name="'+dob_month_id+'" class="form-control col-sm-1" type="tel" maxlength="2" pattern="^(1[0-2]|0?[1-9])$" required aria-required="true" placeholder="MM">';
		f += '  </div>';
		f += '  <div class="col-sm-2">';
		f += '   <input id="'+dob_day_id+'" name="'+dob_day_id+'" class="form-control col-sm-1" type="tel" maxlength="2" pattern="^(3[01]|[12][0-9]|0?[1-9])$" required aria-required="true" placeholder="DD">';
		f += '  </div>';
		f += '</div>';
		// bill box
		f += '<div class="form-group">';
		f += '  <div class="checkbox col-sm-8 col-sm-offset-4">';
		f += '    <label><input type="checkbox" id="'+billable_id+'" name="'+billable_id+'" data-toggle="popover" data-placement="top" data-trigger="focus" data-content="Je kiest ervoor om dit ticket te laten factureren. We nemen hiervoor zo snel mogelijk contact op."> Ticket met factuur (altijd €317 inclusief BTW)</label>'
		f += '  </div>';
		f += '</div>';
		// collapse for options depending on input above
		f += '<div class="collapsible" id="'+options_id+'">';
		f += '</div>';
	}
	f += '<hr/>';

	f += '<div class="form-group">';
	f += '  <div class="row">';
	f += '  <label for="transportation" class="col-xs-12 col-sm-4 control-label">Vervoer</label>';
	f += '  <div class="col-xs-12 col-sm-6">';
	f += '    <select id="transportation" name="transportation" class="form-control">';
	f += '      <option value="UNSURE">nog niet zeker</option>';
	f += '      <option value="CAR">wagen</option>';
	f += '      <option value="CAMPERVAN">een kampeerwagen (camper of caravan)</option>';
	f += '      <option value="PUBLIC">openbaar vervoer</option>';
	f += '      <option value="CARPOOL">carpooling</option>';
	f += '    </select>';
	f += '  </div>';
	f += '  </div>';
	f += '  <div class="row">';
	f += '  <div class="col-sm-5 col-sm-offset-4">';
	f += '  	<p>Dit heeft geen impact op de ticketprijs, maar zo weten we ongeveer hoeveel parkeerplaatsen en plaatsen voor caravans en campers we moeten voorzien.</p>';
	f += '  </div>';
	f += '</div>';
	f += '</div>';

	f += '<hr/>';

	// push it into the DOM so we can hook event listeners on it
	$("#tickets").html(f);
	$('[data-toggle="popover"]').popover();

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

