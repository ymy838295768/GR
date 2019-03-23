$(function () {

    initTopSwiper();
    initTopMenu();

})


function initTopSwiper() {
    var swiper = new Swiper("#topSwiper",{
        autoplay: 3000,
        pagination: '.swiper-pagination'
    })
}

function initTopMenu() {
    var swiper = new Swiper("#swiperMenu",{
        slidesPerView: 3
    })
}