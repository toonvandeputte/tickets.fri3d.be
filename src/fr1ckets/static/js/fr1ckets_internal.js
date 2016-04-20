$(document).ready(function() {
	load_chart_chartjs();
});

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
