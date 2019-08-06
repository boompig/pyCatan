CatanPlayer = {
	hand: {},

	name: "",

	get_hand: function() {
		return this.hand
	},

	add_to_hand: function(resource) {

	},

	push: function(resource) {
		var s = "";
		var stat_id = "RC";
		var tile_id = "player_tile_" + name.hashCode();

		//$(tile_id).find(".player_stat_rc")text(this.get_num_resources());
	},

	get_num_resources: function() {
		var i = 0;

		$.each(this.hand, function(resource, qty) {
			i += qty;
		});

		return i;
	}
};