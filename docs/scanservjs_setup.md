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

## 2. Copy the custom ScanservJS files

This integration extends ScanservJS with additional file actions, configuration files and helper libraries.

Copy the contents of the repository's `scanservjs` directory to your ScanservJS configuration directory:

```text
Repository
scanservjs/
├── actions/
├── config/
└── lib/

↓

/etc/scanservjs/
├── actions/
├── config/
└── lib/
```

For example:

```text
/etc/scanservjs/
|── config.local.js
├── actions/
│   ├── move_image.js
│   ├── move_member_application.js
│   ├── move_paperless.js
│   ├── move_pdf.js
│   └── split_pdf.js
│
├── config/
│   ├── filetypes.js
│   ├── paths.js
│   └── targets.js
│
└── lib/
    ├── create_move_action.js
    └── file.js
```

> **⚠️ Backup recommended**
>
> Before replacing existing files, create a backup of your `/etc/scanservjs` directory.
>
> If you already use custom ScanservJS actions or configuration files, merge your changes instead of simply overwriting the existing files.


## 🔒 Required action

The following files are required for the Home Assistant integration and should not be removed unless you know exactly what you are doing.

`split_pdf.js` is the only action required by the integration for the Split PDF feature. All other move_*.js actions are examples and may be customized or removed.

> **Important**
>
> - Do **not** rename this file.
> - Do **not** delete this file if you want to use the **Split PDF** feature.
> - This action requires `pdfseparate` from the `poppler-utils` package.

---

## 💡 Example actions

The supplied `move_*.js` actions are examples intended to help you get started. Feel free to adapt them to your own workflow or replace them with custom actions.

For example:

- `move_pdf.js`
- `move_image.js`
- `move_paperless.js`
- `move_member_application.js`

You may:

- Rename them
- Modify them
- Delete them
- Create your own actions

Each action simply demonstrates how to move files to one of the configured scan targets.

---

# 3. Configure targets.js

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

# 4. Restart ScanservJS

After all files have been copied, restart the ScanservJS container.

Example:

```bash
docker restart <scanservjs-container>
```

---

# 5. Verify the installation

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
