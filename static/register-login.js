function phonenumListen(obj){
    var val = obj.value;
    var re = /^1\d{10}$/;
    if(re.test(val)){
        $('.form-warning').html("<a>成功</a>");
    }else{
        $('.form-warning').html("<a>请输入手机号</a>");
    }
}

function usernameListen(obj){
    var val = obj.value;
    var re  = /^[0-9A-Za-z]{4,16}$/;
    if(re.test(val)){
        $('.form-warning').html("<a>格式正确</a>");
    }else{
        $('.form-warning').html("<a>請輸入4-16位数字字母</a>");
    }
}

function emailListen(obj){
    var val = obj.value;
    var re  = /^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/;
    if(re.test(val)){
        $('.form-warning').html("<a> </a>");
    }else{
        $('.form-warning').html("<a>格式不正确</a>");
    }
}

function passwordListen(obj){
    var val = obj.value;
    var re  = /^[A-za-z]\w{5,19}$/;
    if(re.test(val)){
        $('.form-warning').html("<a>格式正确</a>");
    }else{
        $('.form-warning').html("请用字母开头");
    }
}

function passwordMatch(obj){
    var val1 = obj.value;
    var val2 = $('#password1').val();
    if(val1 == val2){
        $('.form-warning').html("<a> </a>");
    }else {
        $('.form-warning').html("<a>两次密码不一致</a>");
    }
}

var InterValObj;
var count = 60;
var curCount;

function sendCode() {
     curCount = count;
     $("#verifybutton").attr("disabled", "true");
     $("#verifybutton").html(curCount + "秒后可重新获取");
     InterValObj = window.setInterval(SetRemainTime, 1000);
     var phonenum = $("#phonenum").val();
     var usagestr = $("#usage").val();
     var usage = parseInt(usagestr, 10);
     $.ajax({
        url: '/request-verifycode/',
        type: 'POST',
        data: {"phonenum": phonenum, "usage": usage},
        dataType: 'json',
        timeout: 10000,
        success: function(data) {

        }
     });
}

function SetRemainTime() {
    if (curCount == 0) {
        window.clearInterval(InterValObj);
        $("#verifybutton").removeAttr("disabled");
        $("#verifybutton").html("重新发送验证码");
    }
    else {
        curCount--;
        $("#verifybutton").html(curCount + "秒后可重新获取");
    }
}
















