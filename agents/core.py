from google import genai
from abc import ABC
from google.cloud.aiplatform import telemetry

# import vertexai


# from utilities import PROJECT_ID,BQ_REGION
# vertexai.init(project=PROJECT_ID, location=BQ_REGION)

class Agent(ABC):
    """
    The core class for all Agents
    """

    agentType: str = "Agent"

    def __init__(self,model_id:str):
        """
        model_id is the Model ID for initialization
        """
        self.model_id = model_id 

        if model_id == 'gemini-2.5-pro':
            with telemetry.tool_context_manager('opendataqna'):
                print("Model is Gemini 2.5 Pro (google-genai client)")
                
                # Initialize new Gemini API client
                self.model_id = "gemini-2.5-pro"
                self.model = genai.Client(api_key='')

                # google-genai handles safety internally; you can keep this for consistency
                self.safety_settings = None      
        else:
            raise ValueError("Please specify a compatible model.")
        

    def generate_llm_response(self, prompt):
        try:
            response = self.model.models.generate_content(
                model=self.model_id,
                contents=prompt
            )

            # get the text output safely
            result = response.text if hasattr(response, "text") else ""
            return str(result).replace("sql", "").replace("", "").rstrip("\n")

        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return ""
        

    def rewrite_question(self,question,session_history):
        formatted_history=''
        concat_questions=''
        for i, _row in enumerate(session_history,start=1):
            user_question = _row['user_question']
            # print(user_question)
            formatted_history += f"User Question - Turn :: {i} : {user_question}\n"
            concat_questions += f"{user_question} "

        # print(formatted_history)


        context_prompt = f"""
            Your main objective is to rewrite and refine the question based on the previous questions that has been asked.

            Refine the given question using the provided questions history to produce a standalone question with full context. The refined question should be self-contained, requiring no additional context for answering it.

            Make sure all the information is included in the re-written question. You just need to respond with the re-written question.

            Below is the previous questions history:

            {formatted_history}

            Question to rewrite:

            {question}
        """
        re_written_qe = str(self.generate_llm_response(context_prompt))
        

        print("*"*25 +"Re-written question:: "+"*"*25+"\n"+str(re_written_qe))

        return str(concat_questions),str(re_written_qe)
        
