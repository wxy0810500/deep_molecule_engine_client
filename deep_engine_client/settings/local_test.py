"""
Django settings for deep_engine_client project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

from .base import BASE_DIR
import os



# 其它 存放静态文件的文件夹，可以用来存放项目中公用的静态文件，里面不能包含 STATIC_ROOT
# 如果不想用 STATICFILES_DIRS 可以不用，都放在 app 里的 common_static 中也可以

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "common_static"),
    # PROD_STATIC_DIR,
)


DEBUG = True