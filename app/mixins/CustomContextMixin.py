# coding=utf-8
from datetime import datetime

from django.views.generic.base import ContextMixin
from django.contrib import messages
from django.views.generic import ListView
from app.models import *
from django.shortcuts import redirect
from django.contrib.auth import logout


#

class RedirectMotoristaOcupadoView(ListView):
    def get(self, request, *args, **kwargs):
        motorista = None
        try:
            motorista = Motorista.objects.get(user=self.request.user)
        except:
            pass
        if motorista:
            if motorista.ocupado:
                return redirect('route_pedido_view', **{'pk': motorista.user.pedido_set.last().pk})
        return super(RedirectMotoristaOcupadoView, self).get(request, *args, **kwargs)


class CustomContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        try:
            motorista = Motorista.objects.get(user=self.request.user)
            if not motorista.is_approved:
                motorista.is_online = False
                motorista.save()
                logout(self.request)
        except:
            pass
        if 'notifications_n' not in kwargs:
            kwargs['notifications_n'] = Notification.objects.filter(to=self.request.user, is_read=False).order_by(
                '-created_at')

        try:
            if 'messages_e' not in kwargs:
                kwargs['messages_e'] = Message.objects.filter(u_to=self.request.user, is_read=False)
            if 'pedidos_n' not in kwargs:
                kwargs['pedidos_n'] = Pedido.objects.filter(estabelecimento=self.request.user.estabelecimento,
                                                            status=False, is_complete=False).order_by(
                    '-created_at')
                kwargs['motoristas_online'] = Motorista.objects.filter(is_online=True, ocupado=False)
                kwargs['pedidos_andamento'] = Pedido.objects.filter(estabelecimento=self.request.user.estabelecimento,
                                                                    status=False, is_complete=False,
                                                                    coletado=True).order_by(
                    '-created_at')
                kwargs['pedidos_pendentes'] = Pedido.objects.filter(estabelecimento=self.request.user.estabelecimento,
                                                                    status=True, is_complete=False,
                                                                    coletado=False).order_by(
                    '-created_at')

        except:
            if 'messages_m' not in kwargs:
                kwargs['messages_m'] = Message.objects.filter(u_to=self.request.user, is_read=False)
                print(kwargs['messages_m'])
            if 'pedidos_n' not in kwargs:
                kwargs['pedidos_n'] = Pedido.objects.filter(motorista=self.request.user, status=False,
                                                            is_complete=False).order_by(
                    '-created_at')
            if 'corridas_mes' not in kwargs:
                now = datetime.now()
                corridas_mes = User.objects.get(id=self.request.user.id).pedido_set.filter(created_at__month=now.month)
                corridas_hoje = User.objects.get(id=self.request.user.id).pedido_set.filter(created_at__day=now.day)
                kwargs['corridas_mes'] = corridas_mes
                kwargs['corridas_hoje'] = corridas_hoje
                ganho_mes = 0.0
                ganho_hoje = 0.0
                for pedido in corridas_mes:
                    ganho_mes = float(ganho_mes) + float(pedido.valor_total)
                for ped in corridas_hoje:
                    ganho_hoje = float(ganho_hoje) + float(ped.valor_total)

                kwargs['ganho_mes'] = ganho_mes
                kwargs['ganho_hoje'] = ganho_hoje

        return super(CustomContextMixin, self).get_context_data(**kwargs)


class ListMotoristasMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        motoristas = Motorista.objects.all()
        kwargs['motoristas'] = motoristas
        kwargs['motoristas_online'] = Motorista.objects.filter(is_online=True)
        kwargs['motoristas_livres'] = Motorista.objects.filter(is_online=True, ocupado=False)
        kwargs['motoristas_ocupados'] = Motorista.objects.filter(is_online=True, ocupado=True)
        return super(ListMotoristasMixin, self).get_context_data(**kwargs)


class DashboardMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        now = datetime.now()
        motoristas = Motorista.objects.all()
        pedidos = Pedido.objects.all()
        users = User.objects.all()
        notificacoes = Notification.objects.all()
        locations = Location.objects.all()
        bairros = Bairro.objects.all()
        # estabelecimentos = Estabelecimento.objects.all()
        pontos = Ponto.objects.all()
        kwargs['motoristas'] = motoristas
        kwargs['pedidos'] = pedidos
        kwargs['users'] = users
        # kwargs['estabelecimentos'] = estabelecimentos
        kwargs['bd_space'] = float(float(float(
            len(motoristas) + len(pedidos) + len(users) + len(notificacoes) + len(locations) + len(bairros) + len(pontos)) / 10000) * 100)
        kwargs['num_pedidos_entregues'] = Pedido.objects.filter(created_at__month=datetime.now().month,
                                                                is_complete=True)
        kwargs['pedidos_do_mes'] = Pedido.objects.filter(created_at__month=datetime.now().month).order_by('-created_at')
        kwargs['pedidos_entregues'] = Pedido.objects.filter(is_complete=True,
                                                            created_at__month=datetime.now().month).order_by(
            '-created_at')
        kwargs['pedidos_pendentes'] = Pedido.objects.filter(status=True)
        kwargs['pedidos_andamento'] = Pedido.objects.filter(status=False, is_complete=False)
        kwargs['motoristas_online'] = Motorista.objects.filter(is_online=True)
        kwargs['motoristas_livres'] = Motorista.objects.filter(is_online=True, ocupado=False)
        kwargs['motoristas_ocupados'] = Motorista.objects.filter(is_online=True, ocupado=True)
        # kwargs['lojas'] = Estabelecimento.objects.all().order_by('-created_at')
        kwargs['pontos_mes'] = Ponto.objects.filter(created_at__month=now.month).order_by('bairro')
        kwargs['pontos_all'] = Ponto.objects.all().order_by('bairro')
        kwargs['address_all'] = Ponto.objects.all().order_by('endereco')
        return super(DashboardMixin, self).get_context_data(**kwargs)
