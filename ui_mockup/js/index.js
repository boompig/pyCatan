/* global $, Catan, CatanBoard, Vue */

new Vue({
	el: "#main",
	data: {
		mapEditorOn: false,

		showTradePanel: false,
	},
	methods: {
		toggleMapEditor: function() {
			this.mapEditorOn = !this.mapEditorOn;
			if(this.mapEditorOn) {
				console.log("turned map editor on");
			}
		}
	},
	mounted: function() {
		const textarea = document.getElementById("console");
		if(textarea) {
			textarea.scrollTop = textarea.scrollHeight;
		}

		Catan.generate_trade_panel();
	}
});

$(document).ready(function() {
	//initially hide action tiles
	$("#action_tile_container").hide();
	// initially hide trade panel

	// set console to auto-scroll
	// vanilla JS

	set_action_button_events();

	// generate stuff in template
	Catan.generate_template_player_stats();

	// add template to non-template sections
	Catan.generate_resource_bar();
	Catan.generate_player_tiles();
	Catan.generate_trade_panel();
	Catan.generate_buy_buttons();
	CatanBoard.generate_board();
	const lattice = CatanBoard.compute_lattice();
	console.log(lattice);
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