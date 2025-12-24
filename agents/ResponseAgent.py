from .core import Agent
from abc import ABC
from utilities import (PROMPTS,format_prompt)
from google.cloud.aiplatform import telemetry



class ResponseAgent(Agent, ABC):
    """
    An agent that generates natural language responses to user questions based on SQL query results.

    This agent acts as a data assistant, interpreting SQL query results and transforming them into user-friendly, natural language answers. It utilizes a language model (currently Gemini) to craft responses that effectively convey the information derived from the data.

    Attributes:
        agentType (str): Indicates the type of agent, fixed as "ResponseAgent".

    Methods:
        run(user_question, sql_result) -> str:
            Generates a natural language response to the user's question based on the SQL query result.

            Args:
                user_question (str): The question asked by the user in natural language.
                sql_result (str): The result of the SQL query executed to answer the question.

            Returns:
                str: The generated natural language response.
    """


    agentType: str = "ResponseAgent"

    def run(self, user_question, sql_result):

        context_prompt = PROMPTS['nl_reponse']



        context_prompt = format_prompt(context_prompt,
                                       user_question = user_question,
                                       sql_result = sql_result)
                                       
        # print(f"Prompt for Natural Language Response: \n{context_prompt}")


        if "gemini" in self.model_id:
            with telemetry.tool_context_manager("opendataqna-response-v2"):
                try:
                    # Use the new google-genai API call
                    context_query = self.model.models.generate_content(
                        model=self.model_id,
                        contents=context_prompt
                    )

                    # Extract the text result safely
                    generated_sql = str(getattr(context_query, "text", "")).replace("sql", "").replace("", "").rstrip("\n")

                except Exception as e:
                    print(f"Error generating Gemini response: {e}")
                    generated_sql = ""
        else:
            with telemetry.tool_context_manager('opendataqna-response-v2'):
                context_query = self.model.predict(context_prompt, max_output_tokens = 8000, temperature=0)
                generated_sql = str(context_query.candidates[0])
        
        return generated_sql
        
        