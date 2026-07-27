"use strict";

const fs = require("node:fs");
const path = require("node:path");

const actionsDirectory = path.join(__dirname, "actions");

const actions = fs
  .readdirSync(actionsDirectory)
  .filter((file) => file.endsWith(".js"))
  .sort()
  .map((file) => {
    const action = require(path.join(actionsDirectory, file));

    console.log(
      `[scanservjs] Aktion geladen: ${action.name} (${file})`
    );

    return action;
  });

module.exports = {
  actions,
};