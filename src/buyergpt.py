from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.serpapi import SerpAPIWrapper
from decouple import config
from src.translator import Translator
from src.utils import shorten_url

NUMBER_RESULTS_FAST = 3
NUMBER_RESULTS_DEEP = 50

class BuyerGPT():
    def __init__(self):
        self.prefix = """"You are a conversational agent called ShopperGPT.\
                        \
                        Your tasks consist of providing information on the best offers on products. Your are a NataSquad.com service. You can receive chat messages or audio messages\n"""
        # Initialize OpenAI with API key
        openai_api_key = config('OPENAI_API_KEY')
        self.llm = OpenAI(
            openai_api_key=openai_api_key,
            model_name="gpt-4o-mini",  # Updated to a current model
            #temperature=0.7
        )
        
        # Initialize SerpAPI
        serpapi_api_key = config('SERPAPI_API_KEY')
        self.serpapi_wrapper = SerpAPIWrapper(serpapi_api_key=serpapi_api_key)
        self.serpapi_wrapper.params['engine'] = 'google_shopping'
        
        self.translator = Translator()

    def run(self, human_input="", model_type="fast"):
        print(f"Original input: {human_input}")
        
        input_language = self.translator.detect_language(llm=self.llm, input_text=human_input)
        print(f"Detected language: {input_language}")
        
        translated_input = self.translator.translate(llm=self.llm, 
                                                input_text=human_input, 
                                                source_language=input_language, 
                                                destination_language='English')
        print(f"Translated input: {translated_input}")
        
        domain = self._identify_domain(translated_input)
        print(f"Identified domain: {domain}")
        
        response = self._generate_response(domain, translated_input, input_language, model_type)
        print(f"Generated response: {response}")
        
        return response

    def _identify_domain(self, human_input):
        template = self.prefix + '\n'
        template += """
                    The user makes you a query message and you must identify the domain he is talking about among these domains:\
                    \
                    -greeting: The user greets, says good bye, says hi or hello, or ask things about you or who you are.\
                    \
                    -offers: The user talks to you about product offers or wants to buy something\
                    \
                    -improvements: The user asks you for your next releases or next features you will have implemented, like the functionalities of you as a service\
                    \
                    -other: The user talks about something else than the other domains\
                    \
                    Just output the name of the most possible domain among those given before using lowercase, nothing else.\
                    \
                    Human: {human_input}\
                    \
                    Domain:\
                    """

        try:
            domain = self._execute_llm(template=template, input_variables={"human_input": human_input}, temperature=0)
            domain = domain.strip().lower()
            print(f"Raw domain response: {domain}")
            return domain
        except Exception as e:
            print(f"Error in domain identification: {str(e)}")
            return "other"

    def _generate_response(self, domain, human_input, destination_language, model_type):
        template = self.prefix + '\n'
        input_variables = {'human_input': human_input}
        response = ""  # Initialize response with default value

        if 'greeting' in domain:
            template += 'The user is greeting you, so you must answer him politely and if he is asking for information about who you are you must explain him you job. Remember to say that you are a NataSquad.com service\n Human. And make him a question asking for your functionalities.\n Human: {human_input}\nChatbot:'
            response = self._execute_llm(template, input_variables, temperature=0.9)
            response = self.translator.translate(self.llm, input_text=response, destination_language=destination_language)

        elif 'other' in domain:
            template += 'The user is talking about something you are not able to answer. Tell him politely that you cannot answer that question and explain your goals to him. And make him a question asking him for your functionalities\n Human: {human_input}\nChatbot:'
            response = self._execute_llm(template, input_variables, temperature=0.9)
            response = self.translator.translate(self.llm, input_text=response, destination_language=destination_language)

        elif 'improvements' in domain:
            template += 'The user is talking about the improvements and the next features you will have. Tell him politely that you are in process to have a database implementation for human conversations and users and there is some work for improving user experience when using you\n Human: {human_input}\nChatbot:'
            response = self._execute_llm(template, input_variables, temperature=0.9)
            response = self.translator.translate(self.llm, input_text=response, destination_language=destination_language)

        elif 'offers' in domain:
            try:
                if model_type.lower() == 'fast':
                    shopping_results = self._get_shopping_results(human_input, NUMBER_RESULTS_FAST)
                    offers = self._get_best_offers(human_input, shopping_results, model_type)
                else:
                    shopping_results = self._get_shopping_results(human_input, NUMBER_RESULTS_DEEP)
                    offers = self._get_best_offers(human_input, shopping_results, model_type) 
                response = self._format_offers_response(offers, destination_language, model_type)
            except Exception as e:
                error_msg = f"Sorry, I encountered an error while searching for offers: {str(e)}"
                response = self.translator.translate(self.llm, input_text=error_msg, destination_language=destination_language)
        
        else:
            # Default response if domain is not recognized
            default_msg = "I'm sorry, I don't understand your request. Could you please try rephrasing it?"
            response = self.translator.translate(self.llm, input_text=default_msg, destination_language=destination_language)
        
        return response
    
    def _get_shopping_results(self, human_input, number_results):
        try:
            results = self.serpapi_wrapper.results(query=human_input)
            print(f"SerpAPI results received: {len(results.get('shopping_results', []))} items")
            return results["shopping_results"][0:number_results]
        except Exception as e:
            print(f"Error in shopping results: {str(e)}")
            raise
    
    def _get_best_offers(self, human_input, shopping_results, model_type):
        try:
            offers = []
            for result in shopping_results:
                title = result.get("title", "No title available")
                price = result.get("price", "Price not available")
                link = result.get("link", result.get("product_link", "Link not available"))
                offers.append((title, price, link))
                
            print(f"Processed {len(offers)} offers")
                
            if model_type.lower() == 'fast':
                return offers[:NUMBER_RESULTS_FAST]
            
            offers.sort(key=self._compare_offers(human_input))
            return offers[0:NUMBER_RESULTS_FAST]
        except Exception as e:
            print(f"Error processing offers: {str(e)}")
            raise

    def _compare_offers(self, human_input):
        def comparer(offer):
            inp = human_input
            template = """Given user input indicating their desire for offers for a given product, Return a single integer value between 0 and 10 indicating how good the offer is. Just print the result:\
            Human Input: {human_input}
            \
            Offer: {offer}\
            \
            Result:"""
            input_variables = {"human_input":inp, "offer":(offer[0], offer[1])}
            response = int(self._execute_llm(template=template, input_variables=input_variables, temperature=0))
            return response
        return comparer

    def _format_offers_response(self, offers, destination_language, model_type):
        try:
            offers_main_words = [
                'This is what I have found so far using {} model:'.format(model_type),
                'Product',
                'Price',
                'Link'
            ]
            
            print(f"Translating main words to {destination_language}")
            translated_main_words = [
                self.translator.translate(
                    llm=self.llm,
                    input_text=main_word,
                    destination_language=destination_language
                ) for main_word in offers_main_words
            ]
            
            offers_response = translated_main_words[0] + '\n\n'
            
            for offer in offers:
                try:
                    shortened_link = shorten_url(offer[2]) if 'http' in offer[2] else offer[2]
                    offers_response += '{}: {}\n{}: {}\n{}: {}\n\n'.format(
                        translated_main_words[1], offer[0],
                        translated_main_words[2], offer[1],
                        translated_main_words[3], shortened_link
                    )
                except Exception as e:
                    print(f"Error formatting individual offer: {str(e)}")
                    continue
                    
            print(f"Successfully formatted {len(offers)} offers")
            return offers_response
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error while searching for offers: {str(e)}"
            return self.translator.translate(
                self.llm,
                input_text=error_msg,
                destination_language=destination_language
            )

    def _execute_llm(self, template, input_variables, temperature=0.7):
        #self.llm.temperature = temperature
        prompt = PromptTemplate(template=template, input_variables=list(input_variables.keys()))
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)
        response = llm_chain.run(**input_variables)
        return response