
"""
An email alert module to report ceph cluster health status

See doc/mgr/EmailReport.rst for more info.
"""

from mgr_module import MgrModule
import smtplib
import json
from email.mime.text import MIMEText
from config import CONFIG


class EmailReport(MgrModule):
    COMMANDS = [
        {
            "cmd": "email alert "
                   "name=status_code,type=CephString,req=false",
            "desc": "Send an email alert to inform user of their Ceph cluster status",
            "perm": "r"
        },
    ]


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

    def handle_command(self, inbuf, cmd):
        self.log.error("handle_command")
        if cmd['prefix'] == 'email alert':
            return self.alert_via_email(cmd)
        else:
            raise NotImplementedError(cmd['prefix'])
