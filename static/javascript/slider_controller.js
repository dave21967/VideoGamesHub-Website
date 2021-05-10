function print(data) {
    console.log(data);
}

class SliderController {
    constructor() {
        this.index = 0;
        this.images = $(".slider-image");
        $(this.images).hide();
        $(this.images[0]).show();
    }

    next() {
        this.images = $(".slider-image");
        $(this.images[this.index]).hide();
        print(this.index);
        if(this.index >= (this.images.length-1)) {
            this.index = 0;
        }
        else {
            this.index++;
        }
        $(this.images[this.index]).fadeIn(1000);
    }

    prev() {
        this.images = $(".slider-image");
        $(this.images).hide();
        if(this.index >= 0) {
            this.index--;
        }
        else {
            this.index = (this.images.length-1);
        }
        $(this.images[this.index]).fadeIn(1000);
    }
};


slider = new SliderController();
setInterval(function() {
    slider.next();
}, 5000);