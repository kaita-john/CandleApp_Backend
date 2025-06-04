from decimal import Decimal

MIXED = 'MIXED'
GIRL = 'GIRL'
BOY = 'BOY'

BOARDING = 'BOARDING'
DAY = 'DAY'

MY_GENDER_CHOICES = [
    (MIXED, 'MIXED'),
    (GIRL, 'GIRL'),
    (BOY, 'BOY'),
]

MY_BOARDING_CHOICES = [
    (MIXED, 'MIXED'),
    (BOARDING, 'BOARDING'),
    (DAY, 'DAY'),
]

MANUAL = 'MANUAL'
AUTO = 'AUTO'

PRIORITY = 'PRIORITY'
RATIO = 'RATIO'

CONFIGURATION_CHOICES = [
    (MANUAL, 'MANUAL'),
    (AUTO, 'AUTO'),
]

AUTO_CONFIGURATION_CHOICES = [
    (PRIORITY, 'PRIORITY'),
    (RATIO, 'RATIO'),
]

TEACHING = 'TEACHING'
NON_TEACHING = 'NON_TEACHING'

TEACHINGCHOICES = [
    (TEACHING, 'TEACHING'),
    (NON_TEACHING, 'NON_TEACHING'),
]

STATUS = [
    ("PENDING", "PENDING"),
    ("COMPLETE", "COMPLETE"),
    ("CANCELLED", "CANCELLED"),
    ("FAILED", "FAILED"),
]

# Gender field with choices
group_names = ['CLIENT', 'CELEB']
GENDER_CHOICES = [
    ('MALE', 'Male'),
    ('FEMALE', 'Female')
]



SCHEDULED = 'SCHEDULED'
RESCHEDULED = 'RESCHEDULED'


PENDING = 'PENDING'
CANCELED = 'CANCELED'
COMPLETED = 'COMPLETED'
WITHDRAWREQUEST = 'WITHDRAWREQUEST'
WITHDRAWN = 'WITHDRAWN'


STATE_CHOICES = [
    (PENDING, 'Pending'),
    (CANCELED, 'Canceled'),
    (COMPLETED, 'Completed'),
    (WITHDRAWREQUEST, 'Withdrawrequest'),
    (WITHDRAWN, 'Withdrawn'),
    (RESCHEDULED, 'Rescheduled'),
    (SCHEDULED, 'Scheduled'),
]

sender_email = "kaitaformal@gmail.com"
sender_password ="wwmx vsyr tvwp sfac"

token = "ISSecretKey_live_d7fbfdc8-31f1-40da-9caa-c4bbddc72ab2"
publishable_key = "ISPubKey_live_48453945-adcc-4394-9cbf-98d5d50ad08d"


ONESIGNAL_APP_ID = "abc287a4-1960-4903-8b8f-14812ec6f074"
ONESIGNAL_API_KEY = "os_v2_app_vpbipjazmbeqhc4pcsas5rxqortm4wnjkapeom5wgq5bf543zbs72wihfrqjwmtu3dupjfbof64yezqdktl4cjsm4jllp2gas32cfly"
COMPANY_EMAIL = "ciomaingicandles@gmail.com"
COMPANYID = "67f19eda-9564-4b82-94a0-cc6d3080005c"

COMPANYAMOUNT = Decimal(0.30)