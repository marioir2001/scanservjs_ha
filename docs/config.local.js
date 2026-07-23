const fs = require("node:fs/promises");
const path = require("node:path");

const PDF_TARGET = "/targets/pdf";
const IMAGE_TARGET = "/targets/image";
const MEMBER_APPLICATION_TARGET = "/targets/pdf/Mitgliedsantraege";

async function moveFile(source, targetDirectory) {
  await fs.mkdir(targetDirectory, { recursive: true });

  const filename = path.basename(source);
  const target = path.join(targetDirectory, filename);

  /*
   * copyFile + unlink wird statt rename verwendet, weil Quelle und Ziel
   * auf unterschiedlichen Docker-Mounts beziehungsweise Dateisystemen
   * liegen können.
   */
  await fs.copyFile(source, target);
  await fs.unlink(source);

  return target;
}

module.exports = {
  actions: [
    {
      name: "move_pdf",

      /**
       * Verschiebt die angegebene Datei in den PDF-Zielordner.
       *
       * Aufruf über die API:
       * POST /api/v1/files/{filename}/actions/move_pdf
       */
      async execute(fileInfo) {
        const source = fileInfo.fullname;
        const extension = path.extname(source).toLowerCase();

        if (extension !== ".pdf") {
          throw new Error(
            `Die Aktion move_pdf akzeptiert nur PDF-Dateien. Erhalten: ${
              extension || "unbekannter Dateityp"
            }`
          );
        }

        const target = await moveFile(source, PDF_TARGET);

        console.log(
          `[scanservjs] PDF durch Aktion move_pdf verschoben: ${target}`
        );

        return target;
      },
    },

    {
      name: "move_member_application",

      /**
       * Verschiebt Mitgliedsanträge in einen eigenen Unterordner.
       *
       * Ziel:
       * /targets/pdf/Mitgliedsantraege
       *
       * Aufruf über die API:
       * POST /api/v1/files/{filename}/actions/move_member_application
       */
      async execute(fileInfo) {
        const source = fileInfo.fullname;
        const extension = path.extname(source).toLowerCase();

        if (extension !== ".pdf") {
          throw new Error(
            `Die Aktion move_member_application akzeptiert nur PDF-Dateien. Erhalten: ${
              extension || "unbekannter Dateityp"
            }`
          );
        }

        const target = await moveFile(
          source,
          MEMBER_APPLICATION_TARGET
        );

        console.log(
          `[scanservjs] Mitgliedsantrag verschoben: ${target}`
        );

        return target;
      },
    },

    {
      name: "move_image",

      /**
       * Verschiebt die angegebene Datei in den Bilder-Zielordner.
       *
       * Aufruf über die API:
       * POST /api/v1/files/{filename}/actions/move_image
       */
      async execute(fileInfo) {
        const source = fileInfo.fullname;
        const extension = path.extname(source).toLowerCase();

        const imageExtensions = new Set([
          ".jpg",
          ".jpeg",
          ".png",
          ".tif",
          ".tiff",
          ".webp",
        ]);

        if (!imageExtensions.has(extension)) {
          throw new Error(
            `Die Aktion move_image akzeptiert nur Bilddateien. Erhalten: ${
              extension || "unbekannter Dateityp"
            }`
          );
        }

        const target = await moveFile(source, IMAGE_TARGET);

        console.log(
          `[scanservjs] Bild durch Aktion move_image verschoben: ${target}`
        );

        return target;
      },
    },
  ],
};