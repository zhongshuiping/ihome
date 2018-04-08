from flask import g,current_app,jsonify,request
from ihome.utils.common import login_required
from . import api
from ihome.models import Area,HouseImage,Order
from ihome.utils.response_code import RET
from ihome.models import House,Facility
from ihome import db
from ihome.utils.qiniu_image import upload_image
from ihome.constants import QINIU_URL_DOMAIN
from config import Config
from ihome.constants import AREA_INFO_REDIS_CACHE_EXPIRES
from datetime import datetime
from ihome import constants

redis = Config.get_redis_connect()

'''
显示城区列表
'''
@api.route('/areas')
@login_required
def show_areas():
    try:
        areas_list = redis.get('Area')
    except Exception as e:
        return jsonify({'errno':RET.DBERR,'errmsg':'redis数据库失败'})
    if areas_list :
        return jsonify({'errno': RET.OK, 'errmsg': '查询成功', 'data': eval(areas_list)})

    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno':RET.DBERR,'errmsg':'查询数据库失败'})
    areas_list = []
    for area in areas:
        areas_list.append(area.to_dict())
    redis.set('Area',areas_list,AREA_INFO_REDIS_CACHE_EXPIRES)

    return jsonify({'errno':RET.OK,'errmsg':'查询成功','data':areas_list})

'''
发布房源
'''
@api.route('/houses',methods=['POST'])
@login_required
def set_house():

    data = request.get_json()
    title = data.get('title') #标题
    price = data.get('price') #价格
    area_id = data.get('area_id') #城区id
    address = data.get('address') #房屋地址
    room_count = data.get('room_count') #房间数目
    acreage = data.get('acreage') #房屋面积
    unit = data.get('title') #房屋单元
    capacity = data.get('title') #房屋容纳的人数
    beds = data.get('title') #房屋床铺的配置
    deposit = data.get('title') #房屋押金
    min_days = data.get('title') #最少入住天数
    max_days = data.get('title') #最大入住天数
    facilitys = data.get('facility')



    if not all([title,price,area_id,address,room_count,acreage,unit,capacity,beds,deposit,min_days,max_days]):
        return jsonify({'errno':RET.NODATA,'errmsg':'缺少参数'})
    try:
        room_count = int(room_count)
        price = float(price)*100
        acreage = int(acreage)
        deposit = float(deposit)*100
        min_days = int(min_days)
        max_days = int(max_days)
    except Exception as e:
        return jsonify({'errno':RET.DATAERR,'errmsg':'传的参数类型错误'})
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno':RET.DATAERR,'errmsg':'查询地区失败'})

    if not area:
        return jsonify({'errno':RET.NODATA,'errmsg':'没有该城区'})

    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.deposit = deposit
    house.beds = beds
    house.min_days = min_days
    house.max_days = max_days
    try:
        if facilitys:
            facilitys = Facility.query.filter(Facility.id.in_(facilitys)).all()
            house.facilities = facilitys
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno':RET.DBERR,'errmsg':'配套设施数据库查询失败'})
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify({'errno':RET.DBERR,'errmsg':'添加失败'})

    return jsonify({'errno':RET.OK,'errmsg':'添加成功','data':{'house_id':house.id}})

'''
上传房源的图片
'''
@api.route('/houses/images',methods=['POST'])
@login_required
def set_house_image():

    house_id = request.form.get('house_id')
    house_image = request.files.get('house_image')

    if not all([house_id,house_image]):
        return jsonify({'errno':RET.PARAMERR,'errmsg':'房屋id或者图片不能为空'})
    try:
        house = House.query.get(house_id)
        if not house:
            return jsonify({'errno':RET.DATAERR,'errmsg':'请先添加房屋的基本信息'})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno':RET.DBERR,'errmsg':'查询房屋信息失败'})
    try:
        key = upload_image(house_image.stream.read())
    except Exception as e:
        return jsonify({'errno':RET.THIRDERR,'errmsg':'图片服务器错误,请明天再试'})

    image = HouseImage(house_id=house_id,url=key)

    try:
        db.session.add(image)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'errno':RET.DBERR,'errmsg':'保存图片失败'})
    try:

        house.index_image_url = QINIU_URL_DOMAIN + key


        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify({'errno': RET.DBERR, 'errmsg': '保存房屋失败'})


    return jsonify({'errno':RET.OK,'errmsg':'上传房屋图片成功','data':{'url':QINIU_URL_DOMAIN+key}})

