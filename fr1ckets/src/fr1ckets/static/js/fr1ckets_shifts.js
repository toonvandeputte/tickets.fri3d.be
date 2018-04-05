var posts = undefined;
var times = undefined;
var sched = undefined;
var volunteers = undefined;
// choices = {
// 	person (by number) : [
// 		{
// 			'time' : time,
// 			'shift' : shift,
// 		}
// 	]
// }
var choices = new Object();
var nonce = undefined;

var min_shifts = 1;

$(document).ready(function() {
	var url = window.location.href;
	nonce = url.substr(url.lastIndexOf('/') + 1);
	$.ajax({
		url : '/api/get_volunteering_data/'+nonce,
		success : function(data) {
			d = JSON.parse(data);
			if (d.status == 'OK') {
				posts = d.posts;
				times = d.times;
				sched = d.sched;
				volunteers = d.volunteers;
				volunteer_choice_init();
				volunteer_totals_init();
				volunteer_totals_recalc();
				schedule_render();
				$('#email_entry_wrong').collapse('hide');
				$('#form_entry').collapse('show');
				$('#volunteer_info').collapse('show');
			} else if (d.status == 'FAIL') {
				$('#email_entry_wrong').collapse('show');
				$('#email_entry_wrong').html('<div class="alert alert-danger" role="alert">'+d.msg+'</div>');
			}
		}
	});
	$('.no_js_warning').hide();
	$('#global_info').collapse('show');
	$('#form_entry').collapse('hide');
});

// called when server hands us scheduling info which might contain previous
// choices, extract them
function volunteer_choice_init()
{

	// clear previous
	choices = new Object();

	// init choices
	for (var p_id in volunteers['mine']) {
		choices[volunteers['mine'][p_id]] = new Array();
	}

	// check if our people need choice updates
	for (var t in sched) {
		for (var p in sched[t]) {
			var s = sched[t][p];
			for (var p_id in s['people_list']) {
				// fancy smancy javascript, lofty ideas
				// but 90% is writing C loops and indexing
				var person = s['people_list'][p_id];
				if (volunteers['mine'].indexOf(person) >= 0) {
					volunteer_choice_make(t, s['shift_id'], person);
				}
			}
		}
	}

}

// user selected a volunteer in a slot somewhere, see if it's allowed
// and if the previous occupant needs to be booted
function volunteer_choice_make(time, shift, person, previous_person)
{

	console.log('volunteer_choice_make(time='+time+' shift='+shift+' person='+person+' previous_person='+previous_person+')');

	// check for timing clash for this person
	if (person != "none") {
		for (var c in choices[person]) {
			if (choices[person][c]['time'] == time) {
				// this person already has a shift at this time
				return false;
			}
		}
	}

	// check if we need to boot the previous out
	if (previous_person) {
		var found = undefined;
		for (var c in choices[previous_person]) {
			if (choices[previous_person][c]['shift'] == shift) {
				// found it
				found = c;
			}
		}
		// don't splice in flight
		if (found) {
			choices[previous_person].splice(found, 1);
		}
	}

	// save
	if (person != "none") {
		choices[person].push({ 'time' : time, 'shift' : shift });
	}

	return true;

}

// setup the per-volunteer count
function volunteer_totals_init()
{

	var f = '';
	var width = Math.max(12 / Object.keys(volunteers['mine']).length, 2);

	for (var v_id in volunteers['mine']) {
		var v = volunteers['mine'][v_id];
		var name = volunteers['all'][v]['name'];
		f += '<div class="col-xs-' + width + ' text-center">';
		f += '  <p>' + name + '</p>';
		f += '  <h2 id="counter_' + v + '"></h2>';
		f += '</div>';
	}

	$('#volunteer_list').html(f);

	f = '<p>Legende:</p>';
	f + '<ul>';
	for (var p in posts) {
		f += '<li><b>'+posts[p]['name']+'</b>: '+posts[p]['desc']+'</li>';
	}
	f += '</ul>';

	$('#volunteer_info').html(f);

}

// recalc and display volunteer totals
function volunteer_totals_recalc()
{

	for (var v_id in volunteers['mine']) {
		var v = volunteers['mine'][v_id];
		var target = '#counter_'+v;
		var color = (choices[v].length < min_shifts ? "red" : "green");
		$(target).html('<font color="'+color+'">'+choices[v].length+'</font>');
	}

}

// check that each volunteer has at least min_shifts
function volunteer_totals_check()
{

	for (var v_id in volunteers['mine']) {
		var v = volunteers['mine'][v_id];
		if (choices[v].length < min_shifts) {
			return false;
		}
	}

	return true;

}

// util, find a shift in the schedule
function schedule_find_shift(shift)
{

	for (var t in sched) {
		for (var p in sched[t]) {
			if (sched[t][p]['shift'] == shift) {
				return sched[t][p];
			}
		}
	}

	return undefined;

}

