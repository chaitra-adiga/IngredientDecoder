import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from django.conf import settings

class IngredientAnalyzer:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=settings.API_KEY,
        )
        
        self.prompt = PromptTemplate(
            input_variables=["ingredients", "product_type"],
            template="""
            Analyze the following ingredients for a {product_type} product:
            
            {ingredients}
            
            Return a JSON response with this exact structure:
            {{
                "ingredient_analysis": [
                    {{
                        "name": "ingredient name",
                        "description": "brief description of what this ingredient is",
                        "toxicity_rating": rating from 1-10 (10 being most toxic),
                        "health_concerns": ["concern1", "concern2"],
                        "common_uses": "why this ingredient is used in products"
                    }},
                    ...repeat for each ingredient...
                ],
                "overall_rating": rating from 1-10 (10 being most toxic),
                "summary": "brief summary of overall product safety"
            }}
            
            Be scientific and factual. Consider both short-term and long-term health implications.
            """
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def analyze(self, ingredients_text, product_type):
        """Analyze ingredients and return structured analysis"""
        try:
            result = self.chain.run(ingredients=ingredients_text, product_type=product_type)
            parsed_result = json.loads(result)
            return parsed_result
        except Exception as e:
            print(f"Error analyzing ingredients: {e}")
            return None