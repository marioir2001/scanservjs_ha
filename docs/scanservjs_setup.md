# Preparing ScanservJS

Before using the Home Assistant ScanservJS integration with the extended file actions, a few changes must be made to your ScanservJS installation.

> **Important**
>
> The Home Assistant integration only communicates with the ScanservJS API.
> All custom file actions (such as **Split PDF**) are executed directly by ScanservJS.
> Therefore, ScanservJS must be prepared before these features can be used.

---

# Requirements

Before continuing, make sure you have:

- A working ScanservJS installation
- ScanservJS **3.2 or newer**
- Home Assistant with the ScanservJS integration installed
- Access to the ScanservJS container or host system

---

# 1. Install additional dependencies

Some file actions require additional software.

## PDF Split

The **Split PDF** action requires `pdfseparate`, which is part of the `poppler-utils` package.

### Debian / Ubuntu

```bash
apt install poppler-utils
```

### Alpine Linux

```bash
apk add poppler-utils
```

### Docker

If you are using ScanservJS in Docker, install the package inside the container or extend the Docker image accordingly.

---

# 2. Copy the custom ScanservJS files

This integration extends ScanservJS with additional file actions.

Copy the provided files from this repository into the appropriate ScanservJS configuration directory. `/etc/scanservjs/`

Example:

```text
/etc/scanservjs/actions/
    move_paperless.js
    split_pdf.js
    move_pdf.js
    ...
```

```text
/etc/scanservjs/
     config.local.js
    ...
```

---

# 3. Configure actions.js

The provided `actions.js` registers the custom file actions that are available inside Home Assistant.

After replacing this file, ScanservJS will automatically detect the new actions during startup.

> **Note**
>
> Existing custom actions should be merged manually if you already modified `actions.js`.

---

# 4. Copy custom action files

Some actions require additional JavaScript files.

Example:

- split_pdf.js
- move_pdf.js
- ...

Copy these files into the same directory as `actions.js`.

> **Important**
>
> Do not rename these files unless you also update the references inside `actions.js`.

---

# 5. Configure targets.js

The optional `targets.js` file defines the available destination directories that can be used by custom ScanservJS file actions.

Example:

```javascript
"use strict";

module.exports = {
  pdf: "/targets/pdf",
  image: "/targets/image",
  memberApplication: "/targets/pdf/MemberApplications",
  invoice: "/targets/pdf/Invoices",
  paperless: "/targets/paperless",
};
```

## Using a target

Defining a target in `targets.js` is **not enough**.

A custom file action must also reference that target. Otherwise, the destination will **not** appear in Home Assistant.

Example: `move_pdf.js`

```javascript
"use strict";

const TARGETS = require("../config/targets");
const { PDF_EXTENSIONS } = require("../config/filetypes");
const { createMoveAction } = require("../lib/create_move_action");

module.exports = createMoveAction({
  name: "move_pdf",
  targetDirectory: TARGETS.pdf,
  allowedExtensions: PDF_EXTENSIONS,
});
```

In this example, the action uses the `pdf` target defined in `targets.js`.

When Home Assistant reads the available file actions, it automatically detects that this action supports the **pdf** destination and makes it available in the profile editor.

> **Important**
>
> Every destination defined in `targets.js` requires at least one corresponding file action.
> Unused targets are ignored and will not be shown in Home Assistant.

## How it works

The **property name** becomes the destination shown in Home Assistant.

The **value** specifies the directory where the selected file action should store the file.

| Target | Directory |
|---------|-----------|
| `pdf` | `/targets/pdf` |
| `image` | `/targets/image` |
| `memberApplication` | `/targets/pdf/MemberApplications` |
| `invoice` | `/targets/pdf/Invoices` |
| `paperless` | `/targets/paperless` |

> **Note**
>
> You can freely add, remove or rename targets to match your own folder structure.
>
> After changing `targets.js`, restart the ScanservJS container so the new destinations become available in Home Assistant.

# 6. Restart ScanservJS

After all files have been copied, restart the ScanservJS container.

Example:

```bash
docker restart <scanservjs-container>
```

---

# 7. Verify the installation

After restarting ScanservJS:

- Open Home Assistant.
- Edit or create a Scan Profile.
- Verify that:
    - File Actions are available.
    - Scan Destinations are listed.
    - Split PDF can be selected.
    - The integration connects successfully.

---

# Troubleshooting

## Split PDF is missing

Verify that:

- `pdfseparate` is installed.
- `split_pdf.js` exists.
- `actions.js` has been updated.
- ScanservJS has been restarted.

---

## Scan Destinations are empty

Verify that:

- `targets.js` exists.
- The file contains valid JavaScript.
- ScanservJS has been restarted.

---

## File Actions are missing

Verify that:

- The custom action files have been copied correctly.
- `actions.js` references them correctly.
- ScanservJS has been restarted.

---

# Notes

This guide only covers the ScanservJS preparation.

For installation and configuration of the Home Assistant integration, please refer to the main **README.md**.
