"use strict";

const fs = require("node:fs/promises");
const path = require("node:path");

async function moveFile(source, targetDirectory) {
  await fs.mkdir(targetDirectory, { recursive: true });

  const filename = path.basename(source);
  const target = path.join(targetDirectory, filename);

  /*
   * copyFile + unlink statt rename,
   * da Quelle und Ziel auf unterschiedlichen
   * Dateisystemen liegen können.
   */
  await fs.copyFile(source, target);
  await fs.unlink(source);

  return target;
}

module.exports = {
  moveFile,
};