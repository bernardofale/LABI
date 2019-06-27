var slider = new Slider("#slider");
slider.on("slide", function(sliderValue) {
	document.getElementById("SliderVal").textContent = sliderValue;
});

