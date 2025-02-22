from django.urls import path
from .views import  (verify_payment, InitiatePayment, InvoiceViewSet, download_receipt)

urlpatterns = [
    path('invoice/', InvoiceViewSet.as_view({'get':'list'}), name='invoice'),
    path("initiate-payment/", InitiatePayment.as_view(), name='initiate-payment'),
    path("verify-payment/", verify_payment, name="verify_payment"),
     path('receipt/<str:transaction_id>/', download_receipt, name='generate_receipt'),
]
