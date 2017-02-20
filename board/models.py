# coding: utf8
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class Ad(models.Model):
    """
    Объявления
    """
    id = models.AutoField(primary_key=True)  # bigserial для postgresql
    header = models.CharField(max_length=1024)
    description = models.CharField(max_length=10000)


class CounterReview(models.Model):
    """
    Счетчик просмотров (сумма всех просмотров)
    """
    class Meta:
        abstract = True

    ad = models.OneToOneField(Ad, primary_key=True)
    counter = models.BigIntegerField(default=0)

    @classmethod
    def counter_add(cls, ad_id):
        """
        увеличение счетчика
        """
        cls.objects.filter(pk=ad_id).update(counter=F('counter') + 1)  # насколько я знаю так должно работать быстрее


class CounterReviewRegisteredUser(CounterReview):
    """
    Счетчик просмотров зарегистрированных пользователей(сумма всех просмотров)
    """


class CounterReviewUser(CounterReview):
    """
    Счетчик просмотров НЕ зарегистрированных пользователей(сумма всех просмотров)
    Счетчик работает при сравнении ip
    """


class AdReview(models.Model):
    """
    Просмотр объявления
    """
    class Meta:
        unique_together = NotImplemented
        abstract = True

    id = models.AutoField(primary_key=True)  # bigserial для postgresql
    ad = models.ForeignKey(Ad, db_index=False)

    @classmethod
    def ad_review_save(cls, ad_id, val):
        """
        сохраним информацию о том что данный пользователь или ip уже посмотрели объявление
        """
        raise NotImplemented


class AdReviewRegisteredUser(AdReview):
    """
    Просмотр объявления (сам факт, разового просмотра) зарегистрированным пользоватеем
    """
    class Meta(AdReview.Meta):
        unique_together = (("ad", "user"),)

    user = models.ForeignKey(User, db_index=False)

    @classmethod
    def ad_review_save(cls, ad_id, val):
        cls.objects.create(ad=Ad(ad_id), user=User(val))


class AdReviewUser(AdReview):
    """
    Просмотр объявления (сам факт, разового просмотра) по ip пользователя
    """
    class Meta(AdReview.Meta):
        unique_together = (("ad", "ip"),)

    ip = models.CharField(max_length=255)  # IPAddressField - для postgresql

    @classmethod
    def ad_review_save(cls, ad_id, val):
        cls.objects.create(ad=Ad(ad_id), ip=val)


@receiver(post_save, sender=Ad)
def ad_post_save(sender, instance, created, **kwargs):
    # при создании объявления зарезервировать место для просмотров для зарегистрированого пользователя и всех остальных
    if not created:
        return

    # добавить запись зарегистрированного пользователя (общий счетчик)
    CounterReviewRegisteredUser(pk=instance.pk).save()

    # добавить запись НЕ зарегистрированного пользователя (общий счетчик)
    CounterReviewUser(pk=instance.pk).save()

# делаем описание
# сохраняем
# добавляем счетчики со значением 0 в pre_save
#
# просматриваем объявление пользователем
# проверяем видел ли это объявление пользователь, закешировать на сутки (возможно кеш станет толстым)
#     если видел то ничего не делаем
#     если нет,
#         то увеличиваем счетчик
#         ставим отметку что он видел (кэш будет пустой это не критично)
#
# по ip
# проверяем видел ли это ip, закешировать на сутки (возможно кеш станет толстым)
#     если видел то ничего не делаем
#     если нет,
#         то увеличиваем счетчик ip
#         ставим отметку что он видел (кэш будет пустой это не критично)

# подключение кэша http://djbook.ru/rel1.9/topics/cache.html
#
# без мемкэш и редиса
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'unique-snowflake',
#     }
# }

# все таблицы кроме Ad лучше поместить в редис, по скти будет работать как кэш
# (главно чтоб данные из редиса на диск скидывались)

# добавить админку, вывести туда Ad (admin a12345678)
# проверить что работает редактирование
#
# добавить модуль авторизации
# создать пользователя
#
# создать вьюшку для вывода объявления
# получить user.id and ip
# подключить просмотры, коммент что лучше через ajax