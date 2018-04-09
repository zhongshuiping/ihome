//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    // TODO: 查询房东的订单
    $.get('/api/v1_0/orders?role=landlord',function (data) {
        if (data.errno == '0') {

            var html = template('orders-list-tmpl', {'orders': data.orders});
            $('.orders-list').html(html)

            // TODO: 查询成功之后需要设置接单和拒单的处理
            $(".order-accept").on("click", function () {
                var orderId = $(this).attr("order-id");
                $(".modal-accept").attr("order-id", orderId);
            });
             $(".modal-accept").click(function () {

                 var orderId = $(this).parents("li").attr("order-id");
                 var params = {
                'action': 'accept'
            };
                  $.ajax({
                url: '/api/v1_0/orders/' + orderId + '/status',
                type: 'put',
                data: JSON.stringify(params),
                contentType: 'application/json',
                headers: {"X-CSRFToken": getCookie('csrf_token')},
                success: function (data) {
                    if (data.errno == '0') {
                        $(".orders-list>li[order-id=" + orderId + "]>div.order-content>div.order-text>ul li:eq(4)>span").html("已接单");
                        $("ul.orders-list>li[order-id=" + orderId + "]>div.order-title>div.order-operate").hide();
                        $("#accept-modal").modal("hide");
                    } else if (data.errno == '4101') {
                        window.location.href = '/'
                    } else {
                        alert(data.errmsg)
                    }
                }
            });
             });


            //接单

            $(".order-reject").on("click", function () {
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-reject").attr("order-id", orderId);
            });
            $(".modal-reject").click(function () {
                var orderId = $(this).attr("order-id");
                var rejectReason = $("#reject-reason").val();
                if (!rejectReason) {
                    alert('必须写原因')
                }
                var params = {
                    'action': 'reject',
                    'reason': rejectReason
                }
                //拒单
            $.ajax({
                url: '/api/v1_0/orders/' + orderId + '/status',
                type: 'put',
                data: JSON.stringify(params),
                contentType: 'application/json',
                headers: {"X-CSRFToken": getCookie('csrf_token')},
                success: function (data) {
                    if (data.errno == '0') {
                        $(".orders-list>li[order-id=" + orderId + "]>div.order-content>div.order-text>ul li:eq(4)>span").html("已拒单");
                        $("ul.orders-list>li[order-id=" + orderId + "]>div.order-title>div.order-operate").hide();
                        $("#reject-modal").modal("hide");
                    } else if (data.errno == '4101') {
                        window.location.href = '/'
                    } else {
                        alert(data.errmsg)
                    }
                }
            });

            });

        } else if (data.errno = '4101') {
            window.location.href = '/'
        } else {
            alert(data.errmsg)
        }

    })
});
