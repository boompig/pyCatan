var CatanBoard = {
	
	// as it maps this way...
	board_layout: [3, 5, 5, 5, 4],
	
	/**
	 * Generate some kind of board
	 */
	generate_board: function() {
		console.log("called");
	
		var board = $("#board");
		var hex = $("#templates").find(".hex");
		var hex_row, hex_clone, j;
		
		for (var i = 0; i < this.board_layout.length; i++) {
			hex_row = $(document.createElement("div")).addClass("hex_row");
			$(board).append(hex_row);
			
			for(j = 0; j < 5 - this.board_layout[i]; j++) {
				hex_clone = $(hex).clone().addClass("transparent");
				
				if (j % 2 === 0) {
					$(hex_clone).addClass("even");
				}
				
				$(hex_row).append(hex_clone);
			}
			
			for (; j < this.board_layout[i]; j++) {
				hex_clone = $(hex).clone();
				
				if (j % 2 === 0) {
					$(hex_clone).addClass("even");
				}
				$(hex_row).append(hex_clone);
			}
		}
	}
};