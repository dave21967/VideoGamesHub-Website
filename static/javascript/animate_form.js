var width = window.innerWidth;

if(width <= 600) {
    $("#form").css("opacity", "0.2");
    $("#form").animate({paddingLeft: '0%', opacity: '1'}, 2000);
}
else {
    $("#form").css("opacity", "0.2");
    $("#form").animate({paddingLeft: '35%', opacity: '1'}, 2000);
}