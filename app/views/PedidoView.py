#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template import Context
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from app.forms import PontoFormSet, PontoFormUpdateSet
from app.mixins.CustomContextMixin import RedirectMotoristaOcupadoView, CustomContextMixin
from app.models import Pedido, Estabelecimento, Motorista, Notification, Ponto, Classification
from app.views.fcm import func
from app.views.snippet_template import render_block_to_string


class OrderMotoristaDetailView(LoginRequiredMixin, DetailView, CustomContextMixin):
    model = Pedido
    template_name = 'pedidos/../../templates/acompanhar/order_view.html'
    context_object_name = 'pedido'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            return super(OrderMotoristaDetailView, self).get(request, *args, **kwargs)
        except:
            messages.error(request, 'Este pedido foi cancelado pela loja')
            return HttpResponseRedirect('/app/pedidos/motorista/')


class RouteMotoristaDetailView(LoginRequiredMixin, DetailView, CustomContextMixin):
    model = Pedido
    template_name = 'pedidos/../../templates/acompanhar/route_view.html'
    context_object_name = 'pedido'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            return super(RouteMotoristaDetailView, self).get(request, *args, **kwargs)
        except:
            messages.error(request, 'Este pedido foi cancelado pela loja')
            return HttpResponseRedirect('/app/pedidos/motorista/')


class MapRouteMotoristaView(LoginRequiredMixin, DetailView, CustomContextMixin):
    model = Pedido
    template_name = 'pedidos/../../templates/acompanhar/map_view.html'
    context_object_name = 'pedido'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            return super(MapRouteMotoristaView, self).get(request, *args, **kwargs)
        except:
            messages.error(request, 'Este pedido foi cancelado pela loja')
            return HttpResponseRedirect('/app/pedidos/motorista/')


class PedidosLojaListView(LoginRequiredMixin, ListView, CustomContextMixin):
    login_url = '/login/'
    model = Pedido
    # permission_required = ('app.view_dashboard_1', 'app.view_dashboard_2', 'app.view_dashboard_3', )
    context_object_name = 'pedidos'
    template_name = 'pedidos/list_pedidos_loja.html'

    def get_queryset(self):
        return Pedido.objects.filter(estabelecimento__user=self.request.user).order_by('-created_at')


class PedidosMotoristaListView(LoginRequiredMixin, RedirectMotoristaOcupadoView, ListView, CustomContextMixin):
    login_url = '/login/'
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedidos/list_pedidos_motorista.html'

    def get_queryset(self):
        return Pedido.objects.filter(is_complete=False, coletado=False, status=True, is_draft=False).order_by(
            '-created_at')


class PedidosMotoristaPremiumListView(LoginRequiredMixin, RedirectMotoristaOcupadoView, ListView, CustomContextMixin):
    login_url = '/login/'
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedidos/list_pedidos_premium.html'

    def get_queryset(self):
        return Pedido.objects.filter(is_complete=False, coletado=False, status=True).order_by(
            '-created_at')


class EntregasMotoristaListView(LoginRequiredMixin, ListView, CustomContextMixin):
    login_url = '/login/'
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedidos/list_entregas_motorista.html'

    def get_queryset(self):
        return Pedido.objects.filter(motorista=self.request.user).order_by('-published_at')


@require_http_methods(["GET"])
def buscar_cliente(request):
    q = request.GET['q']
    results = []
    try:
        qs = Ponto.objects.filter(telefone__icontains=q).order_by('-created_at')
        for ponto in qs:
            results.append({
                'cliente': ponto.cliente,
                'endereco': ponto.endereco,
                'numero': ponto.numero,
                'bairro': ponto.bairro.nome,
                'complemento': ponto.complemento,
                'observacoes': ponto.observacoes
            })
    except (Exception,):
        pass
    print(results)
    return JsonResponse({'results': results})


