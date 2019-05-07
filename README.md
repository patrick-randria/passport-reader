# Simple passport reader
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Package repository](https://img.shields.io/badge/packages-repository-b956e8.svg?style=flat-square)](https://github.com/patrick-randria/passport-reader)

A very simple python backend API to extract text informations from a passport image file.

## IMPORTANT NOTICE
SCANNING IDENTITY DOCUMENTS IS IN MOST CASES RESTRICTED BY LAW. OBSERVE THE APPLICABLE LAWS USING THIS TOOL. THE COPYRIGHT HOLDER IS NOT IN ANY WAY LIABLE FOR UNLAWFUL USAGE OF THIS TOOL.
THIS APP ONLY SERVES TO DEMONSTRATE THE BASIC USE OF [PassportEye](https://pypi.org/project/PassportEye/) TO SCAN THE MACHINE READABLE ZONES (MRZ) THEN IMPROVE THE RESULT WITH [Tesseract OCR](https://github.com/tesseract-ocr/tesseract).

## Prerequisite
First of all, make sure you have [Docker](https://docs.docker.com/engine/installation/) Engine installed in your system.

## Quickstart
Just clone the repo and build the app with docker compose.
```
docker-compose up --build
```
## Endpoint `http://0.0.0.0:5000/process`
This is the only one endpoint of this app and accept one `POST` parameter :
- `imagefile` : An image file of the passport. For mobile app, we can use the camera.

##### A sample response:
```json
{
    "country": "Madagascar",
    "country_code": "MDG",
    "first_name": "Patrick",
    "last_name": "RANDRIA",
    "nationality": "Madagascar",
    "number": "X00X00000",
    "sex": "M"
}
```

## License

This tool is is available under the The MIT License.
Further details see LICENSE file.
