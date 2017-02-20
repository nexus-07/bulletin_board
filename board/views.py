# coding: utf8
from django.shortcuts import render, get_object_or_404

from .models import Ad, CounterReviewRegisteredUser, CounterReviewUser
from .services import visits_counter
from bulletin_board.utils import get_client_ip


def index(request):
    ad_list = Ad.objects.order_by('-id')[:10]
    context = {'ad_list': ad_list}
    return render(request, 'board/index.html', context)


# TODO можно закешировать вьюшку, но вынести visits_counter на клиент и вызывать через ajax что покруче
def ad_detail(request, ad_id):
    ad = get_object_or_404(Ad, pk=ad_id)

    # накрутить счетчик (лучше вынести на клиент)
    visits_counter(ad_id, get_client_ip(request), request.user.id)

    # получим счетчики
    # TODO: лучше чисты sql через union
    counter_register = CounterReviewRegisteredUser.objects.get(pk=ad_id).counter
    counter_all = CounterReviewUser.objects.get(pk=ad_id).counter

    return render(request, 'board/detail.html', {
        'ad': ad,
        'counter_register': counter_register,
        'counter_all': counter_all,
    })
