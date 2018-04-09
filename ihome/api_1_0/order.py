from . import api
from flask import request,jsonify,g,current_app
from ihome.utils.response_code import RET
from ihome.utils.common import login_required
from ihome.models import Order,House
from datetime import datetime
from ihome import db
from config import Config

redis = Config.get_redis_connect()

'''
添加订单
'''
@api.route('/orders',methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    house_id = data.get('house_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([house_id,start_date,end_date]):
        return jsonify({'errno':RET.PARAMERR,'errmsg':'参数错误'})
    start_date = datetime.strptime(start_date,'%Y-%m-%d')
    end_date = datetime.strptime(end_date,'%Y-%m-%d')

    if end_date < start_date:
        return jsonify({'errno':RET.DATAERR,'errmsg':'选择时间错误'})
    try:
        house = House.query.get(house_id)
        if not house:
            return jsonify({'errno':RET.NODATA,'errmsg':'没有该房屋'})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno':RET.DBERR,'errmsg':'查询房屋失败'})

    order = Order()
    days = (end_date-start_date).days
    order.user_id = g.user_id  # 下订单的用户编号
    order.house_id = house_id # 预订的房间编号
    order.begin_date = start_date  # 预订的起始时间
    order.end_date = end_date   # 预订的结束时间
    order.days = days # 预订的总天数
    order.house_price = house.price # 房屋的单价
    order.amount = house.price * days # 订单的总金额

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify({'errno':RET.DBERR,'errmsg':'创建order数据失败'})

    return jsonify({'errno':RET.OK,'errmsg':'OK','data':{'order_id':order.id}})

'''
获取订单的列表
'''
@api.route('/orders')
@login_required
def get_order():

    role = request.args.get('role')
    if role not in ['custom','landlord']:
        return jsonify({'errno':RET.PARAMERR,'errmsg':'role类型错误'})
    # 怎么查 根据当前user_id 查询所有跟他有关订单的信息
    user_id = g.user_id
    try:
        if role == 'custom':
            orders = Order.query.filter(Order.user_id==user_id).all()
        elif role == 'landlord':
            # 房东查看想看自己的房子下单的信息 ,所有的房源,他的发布者是该登陆用户的id
            # 根据用户的id找到他所有的房子,在根据房子id,找到跟他相关的订单,而且是没有接单的

            houses = House.query.filter(House.user_id==user_id).all()
            houses_ids = []
            orders = []
            for house in houses:
                houses_ids.append(house.id)
            if houses_ids:
                orders = Order.query.filter(Order.status=='WAIT_ACCEPT',Order.house_id.in_(houses_ids)).all()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno':RET.DBERR,'errmsg':'查询订单失败'})

    order_list = []
    for order in orders:
        order_list.append(order.to_dict())

    return jsonify({'errno':RET.OK,'errmsg':'OK','orders':order_list})

'''
房东接收订单和拒绝订单
'''
@api.route('/orders/<int:order_id>/status',methods=['PUT'])
@login_required
def accept_or_reject_order(order_id):

    data = request.get_json()
    action = data.get('action')
    reason = data.get('reason')

    if action not in ['accept','reject']:
        return jsonify({'errno':RET.DATAERR,'errmsg':'参数有误'})
    try:
        order = Order.query.get(order_id)
    except Exception as e:
        return jsonify({'errno':RET.DBERR,'errmsg':'查询order出错'})

    if action == 'accept':
        try:
            order.status = 'WAIT_COMMENT'
            if not reason:
                order.comment = reason
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'errno':RET.DBERR,'errmsg':'保存order出错'})
        return jsonify({'errno':RET.OK,'errmsg':'OK'})
    else:
        try:
            order.status = 'REJECTED'

            order.comment = reason
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'errno':RET.DBERR,'errmsg':'保存order出错'})

        return jsonify({'errno': RET.OK, 'errmsg': 'OK'})

@api.route("/orders/<int:order_id>/comment", methods=["PUT"])
@login_required
def save_order_comment(order_id):
    """保存订单评论信息"""
    user_id = g.user_id
    # 获取参数
    req_data = request.get_json()
    comment = req_data.get("comment")  # 评价信息

    # 检查参数
    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        # 需要确保只能评论自己下的订单，而且订单处于待评价状态才可以
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id,
                                   Order.status == "WAIT_COMMENT").first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="无法获取订单数据")

    if not order:
        return jsonify(errno=RET.REQERR, errmsg="操作无效")

    try:
        # 将订单的状态设置为已完成
        order.status = "COMPLETE"
        # 保存订单的评价信息
        order.comment = comment
        # 将房屋的完成订单数增加1
        house.order_count += 1
        db.session.add(order)
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="操作失败")

    return jsonify(errno=RET.OK, errmsg="OK")