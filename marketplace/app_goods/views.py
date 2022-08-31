from statistics import mean

from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views import View
from django.views.generic.edit import FormMixin
from django.views.generic import DetailView

from app_goods.models import Product, Reviews
from app_shops.models import ShopProduct
from app_goods.forms import ReviewForm
from cart.forms import CartAddProductForm, CartAddProductShopForm


class ProductDetailView(FormMixin, DetailView):
    """ Представление для получения детальной информации о продукте
    и добавления его в корзину"""
    model = Product
    context_object_name = 'product'
    template_name = 'app_goods/product.html'
    form_class = CartAddProductForm
    extra_context = {'title': 'Товар', 'review_form': ReviewForm, 'reviews': Reviews.objects.all}

    def get_object(self, *args, **kwargs):
        view_object = super(ProductDetailView, self).get_object()
        view_object.views_count += 1
        view_object.save()
        return view_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # считаем среднюю цену товара по магазинам без скидки и со скидкой и добавляем в контекст
        products = ShopProduct.objects.filter(product=self.object.id).select_related('shop', 'product')
        context['price'] = round(mean([product.price for product in products]), 2)
        context['discounted_aver_price'] = round(mean([product.get_discounted_price() for product in products]), 2)
        context['shops'] = products
        if context['shops']:
            if len(context['shops']) > 1:
                for shop in context['shops']:
                    shop.add_to_cart_form = CartAddProductShopForm(initial={'quantity': 1,
                                                                            'shop': shop.shop.name,
                                                                            'product': self.object.id
                                                                            })
            else:
                shop = context['shops'][0]
                shop.add_to_cart_form = CartAddProductShopForm(initial={'quantity': 1,
                                                                        'shop': shop.shop.name,
                                                                        'product': self.object.id
                                                                        })
        return context



class AddReview(View):
    """ Отзыв """

    def post(self, request, slug):
        form = ReviewForm(request.POST)
        product = Product.objects.get(slug=slug)
        if form.is_valid():
            form = form.save(commit=False)
            user = User.objects.get(id=request.user.id)
            form.user = user
            form.email = user.email
            form.product = product

            form.save()

        return redirect(product.get_absolute_url())