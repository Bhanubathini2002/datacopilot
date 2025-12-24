from abc import ABC
from .core import Agent
from dbconnectors import bqconnector
from utilities import PROMPTS, format_prompt,PROJECT_ID,BQ_REGION
from vertexai.generative_models import Content, Part, GenerationConfig
from google.cloud.aiplatform import telemetry
import vertexai


vertexai.init(project=PROJECT_ID,location=BQ_REGION )


class BuildSQLAgent(Agent, ABC):

    agentType: str = "BuildSQLAgent"

    def __init__(self, model_id = 'gemini-2.5-pro'): 
        super().__init__(model_id=model_id)
        
    def build_sql(self,source_type,user_grouping, user_question,session_history,tables_schema,columns_schema, similar_sql, max_output_tokens=2048, temperature=0.4, top_p=1, top_k=32):
        not_related_msg=f'''select 'Question is not related to the dataset' as unrelated_answer;'''
        
        if source_type=='bigquery':

            from dbconnectors import bq_specific_data_types
            specific_data_types = bq_specific_data_types()


        if f'usecase_{source_type}_{user_grouping}' in PROMPTS:
            usecase_context = PROMPTS[f'usecase_{source_type}_{user_grouping}']
        else:
            usecase_context = "No extra context for the usecase is provided"
            
        context_prompt = PROMPTS[f'buildsql_{source_type}']


        context_prompt = format_prompt(context_prompt,
                                       specific_data_types = specific_data_types,
                                       not_related_msg = not_related_msg, 
                                       usecase_context = usecase_context,
                                       similar_sql=similar_sql, 
                                       tables_schema=tables_schema, 
                                       columns_schema = columns_schema)

        # print(f"Prompt to Build SQL: \n{context_prompt}") 

        # Chat history Retrieval

        chat_history=[]
        for entry in session_history:
            
            timestamp = entry["timestamp"]
            timestamp_str = timestamp.isoformat(timespec='auto')

            user_message = Content(
                parts=[Part.from_text(entry["user_question"])],  
                role="user"
            )

            bot_message = Content(
                parts=[Part.from_text(entry["bot_response"])],
                role="assistant"
            )
            chat_history.extend([user_message, bot_message])  # Add both to the history
        

        # print("Chat History Retrieved")

        if self.model_id == 'codechat-bison-32k':
            with telemetry.tool_context_manager('opendataqna-buildsql-v2'):
            
                chat_session = self.model.start_chat(context=context_prompt)
        elif 'gemini' in self.model_id:
            # New google-genai client (Gemini 2.x models)
            with telemetry.tool_context_manager("opendataqna-buildsql-v2"):
                try:
                    # Directly call the Gemini API
                    response = self.model.models.generate_content(
                        model=self.model_id,
                        contents=context_prompt
                    )

                    # Extract the text output
                    result_text = getattr(response, "text", "")

                    # If you need to mimic "chat_session" variable from before
                    chat_session = {"response": result_text}

                except Exception as e:
                    print(f"Error in Gemini generate_content: {e}")
                    chat_session = {"response": ""}
        

        if session_history is None or not session_history:
            concated_questions = None
            re_written_qe = None
            previous_question = None
            previous_sql = None

        else:
            concated_questions,re_written_qe=self.rewrite_question(user_question,session_history)
            previous_question, previous_sql = self.get_last_sql(session_history)


        build_context_prompt=f"""

        Below is the previous user question from this conversation and its generated sql. 

        Previous Question:  {previous_question} 

        Previous Generated SQL : {previous_sql}

        Respond with 

        Generate SQL for User Question : {user_question}

        Note: In BigQuery, always qualify tables with the full path in backticks, 
        using the format project_id.dataset_name.table_name — for example, 
        leafy-guide-482019-n1.imdb_ratings.reviews.
        """

        # print("BUILD CONTEXT ::: "+str(build_context_prompt))


        with telemetry.tool_context_manager('opendataqna-buildsql-v2'):
            try:
                # Call Gemini 2.5 Pro directly using google-genai client
                response = self.model.models.generate_content(
                    model=self.model_id,
                    contents=build_context_prompt
                )

                # Extract and clean generated SQL text
                generated_sql = (
                    getattr(response, "text", "")
                    .replace("```sql", "")
                    .replace("```", "")
                    .strip()
                )

            except Exception as e:
                print(f"Error generating SQL with Gemini: {e}")
                generated_sql = ""

        # Optional: ensure generated_sql is clean after exiting telemetry context
        generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()

        # print(generated_sql)
        return generated_sql
    

    def rewrite_question(self,question,session_history):
        formatted_history=''
        concat_questions=''
        for i, _row in enumerate(session_history,start=1):
            user_question = _row['user_question']
            sql_query = _row['bot_response']
            # print(user_question)
            formatted_history += f"User Question - Turn :: {i} : {user_question}\n"
            formatted_history += f"Generated SQL - Turn :: {i}: {sql_query}\n\n"
            concat_questions += f"{user_question} "

        # print(formatted_history)


        context_prompt = f"""
            Your main objective is to rewrite and refine the question passed based on the session history of question and sql generated.

            Refine the given question using the provided session history to produce a queryable statement. The refined question should be self-contained, requiring no additional context for accurate SQL generation.

            Make sure all the information is included in the re-written question

            Below is the previous session history:

            {formatted_history}

            Question to rewrite:

            {question}
        """
        re_written_qe = str(self.generate_llm_response(context_prompt))
        

        print("*"*25 +"Re-written question for the follow up:: "+"*"*25+"\n"+str(re_written_qe))

        return str(concat_questions),str(re_written_qe)
    

    def get_last_sql(self,session_history):

        for entry in reversed(session_history): 
            if entry.get("bot_response"):  
                return entry["user_question"],entry["bot_response"]  

        return None



        



