"use strict";

const TARGETS = require("../config/targets");
const { IMAGE_EXTENSIONS } = require("../config/filetypes");
const { createMoveAction } = require("../lib/create_move_action");

module.exports = createMoveAction({
  name: "move_image",
  targetDirectory: TARGETS.image,
  allowedExtensions: IMAGE_EXTENSIONS,
});