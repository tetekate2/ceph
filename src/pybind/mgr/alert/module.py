
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
import tweepy
from config import CONFIG

SLEEP_INTERVAL = datetime.timedelta(seconds = 60)

class Alert(MgrModule):
    OPTIONS = [
    ''' define the servers address and some authentication credentials'''
            {
                'name': 'mail_server',
                'default': 'smtp.gmail.com'
            },
            {
                'name': 'mail_port',
                'default': 587
            },
            {
                'name': 'email_receiver',
                'default': None
            },
            {
                'name': 'email_sender',
                'default': None
            },
            {
                'name': 'sender_password',
                'default': None
            },
            {
                'name': 'slack_api',
                'default': None
            },
            {
                'name': 'twitter_consumer_key'
                'default': None
            },
            {
                'name': 'twitter_consumer_secret'
                'default': None
            },
            {
                'name': 'twitter_access_token'
                'default': None
            },
            {
                'name': 'twitter_access_token_secret'
                'default': None
            }
    ]

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

    def init_module_config(self):
        self.config['mail_server'] = \
            self.get_config("mail_server", default=self.config_keys['mail_server'])
        self.config['mail_port'] = \
            int(self.get_config("mail_port", default=self.config_keys['mail_port']))
        self.config['email_receiver'] = \
            self.get_config("email_receiver", default=self.config_keys['email_receiver'])
        self.config['email_sender'] = \
            self.get_config("email_sender", default=self.config_keys['email_sender'])
        self.config['sender_password'] = \
            self.get_config("sender_password", default=self.config_keys['sender_password'])
        self.config['slack_api'] = \
            int(self.get_config("slack_api", default=self.config_keys['slack_api']))
        self.config['twitter_consumer_key'] = \
            int(self.get_config("twitter_consumer_key", default=self.config_keys['twitter_consumer_key']))
        self.config['twitter_consumer_secret'] = \
            int(self.get_config("twitter_consumer_key", default=self.config_keys['twitter_consumer_key']))
        self.config['twitter_access_token'] = \
            int(self.get_config("twitter_access_token", default=self.config_keys['twitter_access_token']))
        self.config['twitter_access_token_secret'] = \
            int(self.get_config("twitter_access_token_secret", default=self.config_keys['twitter_access_token_secret']))

    def get_api():
        auth = tweepy.OAuthHandler(self.config['twitter_consumer_key'], self.config['twitter_consumer_secret'])
        auth.set_access_token(slef.config['twitter_access_token'], self.config['twitter_access_token_secret'])
        return tweepy.API(auth)

    def tweets(alert_message):
        api = get_api()
        tweet = alert_message
        status = api.update_status(status=tweet)
        return status

    def slack(alert_message):
        slack = Slacker(self.config['slack_api'])
        post = alert_message
        return post

    def email(alert_message):
        msg = MIMEText(alert_message)
        msg['Subject'] = 'Ceph: Cluster Health Status Alert'
        msg['From'] = self.config['email_sender']
        msg['To'] = self.config['email_receiver']
        server = smtplib.SMTP('{}:{}'.format(self.config['mail_server'], self.config['mail_port']))
        server.ehlo()
        server.starttls()
        server.login(self.config['email_sender'], self.config['sender_password'])
        sendmail = server.sendmail(self.config['email_sender'], self.config['email_receiver'],msg.as_string())
        return sendmail

    def new_alert(self, cmd):
        self.refresh_config()
        if option in ['slack_api']:    

    def handle_command(self, inbuf, cmd):
        self.log.error("handle_command")
        if cmd['prefix'] == 'email alert':
            return self.alert_via_email(cmd)
        elif cmd['prefix'] == 'slack alert':
            return self.post_to_slack(cmd)
        else:
            raise NotImplementedError(cmd['prefix'])

    def refresh_config(self):
        for opt in self.OPTIONS:
            setattr(self,
                    opt['name'],
                    self.get_config(opt['name']) or opt['default'])
            self.log.debug(' %s = %s', opt['name'], getattr(self, opt['name']))

    def serve(self):
        """
        This method is called by the mgr when the module starts and can be
        used for any background activity.
        """
        self.log.info("Starting")
        old_health = None
        old_health = json.loads(self.get('health')['json'])

        while self.run:
            self.refresh_config()
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
