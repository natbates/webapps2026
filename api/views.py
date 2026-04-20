from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ConversionSerializer

# Hard coded conversion rates for simplicity. The REST API must return static rates per assignment.
RATES = {
    ('GBP', 'USD'): 1.3,
    ('GBP', 'EUR'): 1.15,
    ('USD', 'GBP'): 0.77,
    ('EUR', 'GBP'): 0.87,
    ('USD', 'EUR'): 0.88,
    ('EUR', 'USD'): 1.14,
}


class ConversionView(APIView):
    """REST API view for currency conversion."""

    def get(self, request, from_curr: str, to_curr: str, amount: str):
        try:
            amt = float(amount)
        except ValueError:
            return Response({'detail': 'invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

        from_curr = from_curr.upper()
        to_curr = to_curr.upper()
        if from_curr == to_curr:
            serializer = ConversionSerializer({'rate': 1.0, 'converted_amount': round(amt, 2)})
            return Response(serializer.data)

        key = (from_curr, to_curr)
        if key not in RATES:
            return Response({'detail': 'unsupported currency'}, status=status.HTTP_404_NOT_FOUND)

        rate = RATES[key]
        converted = round(amt * rate, 2)
        serializer = ConversionSerializer({'rate': rate, 'converted_amount': converted})
        return Response(serializer.data)


def conversion_view(request, from_curr: str, to_curr: str, amount: str):
    """Compatibility wrapper for legacy internal service calls."""
    view = ConversionView.as_view()
    response = view(request, from_curr=from_curr, to_curr=to_curr, amount=amount)
    if hasattr(response, 'render'):
        response.render()
    return response

