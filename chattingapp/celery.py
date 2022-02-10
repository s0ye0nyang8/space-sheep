# from __future__ import absolute_import, unicode_literals

# import os

# import boto3
# from celery import Celery
# from django.conf import settings
# from celery import shared_task
# #'셀러리' 프로그램을 위해 기본 장고 설정파일을 설정합니다.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chattingapp.settings')

# app = Celery('chattingapp')
# app.config_from_object('django.conf:settings', namespace='CELERY')

# #등록된 장고 앱 설정에서 task를 불러옵니다.
# app.autodiscover_tasks()

# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))


# @app.task
# def writetoDB(dynamodb,items):
#     table = dynamodb.Table('chat-message')
#     try:
#         # item ={'owner': 'None', 'user': 'None', 'text': 'g', 'media': None, 'timestamp': '1644314464240'}
#         response = table.put_item(
#             # TableName='user',
#             Item= items[0]
#         )
#         # with table.batch_writer() as batch:
#         #     # for item in reversed(items):
#         #     print(item)
#         #     batch.put_item(Item=item)
#     except ClientError as e:
#         print(e)
