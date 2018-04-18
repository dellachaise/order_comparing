$(document).ready(function(){
	$("form").submit(function(event) {
		event.preventDefault();
		const data = {
			data: $("#name").val(),
			metro_url: $("#metro_url").val(),
			fozzy_url: $("#fozzy_url").val(),
			novus_url: $("#novus_url").val(),
			ashan_url: $("#ashan_url").val()
		}
		$.post("http://127.0.0.1:8000/api/goods", data);
	});
});
