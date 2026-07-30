"use strict";

const TARGETS = require("../config/targets");
const { PDF_EXTENSIONS } = require("../config/filetypes");
const { createMoveAction } = require("../lib/create_move_action");

module.exports = createMoveAction({
  name: "move_paperless",
  targetDirectory: TARGETS.paperless,
  allowedExtensions: PDF_EXTENSIONS,
});