from google.cloud import bigquery


async def store_schema_embeddings(table_details_embeddings, 
                            tablecolumn_details_embeddings, 
                            project_id,
                            instance_name,
                            database_name,
                            schema,
                            database_user,
                            database_password,
                            region,
                            VECTOR_STORE):
    """ 
    Store the vectorised table and column details in the DB table.
    This code may run for a few minutes.  
    """


    if VECTOR_STORE == "bigquery-vector": 
         
        client=bigquery.Client(project=project_id)

        #Store table embeddings
        client.query_and_wait(f'''CREATE TABLE IF NOT EXISTS `{project_id}.{schema}.table_details_embeddings` (
            source_type string NOT NULL, user_grouping string NOT NULL, table_schema string NOT NULL, table_name string NOT NULL, content string, embedding ARRAY<FLOAT64>)''')
        #job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")

        delete_conditions = table_details_embeddings[['user_grouping', 'table_name']].apply(tuple, axis=1).tolist()
        where_clause = " OR ".join([f"(user_grouping = '{cond[0]}' AND table_name = '{cond[1]}')" for cond in delete_conditions])

        delete_query = f"""
        DELETE FROM `{project_id}.{schema}.table_details_embeddings`
        WHERE {where_clause}
        """
        client.query_and_wait(delete_query)
        
        client.load_table_from_dataframe(table_details_embeddings,f'{project_id}.{schema}.table_details_embeddings')


        #Store column embeddings
        client.query_and_wait(f'''CREATE TABLE IF NOT EXISTS `{project_id}.{schema}.tablecolumn_details_embeddings` (
            source_type string NOT NULL,user_grouping string NOT NULL, table_schema string NOT NULL, table_name string NOT NULL, column_name string NOT NULL,
            content string, embedding ARRAY<FLOAT64>)''')
        #job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")

        delete_conditions = tablecolumn_details_embeddings[['user_grouping', 'table_name', 'column_name']].apply(tuple, axis=1).tolist()
        where_clause = " OR ".join([f"(user_grouping = '{cond[0]}' AND table_name = '{cond[1]}' AND column_name = '{cond[2]}')" for cond in delete_conditions])

        delete_query = f"""
            DELETE FROM `{project_id}.{schema}.tablecolumn_details_embeddings`
            WHERE {where_clause}
            """
        client.query_and_wait(delete_query)

        client.load_table_from_dataframe(tablecolumn_details_embeddings,f'{project_id}.{schema}.tablecolumn_details_embeddings')

        client.query_and_wait(f'''CREATE TABLE IF NOT EXISTS `{project_id}.{schema}.example_prompt_sql_embeddings` (
                              user_grouping string NOT NULL, example_user_question string NOT NULL, example_generated_sql string NOT NULL,
                              embedding ARRAY<FLOAT64>)''')
                              
    else: raise ValueError("Please provide a valid Vector Store.")
    return "Embeddings are stored successfully"



