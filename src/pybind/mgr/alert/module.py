
"""
An email alert module to report ceph cluster health status

See doc/mgr/EmailReport.rst for more info.
"""

from mgr_module import MgrModule
from threading import Event
import sys
import smtplib
import json
from email.mime.text import MIMEText
import Slacker
from config import CONFIG

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
        # result = ''
        # health_status = self.get('health')
        # for k, v in health_status.items():
        #     result += '{}: {}\n'.format(k, v)
        # print(result)
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

    def serve(self):
        """
        This method is called by the mgr when the module starts and can be
        used for any background activity.
        """
        self.log.info("Starting")
        while self.run:
            sleep_interval = 5
            self.log.debug('Sleeping for %d seconds', sleep_interval)
            ret = self.event.wait(sleep_interval)
            self.event.clear()

    def handle_command(self, inbuf, cmd):
        self.log.error("handle_command")
        if cmd['prefix'] == 'email alert':
            return self.alert_via_email(cmd)
        elif cmd['prefix'] == 'slack alert':
            return self.post_to_slack(cmd)
        else:
            raise NotImplementedError(cmd['prefix'])

    def shutdown(self):
        """
        This method is called by the mgr when the module needs to shut
        down (i.e., when the serve() function needs to exit.
        """
        self.log.info('Stopping')
        self.run = False
        self.event.set()
