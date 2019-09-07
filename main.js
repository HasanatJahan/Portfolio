$(document).ready(function(){
	// This is sidbar navigation
	// Scroll for home
	$('#home-btn').click(function(e){
		e.preventDefault();
		$("html, body").animate({
			scrollTop: $('#Home').offset().top}, 500); 
	});

	//Scroll for inventory
	$('#inventory-btn').click(function(e){
		e.preventDefault();
		$("html, body").animate({
			scrollTop: $('#Inventory').offset().top}, 500); 
	});

	//Scroll for ML
	$('#ml-btn').click(function(e){
		e.preventDefault();
		$("html, body").animate({
			scrollTop: $('#ML-Progress').offset().top}, 600); 
	});

	// Scroll for Main Nav Contact
	$('#contact-btn').click(function(e){
		e.preventDefault();
		$("html, body").animate({
			scrollTop: $('#Contact').offset().top}, 600); 
	});
	
	//This is about me page navigation 
	// Scroll for Main nav home
	$('#main-home-btn').click(function(e){
		e.preventDefault();
		$("html, body").animate({
			scrollTop: $('#Home').offset().top}, 600); 
	});

	//Scroll for main nav inventory
	$('#main-inventory-btn').click(function(e){
		e.preventDefault();
		$("html, body").animate({
			scrollTop: $('#Inventory').offset().top}, 600); 
	});

	//Scroll for main nav ML
	$('#main-ml-btn').click(function(e){
		e.preventDefault();
		$("html, body").animate({
			scrollTop: $('#ML-Progress').offset().top}, 600); 
	});

	// Scroll for main nav Contact
	$('#main-contact-btn').click(function(e){
		e.preventDefault();
		$("html, body").animate({
			scrollTop: $('#Contact').offset().top}, 600); 
	});
});