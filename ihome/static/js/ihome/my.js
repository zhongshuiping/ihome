function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// TODO: 点击推出按钮时执行的函数
function logout() {
    $.ajax({
        url:'/api/v1_0/sessions',
        type:'delete',
        contentType:'application/json',
        headers:{'X-CSRFToken':getCookie('csrf_token')},
        success:function (data) {
            if (data.errno=='0'){
                alert(data.errmsg)
                window.location.href = '/'
            }
        }
    });
}

$(document).ready(function(){

    // TODO: 在页面加载完毕之后去加载个人信息

});
