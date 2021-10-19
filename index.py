import re
import aiohttp
import asyncio


async def run(username, password):
    session = aiohttp.ClientSession()
    data = {
        'client_id': 'play-valorant-web-prod',
        'nonce': '1',
        'redirect_uri': 'https://playvalorant.com/opt_in',
        'response_type': 'token id_token',
        'scope': 'account openid'
    }
    await session.post('https://auth.riotgames.com/api/v1/authorization', json=data)

    data = {
        'type': 'auth',
        'username': username,
        'password': password
    }
    try:
        async with session.put('https://auth.riotgames.com/api/v1/authorization', json=data) as r:
            data = await r.json()
        pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
        data = pattern.findall(data['response']['parameters']['uri'])[0]
        access_token = data[0]

        headers = {
            'Authorization': f'Bearer {access_token}',
        }
    except KeyError:
        print('Can\'t login')
        exit()

    async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
        data = await r.json()
    entitlements_token = data['entitlements_token']

    async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
        data = await r.json()
        user_id = data['sub']
        print('Player id', user_id)
        print('Player Locale:', data['player_locale'])
        print('Email Verified:', data['email_verified'])
        print('Phone Number Verified:', data['phone_number_verified'])
        print('Username:', data['acct']['game_name'] + '#' + data['acct']['tag_line'])
    headers['X-Riot-Entitlements-JWT'] = entitlements_token

    await session.close()


if __name__ == '__main__':
    username = input('Username: ')
    password = input('Password: ')
    asyncio.get_event_loop().run_until_complete(run(username, password))
