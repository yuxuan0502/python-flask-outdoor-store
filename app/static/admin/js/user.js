$(document).ready(function () {

    var $mask2 = $('.mask2:eq(0)');

    $(".list").on('click', '.edit-btn', function () {
        var $li = $(this).closest('li');
        var user_id = $li.data('user_id');
        var userName = $li.data('name');
        var userAdmin = $li.data('admin');

        // 填充表单
        $("#edit_user_id").val(user_id);
        $("#edit_name").val(userName);
        $("#edit_password").val('');  // 密码默认为空，表示不修改

        // 设置单选按钮
        if (userAdmin == 1) {
            $("#radio2").prop('checked', true);
        } else {
            $("#radio1").prop('checked', true);
        }

        // 更新表单的action
        $("#editUserForm").attr('action', '/admin/edit_user/' + user_id);

        $mask2.css('display', 'flex');
    })

    // 取消按钮点击事件
    $(".det-n").on('click', function (e) {
        e.preventDefault();
        $mask2.css('display', 'none');
    })

    // 确认按钮点击事件 - 防止表单默认提交
    $("#editUserForm").on('submit', function (e) {
        // 让表单正常提交，不需要阻止默认行为
        // 表单会通过 POST 方法提交到 action URL
    })


    // 搜索功能
    function performUserSearch() {
        var searchTerm = $('.search-ipt').val().trim();
        if (searchTerm) {
            $.ajax({
                url: '/admin/search_view',
                type: 'GET',
                data: {search: searchTerm, text: 'user'},
                success: function (data) {
                    console.log(data);
                    var $list = $('.list');
                    $list.empty();

                    if (data.users && data.users.length > 0) {
                        $.each(data.users, function (index, user) {
                            // 创建新的列表项
                            var $listItem = $('<li>').data('user_id', user.id).data('name', user.name).data('admin', user.admin);

                            // 创建并添加用户名
                            var $name = $('<span>').addClass('name').text('用户名：' + user.name);

                            // 密码显示为星号
                            var $pwd = $('<span>').addClass('pwd').text('密码：•••••••');

                            // 用户身份
                            var $admin;
                            if (user.admin == 0) {
                                $admin = $('<span>').addClass('admin user-role').text('身份：普通用户');
                            } else {
                                $admin = $('<span>').addClass('admin admin-role').text('身份：管理员');
                            }

                            $listItem.append($name, $pwd, $admin);

                            var $editBtn = $('<a>').attr('href', 'javascript:;').addClass('edit-btn').text('修改');
                            $listItem.append($editBtn);

                            $list.append($listItem);
                        });
                    } else {
                        $list.html('<p style="text-align: center; color: #909399; padding: 40px;">没有找到相关用户</p>');
                    }

                    console.log('用户搜索成功！');
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.error('Error:', textStatus, errorThrown);
                    $('.list').html('<p style="text-align: center; color: #f56c6c; padding: 40px;">搜索失败，请稍后再试</p>');
                }
            });
        }
    }

    // 搜索图标点击事件
    $('.search-icon').on('click', function (event) {
        event.preventDefault();
        event.stopPropagation();
        performUserSearch();
    });

    // 回车键搜索
    $('.search-ipt').on('keypress', function (e) {
        if (e.which == 13) { // 回车键
            e.preventDefault();
            performUserSearch();
        }
    });

    // 清空搜索按钮
    $('.clear-btn').on('click', function (e) {
        e.preventDefault();
        $('.search-ipt').val('');
        location.reload();
    });

})
