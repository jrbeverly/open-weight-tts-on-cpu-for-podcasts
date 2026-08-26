python3 -m venv --system-site-packages .venv
.venv/bin/pip install kokoro "misaki[en]" soundfile torch
.venv/bin/python -m spacy download en_core_web_sm

python3 lint.py script.json
.venv/bin/python render.py script.json
