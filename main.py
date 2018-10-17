from pyzabbix import ZabbixAPI
import sys
import getpass
import pypd

pypd.api_key = getpass.getpass("Pagerduty API key:")
username = raw_input("Zabbix Username:")
password = getpass.getpass("Zabbix Password:")
url = "https://monitoracao.stone.com.br:10443"
hostgroup_filter = "" # Zabbix hostgroup filtering. Example: "Databases/*/*"
team_id = "" # Team ID for escalation policy

try:
  zapi = ZabbixAPI(url)
  zapi.login(username,password)
  print("Connected to Zabbix API Version %s" % zapi.api_version())

except Exception, e:
  sys.stderr.write("Caught exception (%s)\n" % e)
  exit

## For each Zabbix's hostgroup
for hostgroup in zapi.hostgroup.get(output="extend",search={"name":hostgroup_filter},searchWildcardsEnabled=1):
    hostgroup_name_replaced = hostgroup["name"].replace("/","_"),    

    ## Create Escalation policy at Pagerduty 
    try:
      ep = pypd.EscalationPolicy.create(
        data={
          "name": '%s' % hostgroup_name_replaced,
          "escalation_rules": [
#            {
#              "escalation_delay_in_minutes": 10,
#              "targets": [
#                {
#                  "type": "user",
#                  "id": "XXXXXX"
#                },
#                {
#                  "type": "user",
#                  "id": "YYYYYY"
#                },
#                {
#                  "type": "user",
#                  "id": "ZZZZZZ"
#                }
#              ]
#            },
            {
              "escalation_delay_in_minutes": 10,
              "targets": [
                {
                  "type": "schedule",
                  "id": "P9UM4K6" # Command Center N1 Schedule
                }
              ]
            },
            {
              "escalation_delay_in_minutes": 10,
              "targets": [
                {
                  "type": "schedule",
                  "id": "P9T9YUI" # Command Center N2 Schedule
                }
              ]
            },
            {
              "escalation_delay_in_minutes": 10,
              "targets": [
                {
                  "type": "schedule",
                  "id": "PD6FPJX" # Command Center N3 Schedule
                }
              ]
            }
          ],
          "num_loops":9,
          "teams": [
            {
              "id": team_id,
              "type": "team_reference"
            }
          ],          
        }
      )
      sys.stderr.write("%s: OK\n" % hostgroup["name"])
      
    except Exception, e:
      sys.stderr.write("%s: Caught exception (%s)\n" % (hostgroup["name"],e))
      pass

    ## Create Service and associate with Escalation Policy at Pagerduty
    try:
      service = pypd.Service.create(
        data={
          "name": '%s' % hostgroup_name_replaced,
          "description": hostgroup["name"],
          "acknowledgement_timeout": 1800,
          "status": "active",
          "escalation_policy": {
            "id": ep.id,
            "type": "escalation_policy_reference"
          },
          "incident_urgency_rule": {
            "type": 'constant',
            "urgency": "severity_based"
          },
          "alert_creation": "create_alerts_and_incidents",
          "alert_grouping": "time",
          "alert_grouping_timeout": 2         
        }
      )
      
    except Exception, e:
      sys.stderr.write("Caught exception (%s)\n" % e)
      pass

    ## Insert integration for the Service
    try:
      integration = pypd.Integration.create(
        service = service,
        data = {
          "type": "generic_events_api_inbound_integration",         
          "vendor": {
            "id": "PJOGQ4Q", # Zabbix vendor
            "type": "vendor_reference"
          }
        }
      )    
    except Exception, e:
      sys.stderr.write("Caught exception (%s)\n" % e)
      pass
    
    ## Create media type
    try:
      mediatype = zapi.mediatype.create(
        description = "Pagerduty - %s" % hostgroup["name"],
        type = 1,
        exec_path = "pd-zabbix",
        exec_params = "{ALERT.SENDTO}\n{ALERT.SUBJECT}\n{ALERT.MESSAGE}\n"
      )
    except Exception, e:
      sys.stderr.write("Caught exception (%s)\n" % e)
      pass
    
    ## Add media to user
    try:
      zapi.user.addmedia(
        users = [
          {
            "userid":"7" # svcservice
          }
        ],
        medias = [
          {
            "mediatypeid": mediatype['mediatypeids'][0],
            "sendto": integration['integration_key'],
            "active": 0,
            "severity": 60,
            "period": "1-7,00:00-24:00"        
          }
        ]       
      )
    except Exception, e:
      sys.stderr.write("Caught exception (%s)\n" % e)
      pass
    
    ## Add action
    try:
      message = ("name:{TRIGGER.NAME}\n"
                        "trigger_name_orig:{TRIGGER.NAME.ORIG}\n"
                        "id:{TRIGGER.ID}\n"
                        "status:{TRIGGER.STATUS}\n"
                        "hostname:{HOST.NAME}\n"
                        "ip:{HOST.IP}\n"
                        "value:{TRIGGER.VALUE}\n"
                        "event_id:{EVENT.ID}\n"
                        "severity:{TRIGGER.SEVERITY}\n"
                        "groups:{TRIGGER.HOSTGROUP.NAME}\n")

      zapi.action.create(
        name = "Pagerduty - %s" % hostgroup["name"],
        status = 0,
        eventsource = 0,
        esc_period = 3600,
        def_shortdata = "trigger",
        def_longdata = message,
        r_shortdata = "resolve",
        r_longdata = message,
        
        filter = {
          "evaltype": "0", # and/or
          "conditions": [
            {
             "conditiontype": "16", # maintenance status
              "operator": "7", # not in
              "value": ""
            },
            {
              "conditiontype": "0", # host group
              "operator": "0", # =
              "value": hostgroup["groupid"]
            }
          ]
        },
        operations = [
          {
            "mediatypeid": 0,
            "operationtype": "0", # send message
            "opmessage": {
                "mediatypeid": mediatype['mediatypeids'][0],
                "default_msg": "1"
              },
            "opmessage_usr": [
              {
                "userid": "7"
              }
            ]
          }
        ],
        recovery_operations = [
          {
            "operationtype": "0",
            "opmessage": {
              "mediatypeid": mediatype['mediatypeids'][0],
              "default_msg": 1
            },
            "opmessage_usr": [
              {
                "userid": "7"
              }
            ]
          }
        ]
      )
    except Exception, e:
      sys.stderr.write("Caught exception (%s)\n" % e)
      pass