function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(document).ready(function(){
    // TODO: 判断用户是否登录
    $.get('/api/v1_0/sessions',function (data) {
        if(data.errno!='0'){
            window.location.href = '/login.html'
        }
    })

    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $(".input-daterange").on("changeDate", function(){
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();

        if (startDate && endDate && startDate > endDate) {
            showErrorMsg("日期有误，请重新选择!");
        } else {
            var sd = new Date(startDate);
            var ed = new Date(endDate);
            days = (ed - sd)/(1000*3600*24);
            var price = $(".house-text>p>span").html();
            var amount = days * parseFloat(price);
            $(".order-amount>span").html(amount.toFixed(2) + "(共"+ days +"晚)");
        }
    });
    var queryData = decodeQuery();
    var houseId = queryData["hid"];

    // TODO: 获取房屋的基本信息
   $.get('/api/v1_0/houses/'+ houseId,function (data) {
      if(data.errno=='0'){
          $('.house-info>img').attr('src',data.data.house.img_urls[0]);
            $('.house-text>h3').html(data.data.house.title);
            $('.house-text span').html(data.data.house.price);
      } else if(data.errno=='4101'){
          window.location.href='/login.html'
      }else{
          alert(data.errmsg)
      }
   });
    // TODO: 订单提交
    $('.submit-btn').click(function () {

        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();
        if (!startDate){
            alert('请选择开始时期')
            return
        }
        if(!endDate){
            alert('请选择结束日期')
            return
        }
        params = {
            'house_id':houseId,
            'start_date':startDate,
            'end_date':endDate
        }
        $.ajax({
            url:'/api/v1_0/orders?role=custom',
            type:'post',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (data) {
                if (data.errno=='0'){
                    window.location.href = 'orders.html'
                }else if(data.errno=='4104'){
                    window.location.href='/'
                }else{
                    alert(data.errmsg)
                }
            }
        });
    })

});
