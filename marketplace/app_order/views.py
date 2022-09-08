from django.shortcuts import render, redirect
from django.views import View
from .forms import OrderCommentForm
from .models import Order, Delivery, PayMethod
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from app_users.models import Profile
from app_goods.models import Product
from app_shops.models import Shop, ShopProduct
from cart.models import CartItems
from django.conf import settings
from custom_admin.models import DefaultSettings
from django.db.models import Count, F, Value, Subquery, DecimalField, Exists, ExpressionWrapper, FloatField, Sum
from django.db import transaction
from decimal import Decimal
from app_payment.tasks import handle_payment



class OrderView(View):
	
	@staticmethod
	def get(request):
		comment = OrderCommentForm()
		context = dict()
		context['comment'] = comment
		if request.user.is_authenticated:
			user = User.objects.get(id=request.user.id)
			context['user'] = user
			profile = Profile.objects.filter(user_id=request.user.id)
			if profile:
				profile = Profile.objects.get(user_id=request.user.id)
			else:
				role = Role.objects.get(name='покупатель')
				profile = Profile.objects.create(user=user, phone_number='', role=role)
			context['profile'] = profile
			
			cart = CartItems.objects.filter(session_id=request.session.session_key).select_related(
				'product__discount').annotate(price_discount=ExpressionWrapper(
				F('price') * (1 - F('product__discount__discount_value') * Decimal('1.0') / 100),
				output_field=FloatField()), total_sum=Sum('price'), total_sum_with_discount=Sum('price_discount'))
			total_sum = 0
			total_sum_with_discount = 0
			for product in cart:
				total_sum += product.total_sum
				total_sum_with_discount += product.total_sum_with_discount
			context['cart'] = cart
			context['total_sum'] = total_sum
			context['total_sum_with_discount'] = total_sum_with_discount
			
			return render(request, template_name='order/order1.html', context=context)
	
	@staticmethod
	def post(request):
		comment = ''
		comment_form = OrderCommentForm(request.POST)
		if comment_form.is_valid():
			comment = comment_form.cleaned_data.get('comment')
		data = request.POST
		email = data['mail']
		user = User.objects.get(email=email)
		delivery = Delivery.objects.get(title=data['delivery'])
		city = data['city']
		address = data['address']
		pay_method = PayMethod.objects.get(title=data['pay'])
		
		products = CartItems.objects.filter(session_id=request.session.session_key).select_related('product')
		order_goods = {}
		for product in products:
			order_goods[product.product_id] = product.quantity
		Order.objects.create(user=user, order_goods=order_goods, delivery=delivery, city=city,
		                     address=address, pay_method=pay_method, order_comment=comment, payment_error='')
		
		if delivery.id == 1:
			return render(request, template_name='order/payment.html', )
		return render(request, template_name='order/payment_someone.html')


class OrderPayment(View):
	
	@staticmethod
	def post(request):
		card_num = request.POST['numero1']
		user = request.user
		profile = Profile.objects.get(user_id=user.id)
		order = Order.objects.filter(user=user).last()
		payment_amount = order.get_total_cost()
		if order.get_total_cost_with_discount():
			payment_amount = order.get_total_cost_with_discount()
		
		while True:
			res = handle_payment(order.id, card_num, payment_amount)
			if res:
				break
			
		return render(request, template_name='order/progressPayment.html')


@transaction.atomic
def service_payment():
	pass
