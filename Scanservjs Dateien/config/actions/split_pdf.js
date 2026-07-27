"use strict";

const fs = require("node:fs/promises");
const path = require("node:path");
const { execFile } = require("node:child_process");
const { promisify } = require("node:util");

const { SPLIT_TARGET } = require("../config/paths");

const execFileAsync = promisify(execFile);

module.exports = {
  name: "split_pdf",

  async execute(fileInfo) {
    const source = fileInfo.fullname;
    const extension = path.extname(source).toLowerCase();

    if (extension !== ".pdf") {
      throw new Error(
        `split_pdf unterstützt nur PDF-Dateien: ${source}`
      );
    }

    const outputDirectory = path.dirname(source);
    const baseName = path.basename(source, extension);

    const jobId = `${Date.now()}-${Math.random()
      .toString(36)
      .slice(2, 10)}`;

    const workDirectory = path.join(
      SPLIT_TARGET,
      jobId
    );

    const outputPattern = path.join(
      workDirectory,
      `${baseName}_%03d.pdf`
    );

    await fs.mkdir(workDirectory, {
      recursive: true,
    });

    try {
      console.log(`[split_pdf] Quelldatei: ${source}`);
      console.log(`[split_pdf] Arbeitsordner: ${workDirectory}`);

      await execFileAsync(
        "/usr/bin/pdfseparate",
        [
          source,
          outputPattern,
        ],
        {
          timeout: 120000,
          maxBuffer: 10 * 1024 * 1024,
        }
      );

      const directoryEntries = await fs.readdir(
        workDirectory,
        {
          withFileTypes: true,
        }
      );

      const generatedFiles = directoryEntries
        .filter(
          (entry) =>
            entry.isFile() &&
            entry.name.toLowerCase().endsWith(".pdf")
        )
        .map((entry) => entry.name)
        .sort();

      if (generatedFiles.length === 0) {
        throw new Error(
          "pdfseparate hat keine PDF-Dateien erzeugt."
        );
      }

      /*
       * Vor dem Verschieben werden alle Dateinamen geprüft.
       * Bei einem Namenskonflikt wird abgebrochen, bevor eine
       * der erzeugten Dateien verschoben wird.
       */
      for (const filename of generatedFiles) {
        const targetFile = path.join(
          outputDirectory,
          filename
        );

        try {
          await fs.access(targetFile);

          throw new Error(
            `Die Zieldatei existiert bereits: ${targetFile}`
          );
        } catch (error) {
          if (error.code !== "ENOENT") {
            throw error;
          }
        }
      }

      const outputFiles = [];

      for (const filename of generatedFiles) {
        const temporaryFile = path.join(
          workDirectory,
          filename
        );

        const targetFile = path.join(
          outputDirectory,
          filename
        );

        await fs.rename(
          temporaryFile,
          targetFile
        );

        outputFiles.push(targetFile);

        console.log(
          `[split_pdf] Erzeugt: ${targetFile}`
        );
      }

      console.log(
        `[split_pdf] Erfolgreich: ${outputFiles.length} Datei(en)`
      );

      return {
        success: true,
        action: "split_pdf",
        original: source,
        files: outputFiles,
        count: outputFiles.length,
      };
    } catch (error) {
      console.error(
        `[split_pdf] Fehler: ${error.message}`
      );

      throw new Error(
        `PDF konnte nicht aufgeteilt werden: ${error.message}`
      );
    } finally {
      await fs.rm(workDirectory, {
        recursive: true,
        force: true,
      });

      /*
       * Der übergeordnete Split-Ordner wird nur entfernt,
       * wenn kein anderer Auftrag darin arbeitet.
       */
      try {
        const remainingEntries = await fs.readdir(
          SPLIT_TARGET
        );

        if (remainingEntries.length === 0) {
          await fs.rmdir(SPLIT_TARGET);

          console.log(
            `[split_pdf] Leeren Split-Ordner entfernt: ${SPLIT_TARGET}`
          );
        }
      } catch (error) {
        if (
          error.code !== "ENOENT" &&
          error.code !== "ENOTEMPTY"
        ) {
          console.warn(
            `[split_pdf] Split-Ordner konnte nicht entfernt werden: ` +
              `${error.message}`
          );
        }
      }
    }
  },
};