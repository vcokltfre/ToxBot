# vcokltfre/ToxBot

### A Discord bot for toxicity detection

Config structure in `config/config.py`:
```py
name = 'ToxBot'
log_level = 'info'
log_type = 'text'
token = 'token'
hook = 'webhook'
dev_ids = [discord_id]

logs = log_channel_id

max_urls = [
    "http://example.com/model/predict"
]

dbcreds = {
    "host":"localhost",
    "port":3131,
    "user":"root",
    "password":"password",
    "db":"toxbot"
}
```

Example guild in `./guilds/`:
```yml
prefix: "!"
alerts: 781890407994359849

blacklist:
  channels:
    - 781890407994359849 # categories work too
  roles:
    - 762732182170370049
  users:
    - null

levels:
  toxic:
    alert: 0.9
    delete: 0.95
  severe_toxic:
    alert: 0.98
    delete: 0.999
  obscene:
    alert: 0.98
    delete: 0.999
  threat:
    alert: 0.98
    delete: 0.999
  insult:
    alert: 0.98
    delete: 0.999
  identity_hate:
    alert: 0.8
    delete: 0.95

buckets:
  mode: bucket-only # modes: 'all' 'bucket-only'
  duration: 120
  count: 3
```