class PedidoCreateView(LoginRequiredMixin, CreateView, CustomContextMixin):
    model = Pedido
    success_url = '/app/pedidos/loja/'
    login_url = '/login/'
    fields = ['estabelecimento', 'is_draft']
    template_name = 'pedidos/add_pedido.html'

    # def get_success_url(self):
    # return reverse('view_pedido_view', kwargs={'pk': self.object.pk})

    def get_initial(self):
        return {
            'estabelecimento': Estabelecimento.objects.get(user=self.request.user)
        }

    def get_context_data(self, **kwargs):
        data = super(PedidoCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['pontoset'] = PontoFormSet(self.request.POST)
        else:
            data['pontoset'] = PontoFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        pontoset = context['pontoset']
        with transaction.atomic():
            self.object = form.save()
            if pontoset.is_valid():
                pontoset.instance = self.object
                pontoset.save()
        message = "Um novo pedido foi feito pela " + self.request.user.first_name
        print('>>>>>>>> Novo Pedido criado pela loja ' + self.request.user.first_name)
        pedido = self.object
        if not pedido.is_draft:
            a = func()
            for m in Motorista.objects.all():
                if m.is_online and not m.ocupado:
                    n = Notification(type_message='NOVO_PEDIDO', to=m.user, message=message)
                    n.save()
        return super(PedidoCreateView, self).form_valid(form)


class PedidoDetailView(LoginRequiredMixin, DetailView, CustomContextMixin):
    model = Pedido
    template_name = 'pedidos/../../templates/acompanhar/view_pedido.html'

    def get_context_data(self, **kwargs):
        data = super(PedidoDetailView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['pontoset'] = PontoFormUpdateSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['pontoset'] = PontoFormUpdateSet(instance=self.object)
        return data


class PedidoUpdateView(LoginRequiredMixin, UpdateView, CustomContextMixin):
    model = Pedido
    success_url = '/app/pedidos/loja/'
    fields = ['estabelecimento', 'is_draft']
    template_name = 'pedidos/edit_pedido.html'

    def get_initial(self):
        return {
            'estabelecimento': Estabelecimento.objects.get(user=self.request.user)
        }

    def get_context_data(self, **kwargs):
        data = super(PedidoUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['pontoset'] = PontoFormUpdateSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['pontoset'] = PontoFormUpdateSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        pontoset = context['pontoset']
        with transaction.atomic():
            self.object = form.save()
            print(pontoset.errors)
            if pontoset.is_valid():
                pontoset.instance = self.object
                pontoset.save()
        print('>>>>>>>> Pedido editado pela loja ' + self.request.user.first_name)
        pedido = self.object
        if not pedido.is_draft:
            a = func()
            # message = "Um novo pedido foi feito pela " + self.request.user.first_name
            # for m in Motorista.objects.all():
            #     if m.is_online and not m.ocupado:
            #         n = Notification(type_message='NOVO_PEDIDO', to=m.user, message=message)
            #         n.save()
        return super(PedidoUpdateView, self).form_valid(form)


def delete_pedido(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Usuario precisa estar logado para esta operacao")
        raise PermissionDenied("Usuario precisa estar logado para esta operacao")
    else:
        pedido = Pedido.objects.get(id=pk)
        try:
            user_motorista = pedido.motorista
            motorista = Motorista.objects.get(user=user_motorista)
        except:
            user_motorista = None
        if user_motorista:
            if user_motorista.pedido_set.last() == pedido:
                motorista.ocupado = False
                motorista.save()
                loja = Estabelecimento.objects.get(user=request.user)
                if motorista.is_online:
                    print(
                        '>>>>>>>> Motorista ' + motorista.user.first_name + ' teve seu pedido cancelado pela loja ' + pedido.estabelecimento.user.first_name)
                    message = "O Pedido que voce ia entregar foi cancelado pela loja " + request.user.first_name + ". Desculpe pelo transtorno! Qualquer coisa, ligue para a loja: " + loja.phone
                    n = Notification(type_message='DELETE_LOJA', to=motorista.user, message=message)
                    n.save()
        pedido.delete()
        messages.success(request, "Pedido deletado com sucesso")
        return HttpResponseRedirect('/app/pedidos/loja/')


def cancel_pedido(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Usuario precisa estar logado para esta operacao")
        raise PermissionDenied("Usuario precisa estar logado para esta operacao")
    else:
        pedido = Pedido.objects.get(id=pk)
        try:
            user_motorista = pedido.motorista
            motorista = Motorista.objects.get(user=user_motorista)
        except:
            user_motorista = None
        if user_motorista:
            if user_motorista.pedido_set.last() == pedido:
                motorista.ocupado = False
                motorista.save()
                loja = Estabelecimento.objects.get(user=request.user)
                if motorista.is_online:
                    print(
                        '>>>>>>>> Motorista ' + motorista.user.first_name + ' teve seu pedido cancelado pela loja ' + pedido.estabelecimento.user.first_name)
                    message = "O Pedido que voce ia entregar foi cancelado pela loja " + request.user.first_name + ". Desculpe pelo transtorno! Qualquer coisa, ligue para a loja: " + loja.phone
                    n = Notification(type_message='DELETE_LOJA', to=motorista.user, message=message)
                    n.save()
        pedido.status = True
        pedido.motorista = None
        pedido.save()
        messages.success(request, "Pedido deletado com sucesso")
        return HttpResponseRedirect('/app/pedidos/loja/')


@require_http_methods(["GET"])
def get_pedidos_motorista(request):
    pedidos = Pedido.objects.filter(is_complete=False, coletado=False, status=True, is_draft=False).order_by(
        '-created_at')
    context = Context({'pedidos': pedidos, 'user': request.user})
    return_str = render_block_to_string('includes/table_pedidos_motorista.html', context)
    return HttpResponse(return_str)


@require_http_methods(["GET"])
def get_entregas_motorista(request):
    pedidos = Pedido.objects.filter(motorista=request.user).order_by('-published_at')
    context = Context({'pedidos': pedidos, 'user': request.user})
    return_str = render_block_to_string('includes/table_entregas_motorista.html', context)
    return HttpResponse(return_str)


@require_http_methods(["GET"])
def accept_corrida(request, pk_pedido):
    try:
        pedido = Pedido.objects.get(id=pk_pedido)
        if pedido.motorista:
            try:
                messages.error(request,
                               'O motorista ' + pedido.motorista.first_name + ' pegou esta entrega antes de você')
            except (Exception,):
                messages.error(request, 'Outro Motorista pegou esta entrega antes de você')
            return HttpResponseRedirect('/app/pedidos/motorista/')
        else:
            pedido.status = False
            pedido.motorista = request.user
            pedido.save()
            motorista = Motorista.objects.get(user=request.user)
            motorista.ocupado = True
            motorista.save()
            if pedido.estabelecimento.is_online:
                print(
                    '>>>>>>>> Motorista ' + motorista.user.first_name + ' aceitou fazer a corrida para a loja ' + pedido.estabelecimento.user.first_name)
                message = "Um motorista aceitou fazer a entrega do Pedido ID #" + str(
                    pedido.pk) + ". Qualquer problema, ligue para o motorista: " + motorista.phone
                n = Notification(type_message='ACCEPT_ORDER', to=pedido.estabelecimento.user, message=message)
                n.save()
                message = 'A Loja ' + pedido.estabelecimento.user.first_name + ', localizado na ' + pedido.estabelecimento.full_address + ', esta aguardando a coleta.'
                no = Notification(type_message='DELETE_LOJA', to=pedido.motorista,
                                  message=message)  # está delete loja por enquanto.
                no.save()
            return HttpResponseRedirect('/app/pedido/route/' + str(pedido.pk))
    except:
        messages.error(request, 'Este pedido foi deletado pela Loja')
        return HttpResponseRedirect('/app/pedidos/motorista/')


@require_http_methods(["GET"])
def liberar_corrida(request, pk_pedido):
    pedido = Pedido.objects.get(id=pk_pedido)
    pedido.coletado = True
    pedido.save()
    if Motorista.objects.get(user=pedido.motorista).is_online:
        print(
            '>>>>>>>> Motorista ' + pedido.motorista.first_name + ' foi liberado pela loja ' + pedido.estabelecimento.user.first_name)
        message = "Voce foi liberado pela loja para realizar a(s) entrega(s). Sua Rota atual esta no menu ENTREGAS. Quando terminar uma entrega, marque finalizar. Qualquer problema, ligue para a loja: " + pedido.estabelecimento.phone
        n = Notification(type_message='ENABLE_ROTA', to=pedido.motorista, message=message)
        n.save()
    return redirect('/app/acompanhar')


@require_http_methods(["GET"])
def avaliar_motorista(request, pk_pedido, nota):
    pedido = Pedido.objects.get(id=pk_pedido)
    motorista = Motorista.objects.get(user=pedido.motorista)
    new_class = Classification(user=motorista.user, pedido=pedido, nota=nota)
    new_class.save()
    if motorista.is_online:
        print(
            '>>>>>>>> Motorista ' + motorista.user.first_name + ' foi avaliado pela loja ' + pedido.estabelecimento.user.first_name)
    return redirect('/app/pedidos/loja')


@require_http_methods(["GET"])
def finalizar_entrega(request, pk_ponto, pk_pedido):
    try:
        ponto = Ponto.objects.get(id=pk_ponto)
        pedido = Pedido.objects.get(id=pk_pedido)
        ponto.status = True
        ponto.save()
        pto_entregues = len(pedido.ponto_set.filter(status=True))
        print(len(pedido.ponto_set.all()) == pto_entregues)
        if len(pedido.ponto_set.all()) == pto_entregues:
            pedido.is_complete = True
            pedido.save()
            messages.success(request, 'Tudo entregue! Finalize esta Rota para poder pegar outros.')
        if pedido.estabelecimento.is_online:
            print('>>>>>>>> Motorista ' + request.user.first_name + ' entregou pedido ao cliente ' + ponto.cliente)
            message = "Motorista " + request.user.first_name + " entregou pedido ao cliente " + ponto.cliente + " no endereco " + ponto.full_address
            n = Notification(type_message='ORDER_DELIVERED', to=pedido.estabelecimento.user, message=message)
            n.save()
        return HttpResponseRedirect('/app/pedido/route/' + str(pedido.pk))
    except:
        print('******* error url ')
        messages.error(request, 'Este pedido foi deletado pela Loja')
        return HttpResponseRedirect('/app/pedidos/motorista/')


@require_http_methods(["GET"])
def finalizar_pedido(request, pk_pedido):
    try:
        pedido = Pedido.objects.get(id=pk_pedido)
        pedido.btn_finalizado = True
        pedido.save()
        motorista = Motorista.objects.get(user=request.user)
        motorista.ocupado = False
        motorista.save()
        message = "O motorista " + request.user.first_name + " finalizou por completo a ROTA ID #" + str(
            pedido.pk) + ". Se desejar confirmar, ligue para o motorista: " + motorista.phone
        n = Notification(type_message='ALL_DELIVERED', to=pedido.estabelecimento.user, message=message)
        n.save()
        message = 'Voce concluiu a Rota, se voce estiver com algum material (maquineta ou bag) da Loja ' + pedido.estabelecimento.user.first_name + ',  favor devolver. Obrigado!'
        messages.success(request, message)
        return HttpResponseRedirect('/app/pedidos/motorista/')
    except:
        messages.error(request, 'Este pedido foi deletado pela Loja')
        return HttpResponseRedirect('/app/pedidos/motorista/')


@require_http_methods(["GET"])
def get_pedidos(request):
    pedidos = Pedido.objects.filter(status=True)
    if len(pedidos) > 0:
        return JsonResponse({'result': '1'})
    return JsonResponse({'result': '0'})
