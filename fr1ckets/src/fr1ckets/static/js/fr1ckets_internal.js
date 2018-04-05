$(document).ready(function() {
	if (document.getElementById('chart_timeline')) {
		load_chart_chartjs();
	}
});

// =============================================================
// overview page
// =============================================================

function newDate(d) {
	return moment().add(d,'d').toDate();
}

function load_chart_chartjs() {
	$.ajax({
		url : 'api/get_timeline_tickets',
		success : function(data) {
			data = JSON.parse(data);
			for (var i = 0; i < data.at.length; i++) {
				data.at[i] = new Date(data.at[i] * 1000);
			}

			var timeFormat = 'YYYYMMDD';
			var config = {
				type : 'line',
				data : {
					labels: data.at,
					datasets: [
						{
							label: "tickets sold",
							data: data.n,
						},
					],
				},
				options : {
					scales : {
						xAxes : [
							{
								type : "time",
								time : {
									format : timeFormat,
								},
							},
						],
					},
				},
			};
			ctx = $("#chart_timeline").get(0).getContext("2d");
			var chart_timeline = new Chart(ctx, config);
		},
		error : function(data) {
		},
	});
}

// =============================================================
// payments page
// =============================================================

function purchase_mark_paid(id, email, code) {
	var val = $('#switch_paid_'+id).prop('checked') ? 1 : 0;
	if (val && !window.confirm("Echt bestelling "+id+" (email "+email+" code "+code+") als betaald markeren? We sturen automatisch een email!")) {
		$('#switch_paid_'+id).prop('checked', false);
		return;
	}
	if (!val && !window.confirm("Echt bestelling "+id+" (email "+email+" code "+code+") als NIET betaald markeren? We hebben deze mens al een mail gestuurd!")) {
		$('#switch_paid_'+id).prop('checked', true);
		return;
	}
	$.ajax({
		url: "/admin/api/purchase_mark_paid/" + id + '/' + val,
		success: function(data) {
			$('#mark_paid_' + id).html("great!");
			$('#remove_' + id).html("great!");
			window.location.reload(true);
		},
		error: function(data) {
			$('#mark_paid_' + id).html('FAILED!');
		},
	});
}
function purchase_mark_removed(id, email, code) {
	var val = $('#switch_removed_'+id).prop('checked') ? 1 : 0;
	if (val && !window.confirm("Echt bestelling "+id+" (email "+email+" code "+code+") als verwijderd markeren? We sturen automatisch een email!")) {
		$('#switch_removed_'+id).prop('checked', false);
		return;
	}
	if (!val && !window.confirm("Echt bestelling "+id+" (email "+email+" code "+code+") als NIET verwijderd markeren? We hebben deze mens al een mail gestuurd!")) {
		$('#switch_removed_'+id).prop('checked', true);
		return;
	}
	$.ajax({
		url: "/admin/api/purchase_mark_removed/" + id + '/' + val,
		success: function(data) {
			$('#remove_' + id).html("great!");
			window.location.reload(true);
		},
		error: function(data) {
			$('#remove_' + id).html('FAILED!');
		},
	});
}
function purchase_mark_billed(id, email, code) {
	var val = $('#switch_billed_'+id).prop('checked') ? 1 : 0;
	if (val && !window.confirm("Echt bestelling "+id+" (email "+email+" code "+code+") als gefactureerd markeren?!")) {
		$('#switch_billed_'+id).prop('checked', false);
		return;
	}
	if (!val && !window.confirm("Echt bestelling "+id+" (email "+email+" code "+code+") als NIET gefactureerd markeren?!")) {
		$('#switch_billed_'+id).prop('checked', true);
		return;
	}
	$.ajax({
		url: "/admin/api/purchase_mark_billed/" + id + '/' + val,
		success: function(data) {
			$('#remove_' + id).html("great!");
			window.location.reload(true);
		},
		error: function(data) {
			$('#remove_' + id).html('FAILED!');
		},
	});
}
function purchase_mark_dequeued(id) {
	$.ajax({
		url: "/admin/api/purchase_mark_dequeued/" + id,
		success: function(data) {
			$('#remove_' + id).html("great!");
			window.location.reload(true);
		},
		error: function(data) {
			$('#remove_' + id).html('FAILED!');
		},
	});
}
