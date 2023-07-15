# Letter Synthesis

## Env file required values

```dotenv
CREDENTIALS_LOCATION=path/to/gcp-oauth-credentials.json
AUTH0_ACCESS_TOKEN=token
```

## Recommended virtual environment setup

```bash
conda create -n letter-synthesis python==3.10
```

Then : 

```bash
conda activate letter-synthesis
```

```bash
pip install -r requirements.txt
```

## Start

```bash
python app.py
```
