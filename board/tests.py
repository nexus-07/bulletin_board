# coding: utf8
from django.test import TestCase
from .models import Ad, CounterReviewRegisteredUser, CounterReviewUser, AdReviewRegisteredUser, AdReviewUser
from.services import visits_counter


class AdSave(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ad_post_save = None

    def test_post_save(self):
        # проверка вызова БЛ
        ad = Ad(header='заголовок1', description='опиание1')

        # вставка нового значения
        self.assertEqual(ad.save(), None)

        # при создании объявления счетчик = 0 на данное объявление
        self.assertEqual(CounterReviewRegisteredUser.objects.get(pk=ad.pk).counter, 0)  # для зарегистрированных
        self.assertEqual(CounterReviewUser.objects.get(pk=ad.pk).counter, 0)  # для НЕ зарегистрированных

        # обновление не должно вызывать ошибок
        ad.description = 'описание поправлено'
        self.assertEqual(ad.save(), None)
        self.assertEqual(CounterReviewRegisteredUser.objects.get(pk=ad.pk).counter, 0)  # для зарегистрированных
        self.assertEqual(CounterReviewUser.objects.get(pk=ad.pk).counter, 0)  # для НЕ зарегистрированных

        self.ad_post_save = ad


class AdCounter(TestCase):
    def test_visits_counter(self):
        # создадим объявление
        ad_save = AdSave()
        ad_save.test_post_save()
        ad = ad_save.ad_post_save

        user_id = 1
        ip = '127.0.0.1'

        # сохраним просмотр объявления НЕ зарегистрированного
        self.assertEqual(visits_counter(ad.pk, ip), None)

        # просмотр по IP
        self.assertEqual(AdReviewUser.objects.filter(ad=ad.pk, ip=ip).exists(), True)
        # счетчик по ip НЕ зарегистрирован
        self.assertEqual(CounterReviewUser.objects.get(pk=ad.pk).counter, 1)
        # счетчик по ip зарегистрирован
        self.assertEqual(CounterReviewRegisteredUser.objects.get(pk=ad.pk).counter, 0)

        # сохраним просмотр объявления зарегистрированного, того же пользователя
        self.assertEqual(visits_counter(ad.pk, ip, user_id), None)

        ip = ip + ('_' + str(user_id) if user_id else '')
        # просмотр по IP
        self.assertEqual(AdReviewUser.objects.filter(ad=ad.pk, ip=ip).exists(), True)
        # счетчик по ip НЕ зарегистрирован
        self.assertEqual(CounterReviewUser.objects.get(pk=ad.pk).counter, 2)
        # счетчик по ip зарегистрирован
        self.assertEqual(CounterReviewRegisteredUser.objects.get(pk=ad.pk).counter, 1)

