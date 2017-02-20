# coding: utf8
from .models import AdReviewRegisteredUser, AdReviewUser, CounterReviewRegisteredUser, CounterReviewUser


def set_visit_user(ad_id, user_id):
    """ запишем просмотр зарегистрированного пользователя
    """
    # пользователь просмотрел объявление
    # TODO: закешировать get_or_set + Memcached (либо другие библиотеки)
    if AdReviewRegisteredUser.objects.filter(ad=ad_id, user=user_id).exists():
        return

    # сохраним просмотр пользователя
    AdReviewRegisteredUser.ad_review_save(ad_id, user_id)

    # обновим счетчик
    CounterReviewRegisteredUser.counter_add(ad_id)


def set_visit_ip(ad_id, ip, user_id=None):
    """ запишем просмотр НЕ зарегистрированного пользователя
    """
    # пользователь просмотрел объявление

    """ TODO внес коррективу в ip, добавил user_id иначе возможно ситуация,
    что просмотров зарегистрированных пользователей будет больше чем по ip
    """
    ip = ip + ('_' + str(user_id) if user_id else '')

    # TODO: закешировать get_or_set + Memcached (либо другие библиотеки)
    if AdReviewUser.objects.filter(ad=ad_id, ip=ip).exists():
        return

    # сохраним просмотр пользователя
    AdReviewUser.ad_review_save(ad_id, ip)

    # обновим счетчик
    CounterReviewUser.counter_add(ad_id)


def visits_counter(ad_id, ip, user_id=None):
    """
    счетчик просмотров
    :param ad_id: id обявления
    :param ip: ip пользователя
    :param user_id: id пользователя
    :return: None
    """
    if user_id:
        set_visit_user(ad_id, user_id)

    set_visit_ip(ad_id, ip, user_id)

