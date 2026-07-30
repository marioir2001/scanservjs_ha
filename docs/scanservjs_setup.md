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
