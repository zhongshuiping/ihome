function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // TODO: 在页面加载完毕向后端查询用户的信息
    $.get('/api/v1_0/users',function (data) {
        if (data.errno=='0'){
             $('#user-avatar').attr('src',data.data.avatar)
            $('#user-name').val(data.data.name)
        }else if(data.errno=='4101'){
            alert('请登陆')
            window.location.href = '/'
        }
    });

    // TODO: 管理上传用户头像表单的行为
    $('#form-avatar').submit(function (event) {
        event.preventDefault();

        $(this).ajaxSubmit({
            url:'/api/v1_0/avatar',
            type:'post',
            headers: {
                   'X-CSRFToken':getCookie('csrf_token')
               },
            success:function (data) {
                if (data.errno == '0'){
                    alert('上传文件成功')
                }else if(data.errno == '4101'){
                    alert('请登陆')
                    window.location.href = '/'
                }else{
                    alert(data.errmsg)
                }
            }
        });

    });

    // TODO: 管理用户名修改的逻辑
    $('#form-name').submit(function (event) {

        event.preventDefault();
        var name = $('#user-name').val();
        console.log(name)
        params = {
            'name':name
        };
        $.ajax({
            url:'/api/v1_0/name',
            type:'put',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (data) {
                if (data.errno=='0'){
                    showSuccessMsg();
                    window.location.href='/my.html'
                }else if(data.errno=='4101'){
                    alert('请登陆')
                    window.location.href='/'
                }else{
                    alert(data.errmsg)
                }
            }
        })

    });
})

