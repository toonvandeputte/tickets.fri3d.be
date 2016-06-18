var posts = undefined;
var times = undefined;
var sched = undefined;
var volunteers = undefined;
var choice = new Object();

var min_shifts = 2;

$(document).ready(function() {
	$.ajax({
		url : '/api/get_volunteering_data',
		success : function(data) {
			d = JSON.parse(data);
			posts = d.posts;
			times = d.times;
			sched = d.sched;
			volunteers = d.volunteers;
			for (var v in volunteers) {
				choice[v] = new Array();
			}
			volunteering_form_setup();
			recalc_totals();
		}
	});
});

function check_totals()
{

	for (var v in volunteers) {
		var target = '#counter_' + v;
		var count = choice[v].length;
		if (count < min_shifts) {
			return false;
		}
	}

	return true;

}

function recalc_totals()
{

	for (var v in volunteers) {
		var target = '#counter_' + v;
		var count = choice[v].length;
		var color = (count < min_shifts ? "red" : "green" );
		$(target).html('<font color="'+color+'">'+count+'</font>');
	}

}

function volunteer_choice(time_id, post_id, sched_id, person_id, previous_person_id)
{

	// check that this person may sign up for this schedule, reasons
	// why she/he shouldn't are;
	// 	- person already booked for this timeslot
	// 	- person overbooked

	console.log("entry time_id="+time_id + " post_id="+post_id+" sched_id="+sched_id+" person_id="+person_id+" previous_person_id="+previous_person_id);

	var timeslot_clash = false;
	var others_within_slot = new Array();

	// has this person already signed up for this shift?
	if (person_id != "none") {
		for (var c in choice[person_id]) {
			if (choice[person_id][c]['time_id'] == time_id) {
				console.log("clash");
				return false;
			}
		}
	}

	// if someone previously occupied this slot, boot that person out
	if (previous_person_id != undefined) {
		var previous = undefined;
		for (var c in choice[previous_person_id]) {
			if (choice[previous_person_id][c]['sched_id'] == sched_id) {
				previous = c;
			}
		}
		// don't want to splice midflight
		if (c) {
			choice[previous_person_id].splice(c, 1);
		}
	}

	if (person_id != "none") {
		choice[person_id].push({ 'time_id' : time_id, 'sched_id' : sched_id, 'post_id' : post_id });
	}

	return true;

}

function volunteering_form_setup() {

	var f = '';

	f += '<table class="table table-hover table-condensed">';
	f += '  <thead>';
	f += '    <tr>';
	f += '      <th>Shift</th>';
	for (var p in posts) {
		f += '        <th>' + posts[p] + '</th>';
	}
	f += '    </tr>';
	f += '  </thead>';
	f += '  <tbody>';
	for (var t in times) {
		f += '    <tr>';
		f += '      <td>' + times[t] + '</td>';
		for (var p in posts) {
			f += '      <td>';
			if (t in sched && p in sched[t] && sched[t][p]['people_needed'] > 0) {
				var s = sched[t][p];
				for (var i = 0; i < s['people_needed']; i++) {
					var name = t + '_' + p + '_' + s['shift_id'] + '_' + i;
					f += '      <select class="form-control" data-time="'+t+'" data-post="'+p+'" data-shift="'+s['shift_id']+'" data-slot="'+i+'" id="'+name+'">';
					f += '<option value="none"></option>';
					for (var v in volunteers) {
						f += '<option value="'+v+'">'+volunteers[v]+'</option>';
					}
					f += '      </select>';
				}
			} else {
				f += '      &nbsp;';
			}
			f += '      </td>';
		}
		f += '    </tr>';
	}
	f += '  </tbody>';
	f += '  </table>';

	$("#table_dest").html(f);

	for (var t in times) {
		for (var p in posts) {
			if (t in sched && p in sched[t] && sched[t][p]['people_needed'] > 0) {
				var s = sched[t][p];
				for (var i = 0; i < s['people_needed']; i++) {
					var name = t + '_' + p + '_' + s['shift_id'] + '_' + i;
					$("#"+name).on('change', function(src) {
						var person_id = $('#' + src.target.id + ' option:selected').val();
						var time_id = src.target.dataset.time;
						var post_id = src.target.dataset.post;
						var shift_id = src.target.dataset.shift;
						var slot_id = src.target.dataset.slot;
						var previous_person_id = $('#' + src.target.id).data('pre');
						if (volunteer_choice(time_id, post_id, shift_id, person_id, previous_person_id)) {
							$('#' + src.target.id).data('pre', person_id);
						} else {
							alert("Can't let you do that, Dave. Persoon heeft al een shift op dat tijdstip.");
							$('#' + src.target.id).val(previous_person_id);
						}
						recalc_totals();
					});
				}
			}
		}
	}

	$('#shift_formFOO').submit(function(e) {
		/*
		e.preventDefault();
		if (!check_totals()) {
			alert("Er zijn nog personen zonder "+min_shifts+" shiften, gelieve te verbeteren.");
			return;
		}
		*/
	   e.preventDefault();
		var posting = {};
		for (var c in choice) {
			posting[c] = choice[c]['shift_id'];
		}
		console.log(posting);
		$.post("api/set_volunteering_data", posting);
	});



}