'''
房屋详情页面
'''
@api.route('/houses/<int:house_id>')
@login_required
def house_detail(house_id):
    try:
        house = House.query.get(house_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno':RET.DBERR,'errmsg':'没有这个房子'})

    data = {
        'house':house.to_full_dict(),
        'user_id':g.user_id  #这个user_id是登陆用户的id
    }
    return jsonify({'errno':RET.OK,'errmsg':'OK','data':data})

'''
首页房屋推荐
'''
@api.route('/houses/index')
def house_index():

    # 根据数据库房屋的按照最新的进行排序
    try:
        houses = House.query.order_by(House.create_time.desc()).limit(5).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno':RET.DBERR,'errmsg':'数据查询失败'})
    house_list = []
    for house in houses:
        house_list.append(house.to_basic_dict())

    return jsonify({'errno':RET.OK,'errmsg':'OK','data':house_list})

'''
房屋数据的搜索
'''
@api.route('/houses')
def get_house():

    aid = request.args.get('aid') #城区的id
    sd = request.args.get('sd')  # 入住开始时间
    ed = request.args.get('ed')  #入住接收的时间
    sk = request.args.get('sk')  #sortkye 排序的方式
    p = request.args.get('p')    # 页码
    start_time = []
    end_time = []
    try:
        if aid:
            aid = int(aid)
        if sd:
            start_time = datetime.strptime(sd,'%Y-%m-%d')
        if ed:
            end_time = datetime.strptime(ed,'%Y-%m-%d')

        if start_time and end_time:
            # 断言：入住时间一定小于离开时间，如果不满足，就抛出异常
            assert start_time < end_time, Exception('入住时间有误')
        if p:
            p = int(p)
        else:
            p = 1
    except Exception as e:
        return jsonify({'errno':RET.PARAMERR,'errmsg':'传入的参数错误'})
    try:
        data = redis.hget('house_%s_%s_%s_%s' % (aid, sd, ed, sk), p)
        if data:
            return jsonify({'errno': RET.OK, 'errmsg': 'OK', 'data': data})
    except Exception as e:
        current_app.logger.error(e)

    try:
        base_query = House.query
        if aid:
            base_query = base_query.filter_by(area_id=aid)
        # 如果是被下单的房间就不能被显示,更订单里面的时间进行对比
        # 根据用户传入的入住时间和离开的时间
        config_orders = []  #里面装的是要展示的页面的房子的Order
        config_orders_ids = []
        if start_time and end_time:
            config_orders = Order.query.filter(end_time>Order.begin_date,start_time<Order.end_date)
        elif start_time:
            config_orders = Order.query.filter(start_time < Order.end_date).all()
        elif end_time:
            config_orders = Order.query.filter(end_time > Order.begin_date).all()

        if config_orders:
            config_orders_ids = [order.house_id for order in config_orders]
            #遍历冲突订单中的order,把order中的id封装成一个列表
        if config_orders_ids:
            base_query = base_query.filter(House.id.notin_([config_orders_ids]))

        if sk=='new':
            base_query = base_query.order_by(House.create_time.desc())
        if sk=='booking':
            base_query = base_query.order_by(House.order_count.desc())
        if sk=='price-inc': #低到高
            base_query = base_query.order_by(House.price.asc())
        if sk=='price-des': #高到低
            base_query = base_query.order_by(House.price.desc())

        paginate = base_query.paginate(p,constants.HOUSE_LIST_PAGE_CAPACITY,False)

        houses = paginate.items
        total_page = paginate.pages
        houses_list = []
        for house in houses:
            houses_list.append(house.to_basic_dict())

        data = {
            'houses_list':houses_list,
            'total_page':total_page
        }
        try:
            pipe = redis.pipeline()
            pipe.multi() #开始事物
            redis.hset('house_%s_%s_%s_%s' % (aid, sd, ed, sk), p,data)
            redis.expire('Area',constants.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES)
            pipe.execute()
        except Exception as e:
            current_app.logger.error(e)

        return jsonify({'errno':RET.OK,'errmsg':'OK','data':data})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno':RET.DBERR,'errmsg':'查询数据库的房子信息失败'})