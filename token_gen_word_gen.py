# # 32b token generator

# import secrets
#
# def generate_secret():
#     return secrets.token_hex(32)  # 32 bytes = 256 bits
#
# secret = generate_secret()
# print("Generated Secret:", secret)


# # API word generator (parser)

# import requests
#
# api_url = 'https://api.api-ninjas.com/v1/randomword/?type=noun'
# response = requests.get(api_url, headers={'X-Api-Key': 'PIun2cZnuHRZGKW/btYQUw==PJ9WTks49Tey9fhk'})
# if response.status_code == requests.codes.ok:
#     json_response = response.json()
#     print(json_response['word'])
# else:
#     print("Error:", response.status_code, response.text)
