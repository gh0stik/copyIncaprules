import requests
import json
from sys import exit as err_exit
import time
import re

# Usage:
# The function will expect 4 parameters - api_id, api_key, from_id and to_id.
# api_id - api_id of the user.
# api_key - api_key of the user.
# from_id - external site id of the source site.
# to_id - external site id of the destination site.
# API details at https://docs.imperva.com/bundle/cloud-application-security/page/api/sites-api.htm

def copyIncaprules(api_id, api_key, from_id, to_id):

    def copyTo(to_id, rule_params, task):
        if not rule_params["name"].isalnum():
            rule_params["name"] = re.sub("\W+", "", rule_params["name"])
        copy_params = {
            "api_id": api_id,
            "api_key": api_key,
            "site_id": to_id,
            "name": rule_params["name"],
            "action": rule_params["action"],
            "filter": rule_params["filter"]
        }
        if task == "rate_rules":
            copy_params.update({"rate_context": rule_params["context"], "rate_interval": rule_params["interval"]})
        print(copy_params)
        res = requests.post("https://my.imperva.com/api/prov/v1/sites/incapRules/add", params=copy_params)
        try:
            if json.loads(res.text)["status"] == "ok":
                print("Rule: {} has been successfully copied from site id {} to site id {}".format(rule_params["name"], from_id, to_id))
        except:
            print("Error: {}".format(res.text))
        time.sleep(3)
        if rule_params["enabled"] == "false":
            disable_params = {"api_id": api_id,
                             "api_key": api_key,
                             "rule_id": json.loads(res.text)["rule_id"],
                             "enable": "false"}
            requests.post("https://my.imperva.com/api/prov/v1/sites/incapRules/enableDisable", params=disable_params)

    params = {
        "api_id": api_id,
        "api_key": api_key,
        "site_id": from_id
    }
    req = requests.post("https://my.imperva.com/api/prov/v1/sites/incapRules/list", params=params)
    if "RULE_ACTION_RATE" in req.text:
        try:
            rule_params = json.loads(req.text)["rate_rules"]["Rates"]
            for rule in rule_params:
                try:
                    copyTo(to_id, rule, "rate_rules")
                except Exception as e:
                    print("Error - {}".format(str(e)))
                    continue
        except Exception as e:
            print("Did not find any Incaprules. Error - {}".format(str(e)))
            pass


    try:
        rule_params = json.loads(req.text)["incap_rules"]["All"]
        for rule in rule_params:
            try:
                copyTo(to_id, rule, "incap_rules")
            except Exception as e:
                print("Error - {}".format(str(e)))
                continue
    except Exception as e:
        err_exit("Did not find any Incaprules. Error - {}".format(str(e)))
