(function (win){
	var blog =  blog || {};
	var IMG_STORAGE = "img_storage";

	blog.init = function(){
		localStorage.setItem(IMG_STORAGE, '');
		if ( $("#blog_id").val().length === 0 ) {
			$("#blog_id").val(localStorage['blog_id']);
		}
		if ( $("#title").val().length === 0 ) {
			$("#title").val(localStorage['title']);
		}
		

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
		$('#upload').attr('disabled',true);
		$('#upload').val('发送中。。。');
		blog.search_img(true);
		editor.save(true, true);
		var filename = editor.settings.file.name;
		var markdown = editor.exportFile(filename,'text',true)
		var title = $("#title").val().trim();
		if (title.length * markdown.length > 0){
			$.post('/blog/edit/', {
					'blog_id': $("#blog_id").val(),
					'title': title,
					'markdown': markdown},
					function(ret, status){
						$("#blog_id").val(ret.data.blog_id);
						$('#upload').attr('disabled',false);
						$('#upload').val('submit');
						// localStorage.setItem('title', title);
						// localStorage.setItem('blog_id', ret.data.blog_id);
						// var storage = JSON.parse(editor._storage[editor._previewDraftLocation + 
						// 	editor.settings.localStorageName]);
						
						// storage[filename] = editor._defaultFileSchema();

						// editor._storage[editor._previewDraftLocation + editor.settings.localStorageName] = 
						// 	editor._storage[editor.settings.localStorageName] = 
						// 		JSON.stringify({filename: editor._defaultFileSchema()});
						// editor.open();
						// $("#title").val('');
						// $("#blog_id").val('');
						$("#message").show();
						setTimeout(function(){ $("#message").hide();}, 2000);
					},
					'json');
		}else{
			$('#upload').attr('disabled',false);
			$('#upload').val('submit');
			alert('数据不完整');
			return false;
		}

	};
	/**
	 * 遍历编辑框中的图片，将其发送到服务器上。
	 * @param {is_submit} 是否要提交文章了。意味着，如果是则需要将所有未完成上传的都上传一次，且ajax用同步的方式
	 * @return {type} [description]
	 */
	blog.search_img = function( is_submit ){
		var imgs = $('img', $(editor.editor));
		for (var img_index = 0; img_index < imgs.length; img_index++) {
			var img = $(imgs[img_index]);
			var src = img.attr('src');

			//非我的域名的图片都需要转换
			if (src.indexOf('http://gausszh') === 0 || src.indexOf('http://localhost') === 0){
				continue;
			}

			var img_sha1 = CryptoJS.SHA1(src).toString();//SHA256(base64_img);
			img.attr('class', img_sha1);
			var img_storage = blog.img_storage();
			//正在上传或者已将上传过的则不重复了
			if ( img_storage[img_sha1] !== undefined && !is_submit) {
				if ( img_storage[img_sha1].length > 0) {
					img.attr('src', img_storage[img_sha1]);
				}
				continue;
			}
			
			blog.set_img(img_sha1, '');
			var	form = new FormData();
			if (src.indexOf('http') === 0){
				form.append(img_sha1, src)
			} else {
		    	var img_type = src.slice(src.indexOf('data:') + 5,src.indexOf(';'))
				var base64_img = src.slice(src.indexOf('base64,') + 7);
				form.append(img_sha1, blog.str_to_blob(base64_img, img_type));
			}

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
				async: !is_submit,
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
	 * 复制粘贴图片，chrome
	 * @param  {event} e 
	 */
	blog.send_img = function(e){
		var clip =  e.originalEvent.clipboardData || e.clipboardData;
		if ( !/image/.test(clip.types[0])) {
			return true;
		}
		var items = clip.items;
		if ( items ) {
			var img_blob = items[0].getAsFile();
			var rd = new FileReader();
			rd.onload = function ( e ) {
				var base64_img = rd.result;
				editor.editorIframeDocument.execCommand("insertHTML",false,'<img src="' + base64_img + '">');
			}
			rd.readAsDataURL(img_blob);

			e.preventDefault();
		}
		// var	form = new FormData();

		// form.append(img_sha1, img_blob)

	}

  	$(editor.editor).bind('paste', blog.send_img);
	/**
	 * 将字符串装换为Blob类型
	 * @param  {string} str [需要被装换的字符串]
	 * @param  {string} type [生成的Blob数据的 类型,比如 image/png]
	 * @return {Blob}     [装换后的Blob 类型数据]
	 (*/
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

	blog.upload_temp_blog = function () {
		var imgs = blog.img_storage();
		var keys = Object.keys(imgs);
		for (var i = 0; i < keys.length; i++) {
			if ( imgs[keys[i]] == '' || imgs[keys[i]] == undefined ) {
				return false;
			}
		}
		var filename = editor.settings.file.name;
		var markdown = editor.exportFile(filename,'text',true)
		var md_sha1 = CryptoJS.SHA1(markdown).toString();
		if (localStorage.markdown === undefined) {
			localStorage.markdown = md_sha1;
		}
		if ( localStorage.markdown === md_sha1) {
			return false;
		}
		localStorage.markdown = md_sha1;
		var title = $("#title").val().trim();
		if (title.length * markdown.length > 0){
			$.post('/blog/edit/', {
					'blog_id': $("#blog_id").val(),
					'title': title,
					'markdown': markdown},
					function(ret, status){
						$("#blog_id").val(ret.data.blog_id);
						$('#upload').attr('disabled',false);
						$('#upload').val('submit');
					},
					'json');
		}
	}
	//定期扫描编辑区的图片
	window.setInterval(blog.search_img, editor.settings.file.autoSave);
	//定期将编辑的内容保存到服务器草稿中
	window.setInterval(blog.upload_temp_blog, editor.settings.file.autoSave);
	window.blog = blog;

})(window)