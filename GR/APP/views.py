import uuid

from django.core.cache import cache
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse

from App import order_status
from App.models import HomeWheel, HomeNav, HomeMustBuy, HomeShop, HomeMainShow, FoodType, Goods, UserModel, CartModel, \
    OrderModel, OrderGoods

ALL_TYPE = '0'

TOTAL_RULE = '0'

PRICE_AESC = '1'

PRICE_DESC = '2'

def home(request):
    wheels = HomeWheel.objects.all()

    navs = HomeNav.objects.all()

    mustbuys = HomeMustBuy.objects.all()

    shops = HomeShop.objects.all()

    shops0_1 = shops[0:1]

    shops1_3 = shops[1:3]

    shops3_7 = shops[3:7]

    shops7_11 = shops[7:11]

    mainshows = HomeMainShow.objects.all()

    data = {
        'title': '首页',
        "wheels": wheels,
        'navs': navs,
        'mustbuys': mustbuys,
        'shops0_1': shops0_1,
        'shops1_3': shops1_3,
        'shops3_7': shops3_7,
        'shops7_11': shops7_11,
        'mainshows': mainshows

    }

    return render(request, 'home/home.html', context=data)


def market(request):
    return redirect(reverse('axf:market_with_params', args=('104749', '0', '0')))


def market_with_params(request, categoryid, childcid, sort_rule):

    foodtypes = FoodType.objects.order_by('typesort')

    if childcid == ALL_TYPE:
        goods_list = Goods.objects.all().filter(categoryid=categoryid)
    else:
        goods_list = Goods.objects.all().filter(categoryid=categoryid).filter(childcid=childcid)

    if sort_rule == TOTAL_RULE:
        pass
    elif sort_rule == PRICE_AESC:
        goods_list = goods_list.order_by('price')
    elif sort_rule == PRICE_DESC:
        goods_list = goods_list.order_by('-price')

    # 分类对象
    foodtype = FoodType.objects.get(typeid=categoryid)

    childtypenames = foodtype.childtypenames


    childtypename_list = childtypenames.split("#")

    child_type_name_list = []

    for childtypename in  childtypename_list:
        child_type_name_list.append(childtypename.split(":"))

    data = {
        "title": '闪购',
        "foodtypes": foodtypes,
        'goods_list': goods_list,
        'categoryid': int(categoryid),
        'childcid': childcid,
        'child_type_name_list': child_type_name_list,
    }

    return render(request, 'market/market.html', context=data)


def cart(request):

    userid = request.session.get('user_id')

    if not userid:
        return redirect(reverse('axf:user_login'))

    cartmodels = CartModel.objects.filter(c_user_id=userid)

    is_all_select = True

    total_price = 0

    for cartmodel in cartmodels:
        if not cartmodel.c_goods_select:
            is_all_select = False
        else:
            total_price += cartmodel.c_goods_num * cartmodel.c_goods.price

    data = {
        'title': '购物车',
        'cartmodels': cartmodels,
        'is_all_select': is_all_select,
        #  格式化 将数据设置为 float类型，并且保留两位小数
        'total_price':  '{:.2f}'.format(total_price)
    }

    return render(request, 'cart/cart.html', context=data)


def mine(request):

    is_login = False

    user_id = request.session.get('user_id')

    data = {
        "title": "我的",
        "is_login": is_login,
    }

    if user_id:
        try:
            user = UserModel.objects.get(pk=user_id)
            is_login = True
            data['is_login'] = is_login
            data['user_icon'] = '/static/upload/' + user.u_icon.url
            data['username'] = user.u_name

            orders = OrderModel.objects.filter(o_user=user).filter(o_status=order_status.ORDERED)

            data['order_wait_pay_no'] = orders.count()

            sended_count = OrderModel.objects.filter(o_user=user).filter(o_status=order_status.PAYED).count()

            if sended_count > 0:
                data['order_sended_no'] = sended_count

        except Exception as e:
            print(str(e))
            # del request.session['user_id']

    return render(request, 'mine/mine.html', context=data)


def user_register(request):
    if request.method == "GET":
        data = {
            "title": '用户注册',
        }
        return render(request, 'user/user_register.html', context=data)
    elif request.method == "POST":

        u_name = request.POST.get("u_name")
        u_email = request.POST.get("u_email")
        u_password = request.POST.get("u_password")
        print(u_password)
        u_icon = request.FILES.get("u_icon")

        user = UserModel()
        user.u_name = u_name
        user.u_email = u_email
        user.u_icon = u_icon
        user.set_password(u_password)

        user.save()

        request.session['user_id'] = user.id


        token = str(uuid.uuid4())


        cache.set(token, user.id, timeout=60 * 60)

        send_mail_learn(u_name, u_email, token)

        return redirect(reverse('axf:mine'))


