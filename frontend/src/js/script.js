$(document).ready(function(){
	$("form").submit(function(event) {
		event.preventDefault();
		const data = {
			name: $("#name").val(),
			metro: $("#metro_url").val(),
			fozzy: $("#fozzy_url").val(),
			novus: $("#novus_url").val(),
			auchan: $("#ashan_url").val()
		}
		$.post("http://localhost:8000/api/v1/goods/", data);
	});
});
