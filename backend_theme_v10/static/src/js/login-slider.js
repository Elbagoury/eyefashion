odoo.define('backend_theme_v10.login', function (require) {
$(function(){
    $('#login-v2-intro').vegas({
        overlay: "/backend_theme_v10/static/src/img/overlay.png",
        delay:5000,
        //shuffle:true,
        timer:false,
        slides: [
            { src: '/backend_theme_v10/static/src/img/wallpaper3.jpg' },
            { src: '/backend_theme_v10/static/src/img/wallpaper4.jpg' },
            { src: '/backend_theme_v10/static/src/img/wallpaper1.jpg' }
        ]
    });
});


});