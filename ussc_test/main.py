from aiohttp import web
import json
from currency_converter import CurrencyConverter
import redis

c = CurrencyConverter()
r = redis.Redis(host='127.0.0.1', port=6379)
r.set('RUB', '1')
r.set('USD', str(c.convert(1, 'USD', 'RUB')))
r.set('EUR', str(c.convert(1, 'EUR', 'RUB')))
r.set('GBP', str(c.convert(1, 'GBP', 'RUB')))
r.set('CNY', str(c.convert(1, 'CNY', 'RUB')))

async def update_data():
    r.set('USD', str(c.convert(1, 'USD', 'RUB')))
    r.set('EUR', str(c.convert(1, 'EUR', 'RUB')))
    r.set('GBP', str(c.convert(1, 'GBP', 'RUB')))
    r.set('CNY', str(c.convert(1, 'CNY', 'RUB')))


async def convert(request):
    try:
        input_val = request.query['from']
        output_val = request.query['to']
        input_amount = int(request.query['amount'])

        output_amount = round((input_amount * float(r.get(input_val))) / float(r.get(output_val)), 2)

        response_obj = { 
            'status': 'success',
            'input_currency': input_val,
            'output_currency': output_val,
            'input_amount': str(input_amount),
            'output_amount': str(output_amount),
        }
        return web.Response(text=json.dumps(response_obj), status=200)
    except Exception as e:
        response_obj = { 'status':'failed' , 'message': str(e) }
        return web.Response(text=json.dumps(response_obj), status=500)

async def merge_data(request):
    try:
        merge = bool(int(request.query['merge']))
        if (merge):
            for valute in request.query.values():
                if (valute == '1'):
                    continue
                r.set(valute, str(c.convert(1, valute, 'RUB')))
            response_obj = { 'status': 'success' , 'message': 'Valutes updated' }
            return web.Response(text=json.dumps(response_obj), status=200)
        else:
            await update_data()
            response_obj = { 'status': 'success' , 'message': 'Base updated' }
            return web.Response(text=json.dumps(response_obj), status=200)
        response_obj = { 'status': 'success'}
        return web.Response(text=json.dumps(response_obj), status=200)
    except Exception as e:
        response_obj = { 'status':'failed' , 'message': str(e) }
        return web.Response(text=json.dumps(response_obj), status=500)

app = web.Application()
app.router.add_get('/convert', convert)
app.router.add_post('/database', merge_data)

web.run_app(app)
