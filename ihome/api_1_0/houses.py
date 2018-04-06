from flask import g,current_app,jsonify,request
from ihome.utils.common import login_required
from . import api
from ihome.models import Area,HouseImage
from ihome.utils.response_code import RET
from ihome.models import House,Facility
from ihome import db
from ihome.utils.qiniu_image import upload_image
from ihome.constants import QINIU_URL_DOMAIN

'''
显示城区列表
'''
@api.route('/areas')
@login_required
def show_areas():
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno':RET.DBERR,'errmsg':'查询数据库失败'})
    areas_list = []
    for area in areas:
        areas_list.append(area.to_dict())

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
    pass