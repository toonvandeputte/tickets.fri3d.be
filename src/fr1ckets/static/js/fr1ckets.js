$(document).ready(function() {
	$('select').material_select();
});

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
