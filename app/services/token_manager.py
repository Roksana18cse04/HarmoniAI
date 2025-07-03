from app.services.price_calculate import count_tokens

class TokenManager:
    def __init__(self, model, prompt):
        self.model = model
        self.prompt = prompt
    # fetch user's available token

    # fetch models input and output pricing

    # for prompt, calculate input_token=count_tokens(self.prompt, self.model)
    # calucate input_price= input_token*input_pricing

    # Estimate token for output
    # calculate output_price=  token*output_pricing

    # total_cost= input_price + output_price

    # convert cost into token= required token

    # check user token with required_token
    # if enough then return true
    # else return false


    # working----------------------------