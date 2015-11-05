Dropzone.autoDiscover = false;
var myDropzone = new Dropzone("#ipa_file", { 
	url: "/ipa_post",
	maxFilesize: 1024,
	acceptedFiles: '.ipa',
	maxFiles: 1,
	success: function(d, data) {
		console.log(data);
	}
});