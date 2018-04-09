$(document).ready(function(){
    // TODO: 对于发布房源，只有认证后的用户才可以，所以先判断用户的实名认证状态
    $.get('/api/v1_0/sessions',function (data) {
        if(data.errno=='0'){
            if(data.data.flag==1){
                $(".auth-warn").hide();
            }else{
                $(".auth-warn").show();
            }
        }else{
            alert(data.errmsg);
            $(".auth-warn").show();
        }
    });


    // TODO: 如果用户已实名认证,那么就去请求之前发布的房源
    $.get('/api/v1_0/houses/user',function (data) {
        if(data.errno=='0'){
            var html = template('houses-list-tmpl',{'houses':data.data});
            $('#houses-list').html(html)
        }else if(data.errno=='4101'){
            window.location.href = '/'
        }else {
            alert(data.errmsg)
        }
    })
});
