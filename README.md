# ScanservJS Integration for Home Assistant

A custom Home Assistant integration to control **ScanservJS** directly from Home Assistant.

Create scan profiles, start scans with one click, automatically rename scanned files and execute custom ScanservJS actions.

---

## Why this integration?

ScanservJS already provides a great web interface for scanning. This integration brings ScanservJS directly into Home Assistant, allowing scans to be started from dashboards, automations and scripts while supporting filename prefixes and custom ScanservJS file actions.

---

<img src="https://raw.githubusercontent.com/marioir2001/scanservjs_ha/main/screenshots/dashboard.png" width="800">

---

## Features

- 📄 Scan documents directly from Home Assistant
- 📑 Support for Flatbed and ADF scanners
- 📚 Multi-page PDF scanning
- ✂️ Split multi-page PDFs into individual pages
- 🗑️ Optionally delete the original PDF after successful processing
- 📦 Batch Mode support
- 🎨 Color, Gray and Lineart scanning
- 📏 Paper size selection
- 🔧 ScanservJS filter support
- 📝 Automatic filename prefix
- 📂 Execute ScanservJS file actions after scanning
- 📊 Home Assistant entities for every scan profile
- ⚡ Easy profile management inside Home Assistant
- 🌍 Multi-language support
- 🔄 Automatic file renaming

---

## Requirements

- Home Assistant
- ScanservJS 3.2 or newer
- Scanner supported by ScanservJS
- Working ScanservJS installation
- `pdfseparate` (part of the `poppler-utils` package) for the **Split PDF** file action

## Additional Dependencies

The **Split PDF** file action requires `pdfseparate`, which is included in the `poppler-utils` package.

### Debian / Ubuntu

```bash
sudo apt install poppler-utils
```

### Alpine Linux

```bash
apk add poppler-utils
```

### Docker

If you are using ScanservJS in Docker, make sure the `poppler-utils` package is installed inside the container before using the **Split PDF** action.

---

# Installation

Copy the integration into

```
custom_components/scanservjs
```

Restart Home Assistant.

After restarting:
```
Settings
→ Devices & Services
→ Add Integration
→ ScanservJS
```

### Installation via HACS (Home Assistant Community Store)

1. **Ensure HACS is Installed**
   If you don’t have HACS installed, follow the [HACS installation guide](https://hacs.xyz/docs/use/).

2. **Add the Custom Repository**
   - Open Home Assistant and navigate to **HACS** → **Integrations**.
   - Click the **three dots menu** in the top-right corner and select **Custom repositories**.
   - Add the following repository URL:
     ```
     https://github.com/marioir2001/scanservjs_ha
     ```
   - Select **Integration** as the category.
   - Click **Add**.

3. **Install the Integration**
   - Search for "scanservjs_ha" in the HACS integrations list.
   - Click **Install** to download and install the integration.

4. **Restart Home Assistant**
   to apply changes.

5. **Add the integration via the UI**:
   Go to **Settings** → **Devices & Services** → **Add Integration** and search for "scanservjs_ha".



---

# Configuration

Only three settings are required.

| Setting | Description |
|----------|-------------|
| Name | Name of the integration |
| URL | ScanservJS URL |
| Verify SSL | Enable SSL verification |

Example:

```
http://192.168.1.10:8080
```

---

# Creating Scan Profiles

Profiles define how documents are scanned.

When creating or editing a profile, the integration automatically reads the available scanner settings from ScanservJS. This ensures that only supported options for your scanner are presented in Home Assistant.

Depending on your scanner and ScanservJS configuration, available options may include:

- Scanner source (Flatbed / ADF; Flatbed always uses single-page mode)
- Resolution
- Color mode
- Paper size
- File pipeline
- Image filters
- Batch mode
- Filename prefix
-  Split PDF (optional)
- Delete original PDF after successful processing (optional)
- Scan destination (optional)
  
> **Note**
>
> - **Split PDF** splits multi-page PDFs into individual PDF files before executing any file actions.
> - **Delete original PDF after successful processing** removes the original PDF only after the split operation (if enabled) and all configured file actions have completed successfully.
> - The **Split PDF** feature requires `pdfseparate` from the `poppler-utils` package to be installed on the ScanservJS host.

**Note:** All available scanner options are loaded dynamically from your ScanservJS configuration. If you change scanner settings or update ScanservJS, simply reload the integration to make the new options available.
The available options are automatically detected and may differ depending on your scanner model.

<p align="center">
  <img src="https://raw.githubusercontent.com/marioir2001/scanservjs_ha/main/screenshots/Profil-Edit1.png" width="30%">
  <img src="https://raw.githubusercontent.com/marioir2001/scanservjs_ha/main/screenshots/Profil-Edit2.png" width="30%">
  <img src="https://raw.githubusercontent.com/marioir2001/scanservjs_ha/main/screenshots/Profil-Edit3.png" width="30%">  
</p>


---

# File Actions

One of the biggest features of this integration is support for **ScanservJS Actions**.

File Actions allow custom workflows to be executed automatically after a scan has completed. This makes it easy to move documents, sort images or prepare files for applications such as Paperless-ngx.

File Actions allow you to execute custom JavaScript code after a scan has completed.

Typical use cases include:

- Move PDFs
- Move Images
- Rename files
- Archive documents
- Import into Paperless
- Custom workflows

<img src="https://raw.githubusercontent.com/marioir2001/scanservjs_ha/main/screenshots/actions.png" width="75%">

---

## Example Actions

### move_pdf

Moves PDF file into

```
/targets/pdf
```

---

### move_image

Moves images into

```
/targets/image
```

---

### move_member_application

Moves scanned member applications into

```
/targets/pdf/Mitgliedsantraege
```

---

# Example Action Code in config.local.js

```javascript
actions: [
  {
    name: "move_pdf",
    async execute(fileInfo) {
      // Your custom code
    }
  }
]
```

---

# Example Workflow

<p align="center">
  <img src="https://raw.githubusercontent.com/marioir2001/scanservjs_ha/main/diagramm3.svg" alt="Scan workflow" width="75%">
  
</p>

---

# Dashboard

Every profile creates its own Home Assistant button.

One click starts the complete workflow.

Every scan profile is exposed as a Home Assistant button entity and can be used in dashboards, automations and scripts.

<p align="center">
  <img src="https://raw.githubusercontent.com/marioir2001/scanservjs_ha/main/screenshots/dashboard2.png" width="40%">
  <img src="https://raw.githubusercontent.com/marioir2001/scanservjs_ha/main/screenshots/dashboard4.png" width="40%">
</p>



---

# Troubleshooting

## No Actions available

Verify that your

```
config.local.js
```

contains configured actions.

Restart ScanservJS afterwards.


## Changes are not visible

If you change your `config.local.js` or scanner configuration, restart ScanservJS and reload the Home Assistant integration to refresh the available options.

## Rename does not work

This integration uses the ScanservJS rename API.

Current ScanservJS versions expect

```json
{
  "newName": "filename.pdf"
}
```

---

# Roadmap

Planned features

- HACS support
- Additional scan templates
- More translations
- Improved diagnostics

---

# Contributing

Pull requests are welcome.

If you find a bug, please open an issue.

---

# License

MIT License




