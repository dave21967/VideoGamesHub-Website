function setTheme(tema) {
    console.log(tema);
    if(tema == true) {
        $.ajax({
            url: "/user/set-theme/?theme=dark",
            success: function() {
                changeColors();
            }
        });
    }
    else {
        $.ajax({
            url: "/user/set-theme/?theme=light",
            success: function() {
                changeColors();
            }
        });
    }
}

function changeColors() {
    $.ajax({
        url: "/user/get_cookie/theme",
        success: function(data) {
            console.log(data);
            if(data == "dark") {
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
                $("#switch").checked = true;
            }
            else if(data == "light") {
                $("#h1").css("color", "black");
                $("body").css("backgroundColor", "white");
                $("body").css("color", "black");
                $(".index").css("color", "white");
                $("button").css("color", "black");
                $(".post-title").css("color", "black");
                $("#submit").css("borderColor", "white");
                $("h2").css("color", "black");
                $("#switch").checked = false;
            }
        },
    });
}

$("body").ready(function() {
    changeColors();
});

$("switch").click(function() {
    setTheme(this.checked);
    changeColors();
});