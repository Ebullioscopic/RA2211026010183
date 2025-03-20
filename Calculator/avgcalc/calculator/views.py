from django.shortcuts import render
import copy
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

window_store = []
WINDOW_SIZE = 10

API_URLS = {
    'p': 'http://20.244.56.144/test/primes',
    'f': 'http://20.244.56.144/test/fibo',
    'e': 'http://20.244.56.144/test/even',
    'y': 'http://20.244.56.144/test/rand'
}

@api_view(['GET'])
def average_calculator(request, numberid):
    global window_store
    if numberid not in API_URLS:
        return Response({"error": "Invalid numberid provided."}, status=status.HTTP_400_BAD_REQUEST)
    window_prev_state = copy.deepcopy(window_store)
    numbers_received = []
    try:
        api_url = API_URLS[numberid]
        response = requests.get(api_url, timeout=0.5)
        if response.status_code == 200:
            resp_data = response.json()
            numbers_received = resp_data.get("numbers", [])
        else:
            numbers_received = []
    except Exception:
        numbers_received = []
    for num in numbers_received:
        if num not in window_store:
            window_store.append(num)
            if len(window_store) > WINDOW_SIZE:
                window_store.pop(0)
    if window_store:
        avg_value = sum(window_store) / len(window_store)
    else:
        avg_value = 0.0
    response_payload = {
        "windowPrevState": window_prev_state,
        "windowCurrState": window_store,
        "numbers": numbers_received,
        "avg": float(f"{avg_value:.2f}")
    }
    return Response(response_payload, status=status.HTTP_200_OK)

