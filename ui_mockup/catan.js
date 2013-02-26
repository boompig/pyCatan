/**
 * Written by Daniel Kats
 */
 
 // prototype a hash function for strings
 // taken from SO, slightly modified to be more readable 
 // http://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript-jquery

String.prototype.hashCode = function(){
    var hash = 0, i, c;
    if (this.length == 0) return hash;
    for (i = 0; i < this.length; i++) {
        c = this.charCodeAt(i);
        hash = ((hash << 5) - hash) + c;
        hash = hash & hash; // Convert to 32bit integer
    }
	
	// admittedly not the best idea, but let's just take absolute value
    return  Math.abs(hash);
};

// namespace for catan stuff

var Catan = {
	//for now, player names come from here
	player_names : ["fred", "george", "ron", "percy"],
	
	// for now, player colors come from here
	player_colors : ["red", "orange", "blue", "white"],

	resources : ["grain", "ore", "brick", "wood", "sheep"],
	
	player_stats : [
		"Victory Points", 
		"Resource Cards", 
		"Development Cards", 
		"Longest Road", 
		"Largest Army"
	],
	
	/**
	 * Preliminary roll functionality
	 */
	roll : function() {
		var r = 0;
		
		for(var i = 0; i < 2; i++) {
			r += Math.floor(Math.random() * 7);
		}
		
		return r;
	},
	
	/**
	 * Change turn in response to 'End Turn' button being pressed.
	 */
	change_turn: function() {
		var next_i = (this.get_current_turn() + 1) % this.player_names.length;
		// remove from current guy
		$(".player_turn").removeClass("player_turn");
		$("#player_tile_" + this.get_player_id(this.player_names[next_i])).addClass("player_turn");
	
		var t = $("#console").text();
		var new_t = "[ROLL] " + String(this.roll());
		$("#console").text(t + "\n" + new_t);
	},
	
	/**
	 * Return an ID for a player based on the name.
	 */
	get_player_id : function(player_name) {
		return player_name.hashCode();
	},
	
	/**
	 * Return the index of the player whose turn it is.
	 */
	get_current_turn: function() {
		var name = $(".player_turn").find(".player_name").text();
		return this.player_names.indexOf(name);
	},
	
	generate_trade_panel: function() {
		var template = $("#templates .trade_resource_tile");
		var parent = $("#trade_panel");
		var resource, copy, tile_id;
	
		for(var i = 0; i < this.resources.length; i++) {
			tile_id = "trade_resource_tile_" + resource;
			resource = this.resources[i];
			copy = $(template).clone().attr("id", tile_id);
			
			// for now, add text to the resource
			$(copy).find(".trade_resource_logo").text(resource);
			
			// and identify the buttons properly
			$(copy).find(".more_trade_button").addClass("more_trade_button_" + resource);
			$(copy).find(".less_trade_button").addClass("less_trade_button_" + resource);
			
			// has to be after added to document
			this.add_trade_button_events(copy);
			$(parent).append(copy);
		}
	},
	
	add_trade_button_events: function(parent) {
		$(parent).find(".more_trade_button").click(function() {
			var val = Number($(parent).find(".trade_resource_amount").text());
			$(parent).find(".trade_resource_amount").text(String(val + 1));
		});
		
		$(parent).find(".less_trade_button").click(function() {
			var val = Number($(parent).find(".trade_resource_amount").text());
			
			if (val > 0) {
				$(parent).find(".trade_resource_amount").text(String(val - 1));
			}
		});
	},
	
	/**
	 * Add all resources to the resource bar.
	 */
	generate_resource_bar: function() {
		//console.log(this.resources);
		
		var resource_container = $("#templates").find(".resource_container");
		
		for (var i = 0; i < this.resources.length; i++) {
			var resource = this.resources[i];
			var new_container = resource_container.clone().attr("id", resource + "_container");
			
			// update logo and count IDs as well
			// also create img source
			$(new_container).find(".resource_logo").attr("id", resource + "_logo").attr("src", resource + "_circle.png");
			$(new_container).find(".resource_count").attr("id", resource + "_count");
		
			$("#resource_bar").append(new_container);
			//console.log(this.resources[i]);
		}
	},
	
	/**
	 * Add all players to the player window
	 */
	generate_player_tiles: function() {
		var player_tile = $("#templates").find(".player_tile");
		
		// cleanup work first
		$(player_tile).find(".template").remove();
		
		for(var i = 0; i < this.player_names.length; i++) {
			var player = this.player_names[i];
			var player_id = this.get_player_id(player);
			var new_tile = $(player_tile).clone().attr("id", "player_tile_" + player_id);
			
			$(new_tile).find(".player_color_square").css("background-color", this.player_colors[i]);
			$(new_tile).find(".player_name").addClass("player_name_" + player_id).text(player);

			// for now, starting player always index 0
			if (i === 0) {
				$(new_tile).addClass("player_turn");
			}
			
			$("#player_tile_container").append(new_tile);
		}
	},
	
	/**
	 * Generate the stats directly to the template.
	 * Run this before processing/replicating the template.
	 */
	generate_template_player_stats: function() {
		var parent = $("#templates .player_stat_container");//$(tile_id).find(".player_stat_container");
		var item = $(parent).find(".player_stat");
		
		for(var i = 0; i < this.player_stats.length; i++) {
			var stat_name = this.player_stats[i];
			var stat_id = stat_name[0] + stat_name.split(" ")[1][0]
			var stat = $(item).clone().addClass("player_stat_" + stat_id).removeClass("template");
			$(stat).find(".player_stat_name").text(stat_name)
			$(parent).append(stat);
		}
	}
}