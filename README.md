# pd-zabbix-integration
Python script to configure integration between Zabbix actions and Pagerduty

## What does this project do?
For each filtered Zabbix hostgroup:
* creates Pagerduty escalation policy
* creates Pagerduty service
* creates Pagerduty integration key for the service
* creates Zabbix media type
* configures Zabbix media into zbxservice user (using the integration key)
* creates Zabbix action

## Dependencies
This project uses [pypd](https://github.com/PagerDuty/pagerduty-api-python-client) and [pyzabbix](https://github.com/lukecyca/pyzabbix).
```
pip install -r requirements
```

# Contributing
Just open a PR. We love PRs!

## License
MIT