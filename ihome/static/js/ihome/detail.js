function hrefBack() {
    history.go(-1);
}

function mySwiper() {
    // TODO: 数据加载完毕后,需要设置幻灯片对象，开启幻灯片滚动
    var mySwiper = new Swiper ('.swiper-container', {
        loop: true,
        autoplay: 2000,
        autoplayDisableOnInteraction: false,
        pagination: '.swiper-pagination',
        paginationType: 'fraction'
    });
}

// 解析提取url中的查询字符串参数
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    // 获取详情页面要展示的房屋编号
    var queryData = decodeQuery();
    var houseId = queryData["id"];

    // TODO: 获取该房屋的详细信息
    $.get('/api/v1_0/houses/' + houseId,function (data) {
        if (data.errno=='0'){
            var img = template('house-image-tmpl',{'img_urls':data.data.house.img_urls,'price':data.data.house.price});
            $('.swiper-container').html(img);

            var houseInfo = template('house-detail-tmpl',{'house':data.data.house});
            $('.detail-con').html(houseInfo);
            console.log(data.data.user_id);
            console.log(data.data.house.user_id);
            if (data.data.user_id == data.data.house.user_id){
                $('.book-house').hide()
            }else{
                $('.book-house').show()
            }
            mySwiper()
        }else if(data.errno=='4101'){
            window.location.href='/'
        }else{
            alert(data.errmsg)
        }
    });

})