import stripe
from django.conf import settings
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic import  ListView

from .models import Item
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View

stripe.api_key = settings.STRIPE_SECRET_KEY
class ProductView(View):

    model = Item

    template_name = "product.html"

    def get(self, request, product_id):
        product = get_object_or_404(Item, id=product_id)
        return render(request, self.template_name, {'product': product})


# new

@csrf_exempt
def get_stripe_config(request, slug):
    """ Return public key depends on items' currency."""
    if request.method == 'GET':
        if slug == 'EUR':
            stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}

        if slug == 'USD':
            stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


class CreateCheckoutSessionView(View):
    """ View for creating stripe payment."""
    def get(self, request, *args, **kwargs):
        product_id = kwargs['product_id']
        product = get_object_or_404(Item, id=product_id)
        domain_url = "http://127.0.0.1:8087"
        if settings.DEBUG:
            domain_url = "http://127.0.0.1:8087"
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        "price_data": {
                            "currency": product.currency,
                            "product_data": {"name": product.name},
                            "unit_amount": int(product.price * 100),  # convert dollars into cents
                        },
                        "quantity": 1,
                    },
                ],
                mode='payment',
                success_url=f'{domain_url}/payment_success/',
                cancel_url=f'{domain_url}/payment_failed/',
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as err:
            print(err)  # should be in logs
            return JsonResponse({'error': str(err)})
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here

    return HttpResponse(status=200)




class SuccessView(TemplateView):
    template_name = 'success.html'


class CancelledView(TemplateView):
    template_name = 'cancelled.html'


class ProductListView(ListView):
    """ View for all items."""
    model = Item
    template_name = 'product_list.html'
    context_object_name = 'products'


class ProductDeatilView(ListView):

   template_name = 'product_detail.html'
   model = Item
   def get_context_data(self, **kwargs):
       context_data = super().get_context_data(**kwargs)
       context_data['object_list'] = Item.objects.all()
       return context_data