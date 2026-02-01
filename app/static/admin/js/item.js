$(document).ready(function () {

    // ==================== 添加商品 ====================
    $('.add-btn, .search-actions .add-btn').click(function () {
        $('.mask').addClass('show-add').css('display', 'flex');

        // 取消按钮
        $('.add-n, .mask .add-n').off('click').on('click', function (e) {
            e.preventDefault();
            $('.mask').removeClass('show-add').css('display', 'none');
        });

        // 点击遮罩层关闭
        $('.mask').off('click').on('click', function(e) {
            if (e.target === this) {
                $(this).removeClass('show-add').css('display', 'none');
            }
        });
    });

    // ==================== 删除商品 ====================
    $('.list').on('click', '.delete-btn', function (e) {
        e.preventDefault();
        e.stopPropagation();

        var product_id = $(this).closest('li').data('product_id');
        var productName = $(this).closest('li').find('.product_name').text();

        // 显示确认对话框
        $('#customConfirm').css('display', 'block').addClass('show');

        // 确认删除
        $('#customConfirm .y').off('click').on('click', function () {
            $.ajax({
                url: '/admin/delete_product/' + product_id,
                type: 'GET',
                success: function (response) {
                    $('#customConfirm').removeClass('show').css('display', 'none');
                    alert('商品"' + productName + '"删除成功！');
                    location.reload();
                },
                error: function (error) {
                    console.error(error);
                    $('#customConfirm').removeClass('show').css('display', 'none');
                    alert('删除失败，请稍后再试！');
                }
            });
        });

        // 取消删除
        $('#customConfirm .n').off('click').on('click', function () {
            $('#customConfirm').removeClass('show').css('display', 'none');
        });
    });

    // ==================== 修改商品 ====================
    $('.list').on('click', '.edit-btn', function (e) {
        e.preventDefault();
        e.stopPropagation();

        var $li = $(this).closest('li');
        var product_id = $li.data('product_id');

        // 获取商品信息
        var productName = $li.find('.product_name').text();
        var productBrand = $li.find('.product_brand').text().replace('品牌：', '');
        var productPrice = $li.find('.product_price').text().replace('价格：¥', '');
        var productCategory = $li.data('category') || '户外装备';

        // 填充表单
        $('#edit_product_id').val(product_id);
        $('#edit_name').val(productName);
        $('#edit_derive').val(productBrand);
        $('#edit_price').val(productPrice);
        $('#edit_category').val(productCategory);

        // 更新表单action
        $('#editForm').attr('action', '/admin/edit_product/' + product_id);

        // 显示修改对话框
        $('.mask2').addClass('show-upd').css('display', 'flex');

        // 取消按钮
        $('.upd-n, .mask2 .upd-n').off('click').on('click', function (e) {
            e.preventDefault();
            $('.mask2').removeClass('show-upd').css('display', 'none');
        });

        // 点击遮罩层关闭
        $('.mask2').off('click').on('click', function(e) {
            if (e.target === this) {
                $(this).removeClass('show-upd').css('display', 'none');
            }
        });
    });

    // ==================== 搜索功能 ====================
    function performSearch() {
        var searchTerm = $('.search-ipt').val().trim();

        if (!searchTerm) {
            alert('请输入搜索关键词');
            return;
        }

        $.ajax({
            url: '/admin/search_view',
            type: 'GET',
            data: {search: searchTerm, text: 'product'},
            dataType: 'json',
            success: function (data) {
                console.log('搜索结果:', data);
                var $list = $('.list');
                var $pagination = $('.list').find('.pagination');

                // 移除现有的商品项，但保留分页
                $list.find('li').remove();

                if (data.products && data.products.length > 0) {
                    // 渲染搜索结果
                    $.each(data.products, function (index, product) {
                        var commentCount = product.comment_count || 0;
                        var $listItem = $('<li>').data('product_id', product.id);

                        $listItem.html(`
                            <span class="product_name">${product.name}</span>
                            <span class="product_brand">品牌：${product.derive || ''}</span>
                            <span class="product_price">价格：¥${product.price}</span>
                            <span class="product_category">分类：${product.category || '户外装备'}</span>
                            <span class="product_sales">销量：${product.sales || 0}</span>
                            <a href="javascript:;" class="comment-btn" onclick="showComments(${product.id})">评价(${commentCount})</a>
                            <a href="javascript:;" class="delete-btn">删除</a>
                            <a href="javascript:;" class="edit-btn">修改</a>
                        `);

                        $list.append($listItem);
                    });

                    // 隐藏分页或显示搜索结果提示
                    if ($pagination.length > 0) {
                        $pagination.html('<span style="color: #909399;">搜索结果：共 ' + data.products.length + ' 条</span>');
                    }

                } else {
                    $list.html('<p style="text-align: center; color: #909399; padding: 40px;">没有找到相关商品</p>');
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error('搜索错误:', textStatus, errorThrown);
                $('.list').html('<p style="text-align: center; color: #f56c6c; padding: 40px;">搜索失败，请稍后再试</p>');
            }
        });
    }

    // 搜索图标点击
    $('.search-icon').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        performSearch();
    });

    // 回车键搜索
    $('.search-ipt').on('keypress', function (e) {
        if (e.which === 13) { // 回车键
            e.preventDefault();
            performSearch();
        }
    });

    // 清空搜索
    $('.clear-btn').on('click', function (e) {
        e.preventDefault();
        $('.search-ipt').val('');
        location.reload();
    });

    // ==================== 评价功能 ====================
    window.showComments = function(productId) {
        event.preventDefault();
        event.stopPropagation();

        $.ajax({
            url: '/admin/get_comments/' + productId,
            type: 'GET',
            dataType: 'json',
            success: function (response) {
                var $commentList = $('#commentList');
                $commentList.empty();

                if (response.comments && response.comments.length > 0) {
                    $.each(response.comments, function (index, comment) {
                        var $commentItem = $('<div>').addClass('comment-item').css({
                            'background': '#f8f9fa',
                            'border-radius': '8px',
                            'padding': '16px',
                            'margin-bottom': '12px',
                            'border-left': '3px solid #28b779'
                        });

                        var $commentHeader = $('<div>').css({
                            'display': 'flex',
                            'justify-content': 'space-between',
                            'margin-bottom': '8px'
                        });

                        $commentHeader.append($('<span>').css({
                            'font-weight': '600',
                            'color': '#303133'
                        }).text(comment.username));

                        var $deleteBtn = $('<a>').text('删除').attr({
                            'href': 'javascript:void(0);',
                            'onclick': 'deleteComment(' + comment.id + ', ' + productId + ')'
                        }).css({
                            'color': '#f56c6c',
                            'cursor': 'pointer',
                            'font-size': '13px'
                        });

                        $commentHeader.append($deleteBtn);
                        $commentItem.append($commentHeader);

                        $commentItem.append($('<div>').css({
                            'color': '#606266',
                            'line-height': '1.6',
                            'font-size': '14px'
                        }).text(comment.comment));

                        $commentList.append($commentItem);
                    });
                } else {
                    $commentList.html('<p style="text-align: center; color: #909399; padding: 40px;">暂无评价</p>');
                }

                $('.mask3').css('display', 'flex');
            },
            error: function (error) {
                console.error(error);
                alert('获取评论失败！');
            }
        });
    };

    window.closeCommentDialog = function() {
        $('.mask3').css('display', 'none');
    };

    window.deleteComment = function(commentId, productId) {
        if (confirm('确定要删除这条评价吗？')) {
            $.ajax({
                url: '/admin/delete_comment/' + commentId,
                type: 'GET',
                success: function (response) {
                    alert('删除成功！');
                    showComments(productId);
                },
                error: function (error) {
                    console.error(error);
                    alert('删除失败！');
                }
            });
        }
    };
});
