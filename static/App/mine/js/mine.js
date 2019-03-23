$(function () {

    $("#wait_pay").click(function () {

        console.log('查看订单');

        window.open('/axf/orderlist/?order_type=0', tartget='_self');

    })

})