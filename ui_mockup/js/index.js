/* global $, Catan, CatanBoard */

$(document).ready(function() {
	//initially hide action tiles
	$("#action_tile_container").hide();
	// initially hide trade panel
	$("#trade_panel").hide();

	// set console to auto-scroll
	// vanilla JS
	var textarea = document.getElementById("console");
	textarea.scrollTop = textarea.scrollHeight;

	set_action_button_events();

	// generate stuff in template
	Catan.generate_template_player_stats();

	// add template to non-template sections
	Catan.generate_resource_bar();
	Catan.generate_player_tiles();
	Catan.generate_trade_panel();
	Catan.generate_buy_buttons();
	CatanBoard.generate_board();
});

function set_trade_button_events() {
	$("#trade_button").click(function() {
		$("#trade_panel").show();
	});

	$(".action_button").not("#trade_button").click(function() {
		$("#trade_panel").hide();
	});
}

function set_buy_button_events() {
	$("#buy_button").click(function() {
		$("#action_tile_container").show();
	});

	$(".action_button").not("#buy_button").click(function() {
		$("#action_tile_container").hide();
	});
}

function set_action_button_events() {
	set_buy_button_events();
	set_trade_button_events();

	$("#end_turn_button").click(function() {
		Catan.change_turn();
	});
}