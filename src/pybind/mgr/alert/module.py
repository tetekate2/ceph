
"""
An email alert module to report ceph cluster health status

See doc/mgr/EmailReport.rst for more info.
"""

from mgr_module import MgrModule
from threading import Event
import sys
import  six
import smtplib
import json
import datetime
from email.mime.text import MIMEText
import Slacker
from config import CONFIG

SLEEP_INTERVAL = datetime.timedelta(seconds = 60)

class Alert(MgrModule):
    COMMANDS = [
        {
            "cmd": "email alert "
                   "name=status_code,type=CephString,req=false",
            "desc": "Send an email alert to inform user of their Ceph cluster status",
            "perm": "r"
        },
        {
            "cmd": "slack alert ",
            "desc": "post to slack",
            "perm": "r"
        }
    ]

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)

        # set up some members to enable the serve() method and shutdown
        self.run = True
        self.event = Event()

    def post_to_slack(self, cmd):
        slack = Slacker(CONFIG['slack_api'])
        health = json.loads(self.get('health')['json'])
        msg = json.dumps(health, sort_keys=True, indent=4)

    def alert_via_email(self, cmd):
        health = json.loads(self.get('health')['json'])
        health = json.dumps(health, sort_keys=True, indent=4)
        msg = MIMEText(health)
        msg['Subject'] = 'Ceph: Cluster Health Status Alert'
        msg['From'] = CONFIG['mail_username']
        msg['To'] = CONFIG['test_user']
        server = smtplib.SMTP('{}:{}'.format(CONFIG['mail_server'], CONFIG['mail_port']))
        server.ehlo()
        server.starttls()
        server.login(CONFIG['mail_username'], CONFIG['mail_password'])
        server.sendmail(CONFIG['mail_username'], CONFIG['test_user'],msg.as_string())

    def handle_command(self, inbuf, cmd):
        self.log.error("handle_command")
        if cmd['prefix'] == 'email alert':
            return self.alert_via_email(cmd)
        elif cmd['prefix'] == 'slack alert':
            return self.post_to_slack(cmd)
        else:
            raise NotImplementedError(cmd['prefix'])

    def serve(self):
        """
        This method is called by the mgr when the module starts and can be
        used for any background activity.
        """
        old_health = json.loads(self.get('health')['json'])
        self.log.info("Starting")
        while self.run:
            if time.time() >= time_last_checked:
                time_last_checked = time.time()+60
                new_health = json.loads(self.get('health')['json'])
                for code, item in new_health['checks'].iteritems():
                    if code not in old_health['checks']:
                        # it's a new alert
                        new[code] = item
                    else:
                        old_item = old_health['checks'][code]
                        if item['severity'] != old_item['severity'] or item['summary']['message'] != old_item['summary']['message']:
                            # changed
                            updated[code] = item
                for code, item in old_health['checks'].iteritems():
                    if code not in new_health['checks']:
                        # health alert has resolved
            self.log.debug('Sleeping for %d seconds', SLEEP_INTERVAL)
            self.event.wait(SLEEP_INTERVAL)
            self.event.clear()

    def shutdown(self):
        """
        This method is called by the mgr when the module needs to shut
        down (i.e., when the serve() function needs to exit.
        """
        self.log.info('Stopping')
        self.run = False
        self.event.set()
