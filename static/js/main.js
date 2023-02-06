(function($) {

	"use strict";

	 $('.label.ui.dropdown')
  .dropdown();

		$('.no.label.ui.dropdown')
		  .dropdown({
		  useLabels: false
		});

		$('.ui.button').on('click', function () {
		  $('.ui.dropdown')
		    .dropdown('restore defaults')
		})

	 
})(jQuery);

$(function () {
	var pagination = $(".pagination");
  
	function switchToNext() {
	  var _this = $(this);
  
	  if (_this.hasClass("active")) return false;
	  else {
		$(".pagination-active").removeClass("pagination-active");
		_this.addClass("pagination-active");
	  }
	}
  
	pagination.on("click", switchToNext);
  });