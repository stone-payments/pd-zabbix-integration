# pd-zabbix-integration
Configures integration between Zabbix actions and Pagerduty

## What does this project do?
For each filtered Zabbix hostgroup:
* create Pagerduty escalation policy
* create Pagerduty service
* create Pagerduty integration key for the service
* create Zabbix media type
* configure Zabbix media into zbxservice user (using the integration key)
* create Zabbix action

## Dependencies
This project uses [pypd](https://github.com/PagerDuty/pagerduty-api-python-client) and [pyzabbix](https://github.com/lukecyca/pyzabbix).
```
pip install -r requirements
```

# Contributing
Just open a PR. We love PRs!

## License
MIT