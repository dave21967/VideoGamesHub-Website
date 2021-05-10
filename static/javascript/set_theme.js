function setDark() {
    $("h1").css("color", "white");
    $("body").css("backgroundColor", "black");
    $("body").css("color", "white");
    $("h2").css("color", "white");
    $(".post-title").css("color", "white");
    $("button").css("color", "white");
    $(".icon").css("filter", "invert(100%)");
    $(".icon").css("-webkit-filter", "invert(100%)");
    $(".date-icon").css("filter", "invert(100%)");
    $(".date-icon").css("-webkit-filter", "invert(100%)");
    $(".comment-title").css("color", "black");
    $(".comment-text").css("color", "black");
    $("#switch").checked = true;
}

function setLight() {
    $("#h1").css("color", "black");
    $("body").css("backgroundColor", "white");
    $("body").css("color", "black");
    $(".index").css("color", "white");
    $("button").css("color", "black");
    $(".post-title").css("color", "black");
    $("#submit").css("borderColor", "white");
    $("h2").css("color", "black");
    $(".comment-title").css("color", "black");
    $(".comment-text").css("color", "black");
    $("#switch").checked = false;
}

function changeColors() {
    $.ajax({
        url: "/user/get_cookie/theme",
        success: function(data) {
            console.log(data);
            if(data == "dark") {
                setDark();
            }
            else if(data == "light") {
                setLight();
            }
        },
    });
}

$("body").ready(function() {
    var isDark = window.matchMedia("(prefers-color-scheme: dark)");
    if(isDark.matches) {
        $.ajax({
            url: "/user/set-theme/?theme=dark",
        });
        setDark();
    }
    else {
        $.ajax({
            url: "/user/set-theme/?theme=light",
        });
        setLight();
    }
    changeColors();
});