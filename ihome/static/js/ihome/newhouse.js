function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    // TODO: 在页面加载完毕之后获取区域信息
    $.get('/api/v1_0/areas',function (data) {
        if(data.errno=='0'){

            //将后台查询的数据通过模板引擎放到html中
            var html_area = template('areas-tmpl',{areas:data.data});

            $('#area-id').html(html_area)

        }else if(errno=='4101'){
            window.location.href = '/'
        }else{
            alert(data.errmsg)
        }
    });

    // TODO: 处理房屋基本信息提交的表单数据
    $('#form-house-info').submit(function (event) {
        event.preventDefault();

        var data = {}; //{'title':'1'}
        $("#form-house-info").serializeArray().map(function(x) {

            data[x.name]=x.value
        });
        var facility = []
        $(':checkbox:checked[name=facility]').each(function (i,itme) {

            facility[i] = $(itme).val()
        })
        data.facility = facility
        // 向后台发起ajax的请求
        $.ajax({
            url:'/api/v1_0/houses',
            type:'post',
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            data:JSON.stringify(data),
            success:function (data) {
                if (data.errno=='0'){
                    $('#form-house-info').hide();
                    $('#form-house-image').show();
                    $('#house-id').val(data.data.house_id);

                }else if(data.errno=='4101'){
                    window.location.href = '/'
                }else {
                    alert(data.errmsg)
                }

            }
        });


    });

    // TODO: 处理图片表单的数据
    $('#form-house-image').submit(function (event) {
        event.preventDefault();

        // ajsxSubmit 是form的异步提交 input的数据会自动提交
         $(this).ajaxSubmit({
            url:'/api/v1_0/houses/images',
            type:'post',
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (data) {
                if(data.errno=='0'){
                    alert('添加成功')
                    $('.house-image-cons').append('<img src="'+ data.data.url+'">')
                }else{
                    alert(data.errmsg)
                }
            }
        })
    });
})