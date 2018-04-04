function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

var uuid = "";
var last_uuid = '';
// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    uuid = generateUUID();
    url = '/api/v1_0/verifycode?uuid='+uuid+'&last_uuid='+last_uuid;
    var $img = $('.image-code>img').attr('src',url);
    last_uuid = uuid;
}

//用户点击发送验证码执行的逻辑
function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO: 通过ajax方式向后端接口发送请求，让后端发送短信验证码
    //想后端发送请求 传递手机号码 验证码 uuid  和csrf_token
    var data = {
            'mobile':mobile,
            'image_code':imageCode,
            'uuid':uuid
        }
    $.ajax({
        url:'/api/v1_0/smscode',
        type:'post',
        contentType: "application/json",
        data:JSON.stringify(data),
        headers:{'X-CSRFToken':getCookie('csrf_token')},
        success:function (data) {
            // if(data.errno==0){
                 var num = 60;
            // 表示发送成功
            var timer = setInterval(function () {
                if (num >= 1) {
                    // 修改倒计时文本
                    $(".phonecode-a").html(num + "秒");
                    num -= 1;
                } else {
                    $(".phonecode-a").html("获取验证码");
                    $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    clearInterval(timer);
                }
            }, 1000, 60);
            // }else{
            //     $(".phonecode-a").attr("onclick", "sendSMSCode();");
            // }
        }
    })
}

// 用户点击注册执行的逻辑
$(document).ready(function() {
    generateImageCode();  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    // TODO: 注册的提交(判断参数是否为空)
    $('.form-register').submit(function (event) {
        event.preventDefault();
        //我需要给后台的数据 手机号码 密码 uuid csrf
    var mobile = $('#mobile').val();
    var phonecode = $('#phonecode').val();
    var password2 = $('#password2').val();
    var password = $('#password').val();
    if (!mobile) {
        $("#image-code-err span").html("请填写手机号码！");
        $("#image-code-err").show();
        return
    };
    if (!phonecode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        return
    };
    if (password!=password2) {
        $("#image-code-err span").html("二次密码不一致");
        $("#image-code-err").show();
        return
    };
    data = {
        'mobile':mobile,
        'sms_code':phonecode,
        'uuid':uuid,
        'password':password
    };
    $.ajax({
        url:'/api/v1_0/users',
        type:'post',
        contentType: "application/json",
        data:JSON.stringify(data),
        headers:{'X-CSRFToken':getCookie('csrf_token')},
        success:function (data) {
            if(data.errno=='0'){

                window.location.href = '/'
            }else {
                alert(data.errmsg)
            }
        }
    });

    });

});
