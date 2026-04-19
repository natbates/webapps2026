from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound

# Hard coded conversion rates for simplicity; in a real app, these would be dynamic and likely stored in a database or fetched from an external API.

RATES = {
    ('GBP', 'USD'): 1.3,
    ('GBP', 'EUR'): 1.15,
    ('USD', 'GBP'): 0.77,
    ('EUR', 'GBP'): 0.87,
    ('USD', 'EUR'): 0.88,
    ('EUR', 'USD'): 1.14,
}


def conversion_view(request, from_curr: str, to_curr: str, amount: str):
    """Function-based conversion view.

    GET /api/conversion/<from>/<to>/<amount>/ -> JSON
    """
    if request.method != 'GET':
        return HttpResponseBadRequest('only GET allowed')

    try:
        amt = float(amount)
    except Exception:
        return HttpResponseBadRequest('invalid amount')

    from_curr = from_curr.upper()
    to_curr = to_curr.upper()
    if from_curr == to_curr:
        return JsonResponse({"rate": 1.0, "converted_amount": round(amt, 2)})

    key = (from_curr, to_curr)
    if key not in RATES:
        return HttpResponseNotFound('unsupported currency')

    rate = RATES[key]
    converted = round(amt * rate, 2)
    return JsonResponse({"rate": rate, "converted_amount": converted})

