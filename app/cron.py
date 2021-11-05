from .models import Bid, Invoice, User, Test
# import datetime as DT
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .views import  expired_bid_check
# from pysendpulse.pysendpulse import PySendPulse
# from decouple import config

# REST_API_ID = config("REST_API_ID")
# REST_API_SECRET = config("REST_API_SECRET")
# TOKEN_STORAGE = config("TOKEN_STORAGE")
# MEMCACHED_HOST = config("MEMCACHED_HOST")
# SPApiProxy = PySendPulse(REST_API_ID, REST_API_SECRET, TOKEN_STORAGE, memcached_host=MEMCACHED_HOST)
# sender_email = "donotreply@wastecoin.co"

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(expired_bid_check, 'interval', seconds=10)
    scheduler.start()

# def test_scehdule():
#     Test.objects.create(name='Daniel')

# def expired_bid_check():

#     print("hi cronjob")
#     bidClosingDate = bidSelected.invoice.updated_at + DT.timedelta(days=3)
#     bids = Bid.objects.filter(bidClosed=False)
#     today = DT.date.today()
#     for bid in bids:
#         bidClosingDate = bid.invoice.updated_at + DT.timedelta(days=1)
#         print(bidClosingDate)
#         print(today)
#         if bidClosingDate > today:
#             bid.bidClosed = True
#             bid.save()
#             email = "todak2000@gmail.com"
#             mail_subject ='Invoice-'+ str(bid.invoice.id)+'  bids just closed'
#             email2 = {
#                 'subject': mail_subject,
#                 'html': '<section style="background-color: #EEF1F8;height:auto;width: auto;display: flex;flex-direction: column;align-items: center;justify-content: center;"> <div style="background: #FFFFFF;width: 100%;padding: 10vh;"><img src="https://i.im.ge/2021/09/23/TCyJRy.jpg" style="margin:auto; width:40%; height: auto;" /><h3 style="margin-top:-6vh;">Hello Admin!</h3><p style="font-size: 1.15rem;color:#767E9F;">'+str(bid.invoice.id)+' bids just closed. Thanks.</p></div></section>',
#                 'text': 'Hello, Admin!\n Invoice'+str(bid.invoice.id)+' bids just closed. Thanks.',
#                 'from': {'name': 'Quidroo', 'email': sender_email},
#                 'to': [
#                     {'name': 'Quidroo Admin', 'email': email}
#                 ]
#             }
#             sentMail2 = SPApiProxy.smtp_send_mail(email2)