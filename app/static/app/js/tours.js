$(function() {
	$('.datepicker').datetimepicker({
		ampm: true,
		dateFormat: 'mm/dd/yy',
		timeFormat: 'hh:mm tt',
		stepMinute: 5
	});

	$('.timepicker').timepicker({
		ampm: true,
		timeFormat: 'hh:mm tt',
		stepMinute: 5
	});
	$('#add_inactive_semester_btn').click(function(){
		var year = $('#add_inactive_semester_btn').data('year');
		var num = $('#inactive-semesters-table tbody tr.editable').length;
		$('#inactive-semesters-table tbody').append('<tr class="editable"><td><select class="form-control" name="num_' + num + '_semester"><option>--Select--<option value="fall">Fall</option><option value="spring">Spring</option></select></td><td><input class="form-control" name="num_' + num + '_year" type="text" value="' + year + '" /></td></tr>');
	});
});