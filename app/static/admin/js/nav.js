$(document).ready(function () {
// 退出登录
//     var text = null;
//     $('.logout').hover(
//         function () {
//             // 鼠标进入时更改文本
//             text = $(this).text();
//             $(this).text("退出登录");
//             $(this).click(function () {
//                 $.ajax({
//                     url: '/logout', // 你的注册路由
//                     type: 'GET',
//                     success: function (data) {
//                         alert('退出成功！'); // 显示提示框
//                         location.replace('/login')
//                     },
//                     error: function (jqXHR, textStatus, errorThrown) {
//                         console.error('请求失败', textStatus, errorThrown);
//                         alert('退出失败，请稍后再试。');
//                     }
//                 });
//             })
//         },function () {
//             // 鼠标离开时还原文本
//             $(this).text(text);
//         }
//     );


    // 先绑定一次点击事件，而不是在每次悬停时都绑定
    $('.logout').on('click', function () {
        $.ajax({
            url: '/logout', // 你的注销路由
            type: 'GET', // 注意：注销操作通常使用POST方法，但这里根据你的需求
            success: function (data) {
                alert('退出成功！'); // 显示提示框
                location.replace('/login'); // 跳转到登录页面
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error('请求失败', textStatus, errorThrown);
                alert('退出失败，请稍后再试。');
            }
        });
    });

    // 然后，只处理悬停和离开事件来更改文本
    $('.logout').each(function () {
        // 为每个.logout元素存储原始文本
        $(this).data('originalText', $(this).text());
    }).hover(
        function () {
            // 鼠标进入时更改文本
            $(this).text("退出登录");
        },
        function () {
            // 鼠标离开时还原文本
            // 从.data()中获取原始文本并设置回去
            $(this).text($(this).data('originalText'));
        }
    );


    // var text;
    // $('.logout').hover(
    //     function () {
    //         // 鼠标进入时更改文本
    //         text = $(this).text();
    //         $(this).text("退出登录");
    //     },
    //     function () {
    //         // 鼠标离开时还原文本
    //         $(this).text(text);
    //     }
    // );
    //

    // 退出登录

    $(".clear-btn").click(function () {
        location.reload();
    })
});