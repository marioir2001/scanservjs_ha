"use strict";

const path = require("node:path");
const { moveFile } = require("./file");

function createMoveAction({
  name,
  targetDirectory,
  allowedExtensions,
}) {
  if (!name) {
    throw new Error("Action-Name fehlt.");
  }

  if (!targetDirectory) {
    throw new Error(`${name}: Zielverzeichnis fehlt.`);
  }

  return {
    name,

    async execute(fileInfo) {
      const source = fileInfo.fullname;
      const extension = path.extname(source).toLowerCase();

      if (
        allowedExtensions &&
        !allowedExtensions.has(extension)
      ) {
        throw new Error(
          `Die Aktion ${name} akzeptiert diesen Dateityp nicht. Erhalten: ${
            extension || "unbekannter Dateityp"
          }`
        );
      }

      const target = await moveFile(
        source,
        targetDirectory
      );

      console.log(
        `[scanservjs] Datei durch Aktion ${name} verschoben: ${target}`
      );

      return target;
    },
  };
}

module.exports = {
  createMoveAction,
};