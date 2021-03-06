function api_call(path, data, callback) {
	$.ajax({
		"dataType": "json",
		"url": "/api/" + path + ".json",
		"data": data
	}).done(function(data) {
		$("#debug").text("{0}: {1} ({2})".format(path, data["status"], data["message"] || ''));
		callback(data);
	});
}

function update_state() {
	api_call(
		"state", {},
		function(data) {
			var text = "<table>";
			$.each(data.repos, function(i1, repo) {
				var done_bytes = 0;
				var missing_bytes = 0;
				$.each(repo.files, function(i2, file) {
					$.each(file.versions[file.versions.length - 1].chunks, function(i3, chunk) {
						if(chunk.saved) {
							done_bytes += chunk.length;
						}
						else {
							missing_bytes += chunk.length;
						}
					});
				});
				text = text + "<tr>" +
					"<td>"+
						"{0} ({1})".format(repo.name, repo.type) +
						"<br><small>{0}</small>".format(repo.root) +
						"<br><small>{0}</small>".format(repo.uuid) +
					"</td>" +
					"<td>" +
						"{0}%".format((100 * done_bytes) / (done_bytes + missing_bytes)) +
					"</td>" +
					"<td>" +
						"<a href='javascript: remove(\"{0}\");'>Remove</a>".format(repo.uuid) +
						"<br><a href='/download/{0}/{1}.chunker'>Get Chunkfile</a>".format(repo.uuid, repo.name) +
					"</td>" +
				"</tr>";
			});
			text = text + "</table>";
			$("#state").html(text);
		}
	);
}

function remove(uuid) {
	api_call(
		"remove", {"uuid": uuid},
		function(data) {
			// update_state();
		}
	);
}

function show_form(name) {
	$(".form").hide();
	$(".form."+name).show();
}

function random_key(box_id) {
	function random_string(length) {
		var chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
		var result = '';
		for (var i = length; i > 0; --i) result += chars[Math.round(Math.random() * (chars.length - 1))];
		return result;
	}
	$(box_id).val(random_string(128));
}

$(function() {

	$(".form").hide();
	update_state();
	setInterval(update_state, 10*1000);

});