def user_logout(request):
    request.session.flush()
    return redirect(reverse('axf:mine'))


def check_user(request):
    u_name = request.GET.get("u_name")

    print(u_name)

    # 结果只可能是有一个 或没有
    users = UserModel.objects.filter(u_name=u_name)

    data = {
        'msg': 'ok',
        'status': '200'
    }

    if users.exists():
        # 告诉客户端用户存在
        data['status'] = '901'
        data['msg'] = "already exists"
    else:
        # 不存在，可以使用
        data['status'] = '200'
        # 可用
        data['msg'] = 'avaliable'
    return JsonResponse(data)


def check_email(request):

    u_email = request.GET.get('u_email')

    users = UserModel.objects.filter(u_email=u_email)

    data = {
        'msg': 'ok',
        'status': '200'
    }

    if users.exists():
        data['msg'] = 'already exists'
        data['status'] = '902'

    return JsonResponse(data)


def user_login(request):
    if request.method == "GET":
        msg = request.session.get('msg')

        data = {
            'title': '用户登录',
        }

        if msg:
            data['msg'] = msg

        return render(request, 'user/user_login.html', context=data)

    elif request.method == "POST":

        username = request.POST.get('u_name')

        password = request.POST.get('u_password')

        users = UserModel.objects.filter(u_name=username)

        if users.exists():
            user = users.first()
            if user.check_password(password):

                if user.is_active:
                    print('用户已激活，正常登录')
                    request.session['user_id'] = user.id
                    return redirect(reverse('axf:mine'))
                else:
                    print('用户验证成功，但是未激活')
                    # 用户未激活
                    request.session['msg'] = '用户未激活'
                    return redirect(reverse('axf:user_login'))
            else:
                print('密码错误')
                # 用户名或密码错误
                # 密码验证失败  用户密码错误
                request.session['msg'] = '密码错误'
                return redirect(reverse('axf:user_login'))
        else:
            # 用户不存在   用户名错误
            print('用户名不存在')
            request.session['msg'] = '用户名不存在'
            return redirect(reverse('axf:user_login'))


def send_mail_learn(username, receive_email, token):

    subject = "%s爱鲜蜂账户激活" % username

    message = ""

    from_email = 'ymy16600207857@163.com'
    # 动态的
    recipient_list = [receive_email,]

    temp = loader.get_template('user/user_active.html')

    data = {
        'username': username,
        'active_url': 'http://127.0.0.1:8001/axf/activeaccount/?user_token=%s' % token,
    }

    html_message = temp.render(data)

    send_mail(subject, message, from_email, recipient_list,html_message=html_message)


def active_account(request):

    user_token = request.GET.get('user_token')

    user_id = cache.get(user_token)

    if not user_id:
        return HttpResponse("激活邮件已过期，请重新申请激活")

    cache.delete(user_token)

    user = UserModel.objects.get(pk=user_id)

    user.is_active = True

    user.save()

    return HttpResponse('用户激活成功')


def add_to_cart(request):
    print('添加到购物车')
    goodsid = request.GET.get("goodsid")

    userid = request.session.get('user_id')

    data = {
        'status': '200',
        'msg': 'ok',
    }

    if not userid:
        data['status'] = '302'
    else:
        # 添加到购物车，  先查询数据是否存在
        cart_models = CartModel.objects.filter(c_goods_id=goodsid).filter(c_user_id=userid)
        # 判断是否存在
        if cart_models.exists():
            # 如果存在 对原有数据的数量进行 + 1
            cart_model = cart_models.first()

            cart_model.c_goods_num = cart_model.c_goods_num + 1

            cart_model.save()
        else:
            # 如果不存在，需要新建一个对象，来存储信息
            cart_model = CartModel()

            cart_model.c_goods_id = goodsid

            cart_model.c_user_id = userid

            cart_model.save()
        data['goods_num'] = cart_model.c_goods_num

    # 将数据添加到购物车，并且修改显示数量
    return JsonResponse(data)


