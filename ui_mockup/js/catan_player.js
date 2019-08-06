/* global $ */
/* exported CatanPlayer */

class CatanPlayer {
	constructor() {
		this.hand = {};
		this.name = "";
	}

	get_hand() {
		return this.hand;
	}

	add_to_hand(resource) {
		throw new Error("not implemented");
	}

	push(resource) {
		const s = "";
		const stat_id = "RC";
		const tile_id = "player_tile_" + name.hashCode();

		//$(tile_id).find(".player_stat_rc")text(this.get_num_resources());
		throw new Error("not implemented");
	}

	get_num_resources() {
		var i = 0;

		$.each(this.hand, function(resource, qty) {
			i += qty;
		});

		return i;
	}
}