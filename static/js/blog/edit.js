(function (win){
	var blog =  blog || {};
	var IMG_STORAGE = "img_storage";

	blog.init = function(){
		localStorage.setItem(IMG_STORAGE, '');

	};

	blog.img_storage = function(){
		var img_storage_str = localStorage.getItem(IMG_STORAGE);
		if (img_storage_str == undefined || img_storage_str.length < 1){
			return {}
		}
		return JSON.parse(img_storage_str);
	};

	blog.set_img = function(img_sha1, link){
		var img = blog.img_storage();
		img[img_sha1] = link;
		localStorage.setItem(IMG_STORAGE, JSON.stringify(img));
	}

	/**
	 * 发布文章,发布前要先发送图片，并将文章缓存到localStorage
	 * @param  {event} e 
	 */
	blog.submit = function(e){
		blog.send_img();
		editor.save(true, true);
		var filename = editor.settings.file.name;
		var storage = editor.getFiles()[filename];
		var markdown = storage.content.trim();
		var html = editor.exportFile(null, 'html', true).trim();
		var title = $("#title").val().trim();
		if (title.length * html.length * markdown.length > 0){
			$.post('/blog/edit/', {
					'blog_id': $("#blog_id").val(),
					'title': title,
					'html': html, 
					'markdown': markdown},
					function(ret, status){
						$("#blog_id").val(ret.data.blog_id);
						// storage['blog_id'] = ret.data.blog_id;
						// var storage = JSON.parse(editor._storage[editor._previewDraftLocation + 
						// 	editor.settings.localStorageName]);
						
						// storage[filename] = editor._defaultFileSchema();

						// editor._storage[editor._previewDraftLocation + editor.settings.localStorageName] = 
						// 	editor._storage[editor.settings.localStorageName] = JSON.stringify(storage);
						// editor.open();
						// $("#title").val('');
						// $("#blog_id").val('');
						alert('提交成功');
					},
					'json');
		}else{
			alert('数据不完整');
			return false;
		}

	};
	/**
	 * 遍历编辑框中的图片，将其发送到服务器上。但是只有图片的src字符超过1w时才有必要上传。
	 * 我觉得那种很小的图片就算了
	 * @return {[type]} [description]
	 */
	blog.send_img = function(){

		var markdown = editor.exportFile(null, 'text', null);

		var imgs = $('img', $(editor.editor));
		for (var img_index = 0; img_index < imgs.length; img_index++) {
			var img = $(imgs[img_index]);
			var src = img.attr('src');
			if (src.length < 10000 ){
				continue;
			}

			//只针对base64编码的图片才上传
			if (! src.startsWith('data')){
				continue;
			}

			var base64_img = src.slice(src.indexOf('base64,') + 7);
			var st = new Date;
			var img_sha1 = CryptoJS.SHA1(base64_img).toString();//SHA256(base64_img);
    		console.log('SHA256: ' + (new Date - st));
			img.attr('class', img_sha1);
			var img_storage = blog.img_storage();
			//正在上传或者已将上传过的则不重复了
			if ( img_storage[img_sha1] !== undefined ) {
				continue;
			}
			blog.set_img(img_sha1, '');
		    var img_type = src.slice(src.indexOf('data:') + 5,src.indexOf(';'))
			var blob_img = blog.str_to_blob(base64_img, img_type);
			var	form = new FormData();
			form.append(img_sha1, blob_img);

			// 提示用户，目前在上传哦
			img.hide();
			var progress_tag = document.createElement('p');
			progress_tag.className = img_sha1;
			$(progress_tag).insertAfter(img);
			var progress_f = function ( event ) {
				if (event.lengthComputable) {
					var percentComplete = event.loaded / event.total * 100;
					var klass = arguments.callee.klass;
					var progress_tag = $('p.' + klass, $(editor.editor));
					progress_tag.innerHTML = '正在上传....'+ percentComplete + '%'

				} 
			};
			progress_f.klass = img_sha1;

			$.ajax({
				url:'/blog/files/', 
				type:'POST',
				data:form,processData:false,
				contentType: false,
				context: progress_tag,
				xhrFields: {
					onprogress: progress_f
				},
				async: true,
				success: function(ret,status){
					if (ret.ok){
						progress_tag.innerHTML = '';
						for (var i = 0; i < ret.data.length; i++) {
							blog.set_img(ret.data[i].name, ret.data[i].link);
							var img = $('img.' + ret.data[i].name, $(editor.editor));
							img.attr('src', ret.data[i].link);
							img.show();
						};

					} else {
						progress_tag.innerHTML = '上传失败';
					}
				}

			});
		};
	};
	/**
	 * 将字符串装换为Blob类型
	 * @param  {string} str [需要被装换的字符串]
	 * @param  {string} type [生成的Blob数据的 类型,比如 image/png]
	 * @return {Blob}     [装换后的Blob 类型数据]
	 */
	blog.str_to_blob = function (str, type) {
		var	bin_str = atob(str);
		var	array = new Uint8Array(new ArrayBuffer(bin_str.length));
		for(var i = 0; i < bin_str.length; i++) {
			array[i] = bin_str.charCodeAt(i);
		}
		var	dv = new DataView(array.buffer);
		var	blob_file = new Blob([dv], {'type': type});

		return blob_file;

	}
	window.setInterval(blog.send_img, editor.settings.file.autoSave);
	window.blog = blog;

})(window)