def sub_to_cart(request):

    cartid = request.GET.get('cartid')

    cartmodel = CartModel.objects.get(pk=cartid)

    data = {
        'status': '200',
    }

    if cartmodel.c_goods_num > 1:
        cartmodel.c_goods_num = cartmodel.c_goods_num - 1
        cartmodel.save()
        data['goods_num'] = cartmodel.c_goods_num
    else:
        cartmodel.delete()
        data['goods_num'] = 0

    data['total_price'] =  '{:.2f}'.format(calc_total(request.session.get('user_id')))

    return JsonResponse(data)


def change_cart_status(request):

    cartid = request.GET.get('cartid')

    cartmodel = CartModel.objects.get(pk=cartid)

    cartmodel.c_goods_select = not cartmodel.c_goods_select

    cartmodel.save()

    is_all_select = True

    userid = request.session.get('user_id')
    # 筛选购物车数据  是否有未选中
    cartmodels = CartModel.objects.filter(c_user_id=userid).filter(c_goods_select=False)
    # 未选中的只要存在，全选按钮就是未选中
    if cartmodels.exists():
        is_all_select = False

    data = {
        'msg': 'ok',
        'status': '200',
        'select': cartmodel.c_goods_select,
        'is_all_select': is_all_select,
        'total_price': '{:.2f}'.format(calc_total(request.session.get('user_id')))
    }

    return JsonResponse(data)


def change_carts_status(request):

    carts = request.GET.get('carts')

    cart_list = carts.split('#')

    print(cart_list)

    select = request.GET.get('select')

    print(select)

    print(type(select))

    if select == 'true':
        print('这是真的')
        is_select = True
    else:
        print('这是假的')
        is_select = False

    for cartid in cart_list:
        cartmodel = CartModel.objects.get(pk=cartid)
        cartmodel.c_goods_select = is_select
        cartmodel.save()

    data = {
        'msg': 'ok',
        'status': '200',
        'total_price': '{:.2f}'.format(calc_total(request.session.get('user_id')))
    }

    return JsonResponse(data)


def calc_total(user_id):

    total_price = 0

    cartmodels = CartModel.objects.filter(c_user_id=user_id).filter(c_goods_select=True)

    for cartmodel in cartmodels:
        total_price += cartmodel.c_goods_num * cartmodel.c_goods.price

    return total_price


def make_order(request):

    carts = request.GET.get('carts')

    cart_list = carts.split("#")

    print(cart_list)

    order = OrderModel()

    userid = request.session.get('user_id')

    order.o_user = UserModel.objects.get(pk=userid)

    order.save()

    # 订单中的商品数据，是从购物车中来的
    # 就是将购物车中的数据删除，在订单商品表中添加 那些移除的数据

    for cartid in cart_list:
        # 查询购车中的数据
        cartmodel = CartModel.objects.get(pk=cartid)
        # 创建订单商品数据
        ordergoods = OrderGoods()
        # 绑定订单
        ordergoods.o_order = order
        # 订单商品数据的 商品个数
        ordergoods.o_goods_num = cartmodel.c_goods_num
        # 订单商品数据的 商品是啥
        ordergoods.o_goods = cartmodel.c_goods

        ordergoods.save()

        cartmodel.delete()

    data = {
        'msg': 'ok',
        'status':'200',
        'order': order.id
    }

    return JsonResponse(data)


def order_detail(request):

    order_id = request.GET.get('orderid')

    data = {}

    try:

        order = OrderModel.objects.get(pk=order_id)

        data['order_no'] = order.id
        data['order'] = order

    except:
        render(request, 'order/order_does_not_exist.html')

    return render(request, 'order/order_detail.html', context=data)


def alipay_callback(request):

    order_no = request.GET.get('order_no')

    order = OrderModel.objects.get(pk=order_no)

    order.o_status = order_status.PAYED

    order.save()

    data = {
        'msg': 'ok',
        'status': '200'
    }

    return JsonResponse(data)


# 订单列表
#   订单列表类型   已下单  已付款  已评价
def order_list(request):

    order_type = request.GET.get('order_type')

    user_id = request.session.get('user_id')

    user = UserModel.objects.get(pk=user_id)

    status = order_status.TYPE_ORDERED

    if order_type == order_status.TYPE_ORDERED:
        status = order_status.TYPE_ORDERED
    elif order_type == order_status.TYPE_PAYED:
        status = order_status.TYPE_PAYED

    orders = OrderModel.objects.filter(o_user=user).filter(o_status=status)

    data = {
        'orders': orders
    }

    return render(request, 'order/order_list.html', context=data)