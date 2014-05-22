//加载后自动执行
$(function() {

    // 设置图口高度，此处让 footer 自动填高
    $(window).resize(function() {
        $('div:last').height($(window).height() - $('div:last').offset().top);
    });
    $(window).resize();

    // 修改所有外链接的打开方式：在浏览器的新窗口中打开
    $(document.links).filter(function() {
        return this.hostname != window.location.hostname;
    }).attr('target', '_blank');

});
