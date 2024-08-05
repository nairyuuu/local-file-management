# Unsecured file download system with file from local host

## Prerequisites

* Ngrok
* Python3

## Run manual

Edit the desired folder in config.py

Install the python libraries needed:
```shell
pip install -r .\requirements.txt
```
Run the server:
```bash
python app.py
```

## Deploy to Internet using ngrok

```bash
ngrok http http://localhost:5000
```
