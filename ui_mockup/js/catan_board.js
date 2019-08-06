/* global $ */
/* exported CatanBoard */

/**
 * Generate the Catan board as HTML elements
 */

const CatanBoard = {

	/*
	 * The numbers refer to the number of hexes in each row
	 * But a row in this case is a grouping of two adjacent rows
	 * So the first value (3) = (1) + (2)
	 */
	board_layout: [3, 5, 5, 5, 4],

	// different from the above in that it doesn't double-count
	numTrueRows: 9,

	numHexes: 19,

	// see hex.css
	settlementDotRadius: 10,

	// filled in when generate_board is called
	// mapping from hexId to array of hexes
	adjacentHexes: {},

	// mapping from hexId to hex
	hexes: {},

	// mapping from (trueRow, col) to hex
	board: {},

	/**
	 * Generate some kind of board
	 * "even" means those hexes that are on even rows
	 * the rows are generated 2 at a time
	 *
	 * Store the true row value in data-true-row
	 */
	generate_board: function() {
		const $board = $("#board");
		const hex = $("#templates").find(".hex");
		var hex_row, hex_clone, j;
		// not guaranteed to be in any kind of order, just used for uniqueness
		let hexId = 0;

		for (let i = 0; i < this.board_layout.length; i++) {
			hex_row = $(document.createElement("div")).addClass("hex_row");
			$($board).append(hex_row);

			for(j = 0; j < 5 - this.board_layout[i]; j++) {
				hex_clone = $(hex).clone().addClass("transparent");

				if (j % 2 === 0) {
					$(hex_clone).addClass("even");
				}

				$(hex_row).append(hex_clone);
			}

			for (; j < this.board_layout[i]; j++) {
				hex_clone = $(hex).clone().attr("data-hex-id", hexId)
					.attr("data-col", j)
					.attr("data-layout-row", i);
				this.hexes[hexId] = hex_clone;
				let trueRow;

				if (j % 2 === 0) {
					trueRow = 2 * i;
					$(hex_clone).addClass("even").attr("data-true-row", trueRow);
				} else {
					trueRow = (2 * i - 1);
					$(hex_clone).addClass("odd").attr("data-true-row", trueRow);
				}
				this.board[`${trueRow},${j}`] = hex_clone;

				$(hex_row).append(hex_clone);
				hexId++;
			}
		}

		// before exiting, fill in adjacent hexes
		for(let hexId = 0; hexId < this.numHexes; hexId++) {
			this.adjacentHexes[hexId] = [];
			// get the hex
			let $hex = this.hexes[hexId];
			const trueRow = Number($hex.attr("data-true-row"));
			const col = Number($hex.attr("data-col"));
			// clockwise starting from 12 o'clock position
			// guarantees that this.adjacentHexes will be in predictable order
			const adj = [
				[trueRow - 2, col],
				[trueRow - 1, col + 1],
				[trueRow + 1, col + 1],
				[trueRow + 2, col],
				[trueRow + 1, col - 1],
				[trueRow - 1, col - 1],
			];
			for(let coord of adj) {
				if(this.board[coord]) {
					this.adjacentHexes[hexId].push(this.board[coord]);
				}
			}
		}
		console.log(this.adjacentHexes);
	},

	/**
	 * Get the coordinates for each node on a settlement
	 */
	compute_lattice: function() {
		const board = $("#board");
		const hexLattice = [];

		// construct the in-order hex lattice
		$(board).find(".hex:not(.transparent)").each((i, elem) => {
			const trueRow = Number($(elem).attr("data-true-row"));
			if(!hexLattice[trueRow]) {
				hexLattice[trueRow] = [];
			}
			hexLattice[trueRow].push(elem);

		});

		// for each hexId, add vertices in clockwise order starting from top left
		const vertexMap = {};

		for(let hexId = 0; hexId < this.numHexes; hexId++) {
			let $hex = $("#board").find(`[data-hex-id=${hexId}]`);
			const $left = $hex.find(".left");
			const leftX = $left.position().left;
			const rightX = $hex.width() + leftX;
			const h = $hex.height();
			const topY = $left.position().top;
			const $middle = $hex.find(".middle");

			const leftMiddle = new Point(
				leftX,
				topY + h / 2
			);

			const rightMiddle = new Point(
				rightX,
				topY + h / 2
			);

			const topLeft = new Point(
				$middle.position().left,
				topY
			);

			const topRight = new Point(
				$middle.position().left + $middle.width(),
				topY,
			);

			const bottomLeft = new Point(
				$middle.position().left,
				topY + h
			);

			const bottomRight = new Point(
				$middle.position().left + $middle.width(),
				topY + h
			);

			vertexMap[hexId] = [
				topLeft,
				topRight,
				rightMiddle,
				bottomRight,
				bottomLeft,
				leftMiddle
			];
		}

		// because of the way I'm calculating the coordinates the values don't always sync up
		// so now we have to construct a backwards map from each coordinate delete any overlapping coordinates
		const nodes = [];

		for(let hexId = 0; hexId < this.numHexes; hexId++) {
			for(let vertex of vertexMap[hexId]) {
				// if this vertex has not been drawn, then draw it
				// NOTE: in practice only need to check adjacent hexes
				// but that's not important here

				let found = false;
				for(let vertex2 of nodes) {
					if(vertex.distanceTo(vertex2) <= this.settlementDotRadius) {
						found = true;
						break;
					}
				}
				if(!found) {
					nodes.push(vertex);
				}
			}
		}

		for(let node of nodes) {
			let elem = $("<div></div>")
				.addClass("future-settlement-node")
				.css("left", node.x - this.settlementDotRadius)
				.css("top", node.y - this.settlementDotRadius);
			$("#board").append(elem);
		}

		return hexLattice;
	}
};

class Point {
	constructor(x, y) {
		this.x = x;
		this.y = y;
	}

	distanceTo(p2) {
		return Math.sqrt((this.x - p2.x) ** 2 + (this.y - p2.y) ** 2);
	}
}