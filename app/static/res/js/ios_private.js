Dropzone.autoDiscover = false;
var myDropzone = new Dropzone("#ipa_file", { 
	url: "/ipa_post",
	maxFilesize: 1024,
	acceptedFiles: '.ipa',
	maxFiles: 5,
	success: function(d, data) {
		data = JSON.parse(data);
		if (data.success == 1) {
			//显示app信息
			$('#app_name').text(data.data.app_name);
			$('#version').text(data.data.version);
			$('#bundle_identifier').text(data.data.bundle_identifier);
			$('#target_os_version').text(data.data.target_os_version);
			$('#minimum_os_version').text(data.data.minimum_os_version);
			$('#app_name').text(data.data.app_name);
			//显示ipa的架构信息
			$('#app_arcs').text(data.data.arcs.join(', '))          
			//显示私有api信息
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