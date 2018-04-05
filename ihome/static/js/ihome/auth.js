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

$(document).ready(function(){
    // TODO: 查询用户的实名认证信息
    $.get('/api/v1_0/user/auth',function (data) {
        if (data.errno=='0'){
            $("#real-name").val(data.data.real_name);
            $("#id-card").val(data.data.id_card);

            if (data.data.real_name){
                 $("#real-name").attr("disabled",true)

            }
            if (data.data.id_card){
                $("#id-card").attr("disabled",true)
                $(".btn-success").hide()
                return
            }

            $('.error-msg').show()

        }else if(data.errno=='4101'){
            alert('请登陆')
            window.location.href = '/'
        }
    });

    // TODO: 管理实名信息表单的提交行为
    $('#form-auth').submit(function (event) {
         event.preventDefault();
         var real_name = $("#real-name").val()
         var id_card = $("#id-card").val()

         params = {
            'real_name':real_name,
            'id_card':id_card
         }

         $.ajax({
             url:'/api/v1_0/user/auth',
             type:'post',
             contentType:'application/json',
             data:JSON.stringify(params),
             headers:{'X-CSRFToken':getCookie('csrf_token')},
             success:function (data) {
                 if (data.errno=='0'){
                     $("#real-name").attr("disabled",true);
                     $("#id-card").attr("disabled",true);
                     $(".btn-success").hide();
                     alert('保存成功')
                     window.location.href = '/auth.html'
                 }else if(data.errno=='4101'){
                     alert('请登陆');
                     window.location.href='/'
                 }else{
                     alert(data.errmsg)
                 }
             }
         });
    });
})