Dropzone.autoDiscover = false;
var myDropzone = new Dropzone("#ipa_file", { 
	url: "/ipa_post",
	maxFilesize: 1024,
	acceptedFiles: '.ipa',
	maxFiles: 1,
	success: function(d, data) {
		data = JSON.parse(data);
		if (data.success == 1) {
			$('#api_in_app div.api_section').remove();
			for (var i = 0; i < data.data.methods_in_app.length; i++) {
				var api = data.data.methods_in_app[i];
				var html = '<div class="api_section section__text mdl-cell mdl-cell--10-col-desktop mdl-cell--6-col-tablet mdl-cell--3-col-phone">' + 
                  '<h5>' + (i + 1) + '、' + api.api_name + '</h5>' + 
                  'api is ' + api.type + ', IN sdk ' + api.sdk + '、' + api.framework + ' -> ' + api.header_file + ' -> ' + api.class_name + ' -> '+ api.api_name + 
                '</div>';
                $('#api_append_div').append(html);
			};
			$('#framework_in_app div.api_section').remove();
			for (var i = 0; i < data.data.private_framework.length; i++) {
				var framework = data.data.private_framework[i];
				var html = '<div class="api_section section__text mdl-cell mdl-cell--10-col-desktop mdl-cell--6-col-tablet mdl-cell--3-col-phone">' + 
                  '<h5>' + (i + 1) + '、' + framework + '</h5>' + 
                '</div>';
                $('#framework_append_div').append(html);
			};
		}
		else {
			alert(data.data);
		}
	}
});