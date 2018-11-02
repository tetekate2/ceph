=============
Alert Plugin
=============

The alert plugin send cluster health notification via email.

--------
Enabling
--------

To enable the module, use the following command:

::

    ceph mgr module enable alert

If you wish to subsequently disable the module, you can use the equivalent
*disable* command:

::

    ceph mgr module disable alert

-------------
Configuration
-------------

For the alert module to send an email, it
is necessary to configure the servers address and some authentication
credentials by editing the config.py file found inside the module directory

Set configuration values in the config `config.py` should look something like:

::

   'mail_server' : 'smtp.gmail.com',
   'mail_port' : 587,
   'test_user' : 'receiver@gmail.com',
   'mail_username' : 'sender@gmail.com',
   'mail_password' : 'sender_password'
