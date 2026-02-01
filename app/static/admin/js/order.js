$(document).ready(function () {

    $(".list").on('click', '.detail-btn', function () {
        var $li = $(this).closest('li');
        var item_id = $li.data('order_id');
        var $mask2 = $('.mask2:eq(0)');
        $.ajax({
            url: '/admin/get_item/' + item_id,
            type: 'GET',
            success: function (response) {
                console.log(response.item);
                $mask2.find('.user_name').text(response.item.user.name + '的订单内容');
                $mask2.find('.product_name').text('商品：' + response.item.product.name);
                $mask2.find('.product_brand').text('品牌：' + response.item.product.derive);
                $mask2.find('.product_price').text('价格：¥' + response.item.product.price);
                if (response.item.item.is_pay == 1) {
                    $mask2.find('.is_pay').text('该订单已支付');
                } else {
                    $mask2.find('.is_pay').text('该订单未支付');
                }
                $mask2.find('.item_number').text('共包含' + response.item.item.number + '件商品');
            },
            error: function (error) {
                console.error(error);
                alert("获取详情失败！");
            }
        });
        $mask2.css('display', 'block');
        $mask2.addClass("show");
        return false;
    });

    $('.det-n').on('click', function () {
        $('.mask2').css('display', 'none');
        $('.mask2').removeClass("show");
    });

    // 搜索功能
    function performOrderSearch() {
        var searchTerm = $('.search-ipt').val().trim();

        if (!searchTerm) {
            alert('请输入搜索关键词');
            return;
        }

        $.ajax({
            url: '/admin/search_view',
                type: 'GET',
                data: {search: searchTerm, text: 'order'},
                success: function (data) {
                    console.log(data);
                    var $list = $('.list');
                    $list.empty();

                    if (data.orders && data.orders.length > 0) {
                        // 按用户分组显示订单
                        var groupedOrders = {};
                        $.each(data.orders, function(index, order) {
                            if (!groupedOrders[order.user_id]) {
                                groupedOrders[order.user_id] = {
                                    user: null,
                                    orders: []
                                };
                            }
                            groupedOrders[order.user_id].orders.push(order);
                        });

                        // 添加用户信息并显示
                        $.each(data.users, function(index, user) {
                            if (groupedOrders[user.id]) {
                                groupedOrders[user.id].user = user;
                            }
                        });

                        // 渲染订单
                        $.each(groupedOrders, function(userId, groupData) {
                            if (groupData.user) {
                                var $user = $('<span>').addClass('user').html('<span class="s">用户</span>&nbsp;&nbsp;' + groupData.user.name + '&nbsp;&nbsp;<span class="s">的订单</span>');
                                $list.append($user);

                                $.each(groupData.orders, function(index, order) {
                                    var $listItem = $('<li>').data('order_id', order.item_id).data('product_id', order.product_id);
                                    var $productName = $('<span>').addClass('product_name').text(order.product.name || '未知商品');
                                    var $productBrand = $('<span>').addClass('product_brand').text('品牌：' + (order.product.derive || '未知'));
                                    var $productPrice = $('<span>').addClass('product_price').text('价格：¥' + (order.product.price || '0'));
                                    var $number = $('<span>').addClass('number').text('数量：' + order.number);
                                    var $isPay = $('<span>').addClass('is_pay').text(order.is_pay == 1 ? '已支付' : '未支付');
                                    $listItem.append($productName, $productBrand, $productPrice, $number, $isPay);

                                    var $detBtn = $('<a>').attr('href', 'javascript:;').addClass('detail-btn').text('详情');
                                    $listItem.append($detBtn);

                                    $list.append($listItem);
                                });
                            }
                        });
                    } else {
                        $list.html('<p style="text-align: center; color: #909399; padding: 40px;">没有找到相关订单</p>');
                    }

                    console.log('订单搜索成功！');
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.error('Error:', textStatus, errorThrown);
                    $('.list').html('<p style="text-align: center; color: #f56c6c; padding: 40px;">搜索失败，请稍后再试</p>');
                }
            });
    }

    // 搜索图标点击事件
    $('.search-icon').on('click', function (event) {
        event.preventDefault();
        event.stopPropagation();
        performOrderSearch();
    });

    // 回车键搜索
    $('.search-ipt').on('keypress', function (e) {
        if (e.which == 13) { // 回车键
            e.preventDefault();
            performOrderSearch();
        }
    });

    // 清空搜索按钮
    $('.clear-btn').on('click', function (e) {
        e.preventDefault();
        $('.search-ipt').val('');
        location.reload();
    });

})
