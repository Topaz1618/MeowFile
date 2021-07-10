
    var page = 0;
    var limit = 5;
    var piclist = []
    var isLoading = false;
    var isEnd = false;

    window.onscroll = function () {
        if(isLoading || isEnd) return;
        var scrollTop = document.documentElement.scrollTop||document.body.scrollTop;
        var scrollHeight = $(document).height()
        var clientHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;

        if(scrollTop + clientHeight >= scrollHeight){
            if(document.getElementById("more")){
                loadMore();
            }else if(document.getElementById("usermore")){
                loadUserMore();
            }
        }
    }

    function loadMore() {
   		page = page + 1;
        isLoading = true;
       	$.ajax({
        url: '/api/media/collect/',
        type: 'GET',
        data: {start: page * limit, limit: limit},
        dataType: 'json',
        timeout: 10000,
        success: function(data) {
        	if (data['media'].length < limit) {
        	    isEnd = true;
        		$("#more").attr("class", "hidden");
        	}
            insertDivCollect(data);
        },
        error: function(){
            page = page - 1;
        },
        complete: function(){
            isLoading = false;
        }
       });
    }

    function loadUserMore() {
   		page = page + 1;
        isLoading = true;
       	$.ajax({
        url: '/api/media/list/',
        type: 'GET',
        data: {start: page * limit, limit:limit},
        dataType: 'json',
        timeout: 10000,
        success: function(data) {
        	if (data['media'].length < limit) {
        	    isEnd = true;
        		$("#usermore").attr("class", "hidden");
        	}

            insertDiv(data);
        },
        error: function(){
            page = page - 1;
        },
        complete: function(){
            isLoading = false;
        }
       });
    }

    $("#more").click(loadMore);

    $("#usermore").click(loadUserMore);

    function insertDiv(data){
		data = data['media']
        var temphtml = " ";
        var html01 = "<div class='col-xs-12 col-md-6' id='";
        var html02 = "'><a href='#' class='thumbnail'><img src='/";
        var html03 = "' onclick='zoomPic(this)' alt></a>";
		var html04 = "<div class='del' onclick='del("
		var html05 = ")'> <i class='fa fa-trash-o'></i></div></div>"

		for (var i = 0; i < data.length; i++) {
			temphtml = html01 + data[i]['id'] + html02 + data[i]['leftright'] + html03 + html04 + data[i]['id'] + html05;
        	$("#media").append(temphtml);
		}
        // for(var i =0; i < name.length; i++)
        //     temphtml += html01 + media_id[i] + html02+ file[i] + html03;
        //     $("#media").append(temphtml);
    }

    function insertDivCollect(data){
		data = data['media']
        var temphtml = " ";
        var html01 = "<div class='col-xs-12 col-md-6' id='";
        var html02 = "'><a href='#' class='thumbnail'><img src='/";
        var html03 = "' onclick='zoomPic(this)' alt></a></div>";

		for (var i = 0; i < data.length; i++) {
			temphtml = html01 + data[i]['id'] + html02 + data[i]['leftright'] + html03
        	$("#media").append(temphtml);
		}
        // for(var i =0; i < name.length; i++)
        //     temphtml += html01 + media_id[i] + html02+ file[i] + html03;
        //     $("#media").append(temphtml);
    }


    function down(id) {
    $.ajax({
        url: '../download/',
        type: 'POST',
        data: {media_id: id},
        dataType: 'json',
        timeout: 10000,
        success: function(data) {
            if(data){
                alert("开始下载");
            }
        }
       });
    }


    function del(id){
		var msg = "您真的确定要删除吗？";
		if (confirm(msg)==true){
		    $.ajax({
		    url: '/api/media/delete/',
		    type: 'GET',
		    data: {media_id: id},
		    dataType: 'json',
		    timeout: 10000,
		    success: function(data) {
		       	if(data){
		            $('#'+id).remove();
		        }
		    }
		   });
		}else {
		    return false;
		}
	}


	

    function zoomPic(pic){
    	requestFullscreen(document.documentElement);
    	$('.footer').attr("style","display:none");
    	
    	current_big_id = $(pic).attr('id');
    	zoomPicExec(current_big_id);

    }
    
    var current_big_id = -1;
    
     function fadeOut(val){
        exitFullscreen();
        $(val).fadeOut("fast");
        $('.footer').attr("style","");
        current_big_id = -1;
    }

	

    function zoomPicDisplay(pic, divid){
    	current_big_id = $(pic).attr('id');
    	
    	requestFullscreen(document.documentElement);
   
    	zoomPicExec(current_big_id);
		
        $('#outerdiv').click(function(){//再次点击淡出消失弹出层
            $(this).fadeOut("fast");
            document.documentElement.style.overflowY = 'scroll';
            
            parentdiv = document.getElementById(divid)
            parentdiv.scrollIntoView()
        });
    }
    
    function zoomPicExec(pic) {
    	var _this = $("#" + pic);
    	
        var src = _this.attr("src");//获取当前点击的media_img元素中的src属性
        $('#bigimg').attr("src", src);//设置#bigimg元素的src属性

		document.documentElement.style.overflowY = 'hidden';
            /*获取当前点击图片的真实大小，并显示弹出层及大图*/
        $("<img/>").attr("src", src).load(function(){
            //var windowW = $(window).width();//获取当前窗口宽度
            //var windowH = $(window).height();//获取当前窗口高度
            var windowW = window.screen.width;
            var windowH = window.screen.height;
            
            var realWidth = this.width;//获取图片真实宽度
            var realHeight = this.height;//获取图片真实高度
            var imgWidth, imgHeight;
            var scale = 1;//缩放尺寸，当图片真实宽度和高度大于窗口宽度和高度时进行缩放
            
            if(realWidth>windowW*scale) {//判断图片宽度
                imgWidth = windowW*scale;//如大于窗口宽度，图片宽度进行缩放
                imgHeight = imgWidth*realHeight/realWidth;//等比例缩放高度
        
                if(imgHeight > windowH*scale) {
                    imgHeight = windowH*scale;
                    imgWidth = imgHeight * realWidth / realHeight
  
                }
            } else if(realHeight>windowH*scale) {//如图片高度合适，判断图片宽度
                imgHeight = windowH*scale;//如大于窗口宽度，图片宽度进行缩放
                imgWidth = imgHeight*realWidth/realHeight;//等比例缩放高度
            } else {//如果图片真实高度和宽度都符合要求，高宽不变
                imgWidth = realWidth;
                imgHeight = realHeight;
            }
			
            $('#bigimg').css("width",windowW);//以最终的宽度对图片缩放
            $('#bigimg').css("height",1000);//以最终的宽度对图片缩放
            //var w = (windowW-imgWidth)/2;//计算图片与窗口左边距
           // var h = (windowH-imgHeight*2)/2;//计算图片与窗口上边距

            $('#innerdiv').css({"top":0, "left":0});//设置#innerdiv的top和left属性
            $('#outerdiv').fadeIn("fast");//淡入显示#outerdiv
            
       
        });
     }

    $("#pri-source").click(function () {
        $('#pub-source').attr("class"," ");
        $('#pri-source').attr("class","active")
    });

    $("#pub-source").click(function () {
        $('#pri-source').attr("class"," ");
        $('#pub-source').attr("class","active")
    });

    function getcode() {
		var package_id = $('#package_id').html()

        $.ajax({
        url: '/recharge/create/',
        type: 'POST',
        data: { package_id: package_id },
        dataType: 'json',
        timeout: 10000,
        success: function(data) {
			alert(1)
			alert(data)
            var src = data.code;
            $('#getcode').attr("class","hidden");
            $('#code').attr("class"," ");
            $('#code img').attr("src", src)
        }
       });
    }
    
    function exitFullscreen(){
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
        else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        }
        else if (document.webkitCancelFullScreen) {
            document.webkitCancelFullScreen();
        }
        else if (document.msExitFullscreen) {
              document.msExitFullscreen();
        }
    }

function requestFullscreen(element) {
    if (element.requestFullscreen) {
        element.requestFullscreen();
    } else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen();
    } else if (element.webkitRequestFullScreen) {
        element.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
    }
}


$("body").keydown(function(e){
    var ev = window.event || e;
    var code = ev.keyCode || ev.which;

    if (code==37) {
        if(ev.preventDefault) {
            ev.preventDefault();
        }else {
            ev.keyCode=0;
            ev.returnValue=false;
        }
        leftImg();
    }
    if (code==39) {
        if(ev.preventDefault) {
            ev.preventDefault();
        }else {
            ev.keyCode=0;
            ev.returnValue=false;
        }
        rightImg();
    }

	// switch rl
	if (code == 90) {
    	$('#switch_placeholder').toggle();
	}

});
    // 刷新当前框架
function leftImg() {
	number = parseInt(current_big_id);
	
    if (number > 0) {
    	var x = number - 1;
    	current_big_id = x.toString();
    	zoomPicExec(x.toString());
    }
}
function rightImg() {
    number = parseInt(current_big_id);
	
	if (number >= 0) {
		var x = number + 1;
		current_big_id = x.toString();
		zoomPicExec(x.toString());
	}
   
}









