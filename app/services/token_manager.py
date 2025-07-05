from app.services.price_calculate import count_tokens
import requests
from app.services.helper import safe_float

# convert cost into token
def convert_dollar_into_token(dollar):
    api_url = f"https://harmoniai-backend.onrender.com/api/v1/configure/get-configure"
    response = requests.get(api_url).json()
    dollar_per_token = response['data']['dollerPerToken'] 
    token = round( (dollar/dollar_per_token), 10) 
    print(token)
    return token

class TokenManager:
    def __init__(self, auth_token, prompt, model):
        self.auth_token= auth_token
        self.prompt = prompt
        self.model = model

    # fetch user's available token
    def fetch_user_token(self):
        url = f"https://harmoniai-backend.onrender.com/api/v1/users/me"
        headers = {
            "Authorization": self.auth_token
        }
        response = requests.get(url, headers= headers).json()
        # print(response)
        return response['data']['token']

    # fetch models input and output pricing
    def fetch_model_price(self):
        api_url = f"https://harmoniai-backend.onrender.com/api/v1/llm-model/get-all-llm-model?isDeleted=false&searchTerm={self.model}"
        res = requests.get(api_url)
        res.raise_for_status()
        data = res.json()

        results = data['data']['result']
        matched_model = next(
            (item for item in results if item.get('name') == self.model),
            None
        )
        if matched_model:
            input_price = matched_model.get('inputTokenPrice', 0)
            output_price = matched_model.get('outputTokenPrice', 0)
        else:
            print(f"[price_calculate] No matching model found for: {self.model}")
            input_price = output_price = 0
        print("input------", input_price)
        return input_price, output_price

    # for prompt, calculate input_token=count_tokens(self.prompt, model)
    def estimate_cost(self):
        input_token = count_tokens(self.prompt, self.model)
        input_price, output_price = self.fetch_model_price()
        input_cost= input_token*input_price

        # Estimate token for output
        estimate_output_token = 1000
        output_cost=  estimate_output_token*output_price

        total_cost= input_cost + output_cost
        return total_cost

    # check user token with required_token
    def is_enough_token(self):
        available_token = self.fetch_user_token()
        cost = self.estimate_cost()
        require_token = convert_dollar_into_token(cost)
        print(f"available token = {available_token}, required_token = {require_token}")

        if available_token is not None and available_token >= require_token:
            return True
        return False


    # working----------------------------
if __name__=="__main__":
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2ODRkMTU3ZDI2ZDJjNTc2OGM2MmVjMzUiLCJyb2xlIjoidXNlciIsImlhdCI6MTc1MTU5OTgyMCwiZXhwIjoxODM3OTk5ODIwfQ.TzkiOwXuU5mygJ7a00EToi9KP7ngGY8jOGOK3PKCb9k"
    obj = TokenManager(token, "generate a slogan for movement", 'gpt-4o')
    print( obj.fetch_user_token() )