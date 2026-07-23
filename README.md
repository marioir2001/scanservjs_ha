# ScanservJS Integration for Home Assistant

A custom Home Assistant integration to control **ScanservJS** directly from Home Assistant.

Create scan profiles, start scans with one click, automatically rename scanned files and execute custom ScanservJS actions.

---

## Why this integration?

ScanservJS already provides a great web interface for scanning. This integration brings ScanservJS directly into Home Assistant, allowing scans to be started from dashboards, automations and scripts while supporting filename prefixes and custom ScanservJS file actions.

---

<img src="screenshots/dashboard.png" width="800">

---

## Features

- 📄 Scan documents directly from Home Assistant
- 📑 Support for Flatbed and ADF scanners
- 📚 Multi-page PDF scanning
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

### HACS (Coming Soon)

Not yet available.



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

- Scanner source (Flatbed / ADF)
- Resolution
- Color mode
- Paper size
- File pipeline
- Image filters
- Batch mode
- Filename prefix
- File action
  
**Note:** All available scanner options are loaded dynamically from your ScanservJS configuration. If you change scanner settings or update ScanservJS, simply reload the integration to make the new options available.

The available options are automatically detected and may differ depending on your scanner model.

<p align="center">
  <img src="screenshots/Profil-Edit1.png" width="30%">
  <img src="screenshots/Profil-Edit2.png" width="30%">
  <img src="screenshots/Profil-Edit3.png" width="30%">
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

<img src="screenshots/actions.png" width="75%">

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
  <img src="diagramm3.svg" alt="Scan workflow" width="75%">
</p>

---

# Dashboard

Every profile creates its own Home Assistant button.

One click starts the complete workflow.

Every scan profile is exposed as a Home Assistant button entity and can be used in dashboards, automations and scripts.

<p align="center">
  <img src="screenshots/dashboard2.png" width="40%">
  <img src="screenshots/dashboard3.png" width="40%">
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




