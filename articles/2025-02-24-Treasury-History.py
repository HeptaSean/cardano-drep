from datetime import datetime, UTC
import json
import urllib.request
from typing import Optional, Iterator


def koios(path: str,
          select: Optional[list[str]] = None,
          order: Optional[str] = None,
          query: dict[str, str] = {},
          body: Optional[dict] = None) -> Iterator[dict]:
    base_url = f"https://api.koios.rest/api/v1/{path}"
    headers = {'User-Agent': 'HeptaSean/0.1'}
    url_params = {}
    if select:
        url_params['select'] = ','.join(select)
    if order:
        url_params['order'] = order
    for key in query:
        url_params[key] = query[key]
    data = None
    if body:
        data = bytes(json.dumps(body), encoding='utf-8')
        headers['Content-Type'] = 'application/json'
    limit = 1000
    url_params['limit'] = str(limit)
    continued = True
    offset = 0
    while continued:
        continued = False
        url_params['offset'] = str(offset)
        url = base_url + '?' + \
            '&'.join([f"{k}={v}" for (k, v) in url_params.items()])
        if data:
            req = urllib.request.Request(url, data=data, headers=headers)
        else:
            req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            full_range = f"{offset}-{offset + limit - 1}/"
            if response.info()['content-range'].startswith(full_range):
                continued = True
                offset += limit
            results = json.loads(response.read().decode())
            for result in results:
                yield result


reserve_withdrawals = {}
for withdrawal in koios('reserve_withdrawals',
                        select=['epoch_no', 'amount'],
                        order='epoch_no.asc'):
    epoch_no = withdrawal['epoch_no']
    amount = int(withdrawal['amount'])
    if epoch_no not in reserve_withdrawals:
        reserve_withdrawals[epoch_no] = 0
    reserve_withdrawals[epoch_no] += amount

treasury_withdrawals = {}
for withdrawal in koios('treasury_withdrawals',
                        select=['epoch_no', 'amount'],
                        order='epoch_no.asc'):
    epoch_no = withdrawal['epoch_no']
    amount = int(withdrawal['amount'])
    if epoch_no not in treasury_withdrawals:
        treasury_withdrawals[epoch_no] = 0
    treasury_withdrawals[epoch_no] += amount

print("| Epoch ", end="")
print("| Beginning           ", end="")
print("| Reserves                             ", end="")
print("| Treasury                   ", end="")
print("| Withdrawals/Inflow               ", end="")
print("|")
print("|------:", end="")
print("|---------------------", end="")
print("|-------------------------------------:", end="")
print("|---------------------------:", end="")
print("|---------------------------------:", end="")
print("|")
previous_epoch = 0
previous_reserves = 0
previous_treasury = 0
epoch = 240
while True:
    reserves = 0
    treasury = 0
    for totals in koios('totals', query={'_epoch_no': str(epoch)},
                        select=['reserves', 'treasury']):
        reserves = int(totals['reserves'])
        treasury = int(totals['treasury'])
    if not reserves:
        break
    for withdrawal_epoch in reserve_withdrawals:
        if epoch <= withdrawal_epoch:
            reserves -= reserve_withdrawals[withdrawal_epoch]
    if previous_epoch:
        reserves_diff = reserves - previous_reserves
        reserves_percent = abs(reserves_diff) / previous_reserves
        treasury_diff = treasury - previous_treasury
        inflow = treasury_diff + withdrawals
        inflow_percent = inflow / previous_reserves
        print("|       ", end="")
        print("|                     ", end="")
        print(f"| {reserves_diff:+22_d} µADA ", end="")
        print(f"({reserves_percent:5.2%}) ", end="")
        print(f"| {treasury_diff:+21_d} µADA ", end="")
        print(f"| {inflow:19_d} µADA ", end="")
        print(f"({inflow_percent:4.2%}) ", end="")
        print("|")
    print(f"| {epoch:5d} ", end="")
    for epoch_info in koios('epoch_info', query={'_epoch_no': str(epoch)},
                            select=['start_time']):
        start = datetime.fromtimestamp(epoch_info['start_time'], UTC)
        formatted_start = start.strftime('%Y-%m-%d %H:%M:%S')
        print(f"| {formatted_start} ", end="")
    print(f"| {reserves:31_d} µADA ", end="")
    print(f"| {treasury:21_d} µADA ", end="")
    withdrawals = 0
    for withdrawal_epoch in treasury_withdrawals:
        if epoch <= withdrawal_epoch < epoch + 73:
            withdrawals += treasury_withdrawals[withdrawal_epoch]
    print(f"| {withdrawals:27_d} µADA ", end="")
    print("|")
    previous_epoch = epoch
    epoch += 73
    previous_reserves = reserves
    previous_treasury = treasury
