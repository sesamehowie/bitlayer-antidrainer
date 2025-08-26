**BITLAYER ANTIDRAIN**

**CONFIGURATION**

Set up input_data files:
private_keys.txt
proxies.txt (format: user:pass@ip:port). ONLY HTTP FOR NOW

**VIRTUAL ENVIRONMENT**

Interpreter : python 3.12 or newer

**Activation**

Windows:
```
python3 -m venv .venv
.venv/Scripts/Activate.ps1
```

Linux(Debian):
```
python3 -m venv .venv
. .venv/bin/activate
```

**INSTALL DEPENDENCIES**

```
pip install -r requirements.txt
```

*RUN*

```
python main.py
```
