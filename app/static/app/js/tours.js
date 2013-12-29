$(function() {
	$('.datepicker').datetimepicker({
		ampm: true,
		dateFormat: 'mm/dd/yy',
		timeFormat: 'hh:mm tt z',
		stepMinute: 5
	});
});