// write out the whole scheduling table
function schedule_render()
{

	var f = '';
	var select_count = 0;
	var selects = new Array();
	var fill_previous = new Object();
	var prev_day = undefined;

	f += '<table class="table table-hover table-condensed">';
	f += '  <tbody>';

	function header(day) {
		var fh = '';
		fh += '    <tr>';
		fh += '      <td><b><i>Dag '+day+'</i></b></td>';
		for (var p in posts) {
			fh += '        <td><b>' + posts[p]['name'] + '</b></td>';
		}
		fh += '    </tr>';
		return fh;
	}

	var times_names = new Array();
	for (var t in times) {
		times_names.push(times[t]['index']);
	}
	var cmp = function(a, b) {
		return a - b;
	}
	times_names.sort(cmp);

	for (var t_name in times_names) {
		var t = undefined;
		for (var t_find in times) {
			if (times_names[t_name] == times[t_find]['index']) {
				t = t_find;
			}
		}
		if (times[t]['day'] != prev_day) {
			f += header(times[t]['day']);
			prev_day = times[t]['day'];
		}

		f += '    <tr>';
		f += '      <td>' + times[t]['name'] + '</td>';
		for (var p in posts) {
			f += '      <td>';
			if (!(t in sched && p in sched[t])) {
				// no shifts at this time/post
				f += '        &nbsp;';
				continue;
			}
			var s = sched[t][p];

			// first display the people already signed up for this shift,
			// if they're ours we can show them in a select (the right person preselected)
			for (var person_id in s['people_list']) {
				var person = s['people_list'][person_id];
				if (volunteers['mine'].indexOf(person) >= 0) {
					// it's one of ours, figure out a unique id for the select and save it for callbacks
					var name = t + '_' + p + '_' + s['shift_id'] + '_' + select_count++;
					selects.push(name);

					// store the time/post/shift data in data fields so we can read them from the callbacks
					f += '<select class="form-control" data-time="'+t+'" data-post="'+p+'"';
					f += '  data-shift="'+s['shift_id']+'" id="'+name+'">';
					f += '    <option value="none"></option>';
					for (var my_person_id in volunteers['mine']) {
						var my_person = volunteers['mine'][my_person_id];
						var selected = '';
						if (my_person == person) {
							// preselect the correct person
							selected = 'selected data-pre="'+my_person+'"';
							// special item, we need to set the 'pre' datafield
							fill_previous[name] = my_person;
						}
						f += '    <option value="'+my_person+'" '+selected+'>'+volunteers['all'][my_person]['name']+'</option>';
					}
					f += '</select>';
				} else {
					// not one of ours, just show the person
					f += '<select class="form-control alert-success" disabled="disabled">';
					f += '  <option value="none" selected>' + (volunteers['all'][person]['name'] ? volunteers['all'][person]['name'] : 'John D') + '</option>';
					f += '</select>';
				}
			}

			// then display the rest of them
			for (var i = 0; i < (s['people_needed'] - s['people_list'].length); i++) {
				var name = t + '_' + p + '_' + s['shift_id'] + '_' + select_count++;
				selects.push(name);
				f += '<select class="form-control" data-time="'+t+'" data-post="'+p+'"';
				f += '  data-shift="'+s['shift_id']+'" id="'+name+'">';
				f += '    <option value="none" selected></option>';
				for (var my_person_id in volunteers['mine']) {
					var my_person = volunteers['mine'][my_person_id];
					f += '    <option value="'+my_person+'">'+volunteers['all'][my_person]['name']+'</option>';
				}
				f += '</select>';
			}
			f += '      </td>';
		}
		f += '    </tr>';
	}
	f += '  </tbody>';
	f += '  </table>';

	$('#table_dest').html(f);

	$('[disabled="disabled"]').css({ 'color' : '#3c763d', 'background-color' : '#dff0d8' });

	// some selects are pre-filled with specific persons, we need to
	// provide these in the 'pre' datafield, see below how it works
	for (var select in fill_previous) {
		$('#'+select).data('pre', fill_previous[select]);
	}

	// wire in callbacks for all the selects
	for (var s in selects) {
		var select = selects[s];
		$('#'+select).on('change', function(src) {
			var person = $('#' + src.target.id + ' option:selected').val();
			var time = src.target.dataset.time;
			var post = src.target.dataset.post;
			var shift = src.target.dataset.shift;
			// the 'pre' field contains the previous selected value, so we
			// can re-instate it when the new value is no good
			var previous_person = $('#' + src.target.id).data('pre');
			if (volunteer_choice_make(time, shift, person, previous_person)) {
				$('#' + src.target.id).data('pre', person);
				volunteer_totals_recalc();
			} else {
				alert('Deze persoon heeft al een shift op dit tijdsstip.');
				$('#' + src.target.id).val(previous_person);
			}
			console.log(src.target.id);
		});

	}

	$('#submit').on('click', function(e) {
		e.preventDefault();
		if (!volunteer_totals_check()) {
			alert('Niet al uw personen hebben minstens '+min_shifts+' shift, gelieve te verbeteren');
			return;
		}

		var payload = new Object();
		for (var c in choices) {
			if (!(c in payload)) {
				payload[c] = new Array();
			}
			for (var s in choices[c]) {
				payload[c].push(choices[c][s]['shift']);
			}
		}
		$.post('/api/set_volunteering_data/'+nonce, JSON.stringify(payload)).done(function(data) {
			var d = data;
			if (d.status == 'OK') {
				$('#confirm_modal').modal();
			} else {
				$('#error_modal').modal();
			}
		});


	});


}
