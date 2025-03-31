from langflow.load import run_flow_from_json
TWEAKS = {
  "ParseData-RfDb1": {
    "sep": "\n",
    "template": "{text}"
  },
  "GoogleGenerativeAIModel-RE7tv": {
    "google_api_key": "gemini_API_KEY",
    "input_value": "",
    "max_output_tokens": 500,
    "model": "gemini-1.5-pro",
    "n": None,
    "stream": False,
    "system_message": "",
    "temperature": 0.1,
    "top_k": None,
    "top_p": None
  },
  "GoogleGenerativeAIModel-FkMev": {
    "google_api_key": "gemini_API_KEY",
    "input_value": "",
    "max_output_tokens": 500,
    "model": "gemini-1.5-flash",
    "n": None,
    "stream": True,
    "system_message": "",
    "temperature": 0.1,
    "top_k": None,
    "top_p": None
  },
  "Prompt-ZVp0Q": {
    "template": "{product-related}\n\nthe info passed above is the name of the brand you work for and the product who's marketing is a part of your job, use the given information to come up with phrases and keywords that can be used when creating marketing campaigns for your product, use your own knowledge to ensure you come up with things that are trendy and suited for your tg\nyou can only answer with 480 characters, so make sure you finish your response withing that limit.",
    "product-related": ""
  },
  "Prompt-ICSuW": {
    "template": "{competition-finding}\n\nthe info passed above is the name of the brand you work for and the product who's marketing is a part of your job, use the given information to find competitors for the product and the brand in this space, make sure to look very carefully through any data you can access, a competitor would be something like, e.g:  if you work for parle and are on the marketing team of parleG, other busicuits targeting the same tg's, having the same flavours, similar price points, these could be your competition, something like oreo won't be a direct competitor although they would be in the busicuits market. all you been told to do is find these competitors and come up with keywords and / or phrases they might be using in their marketing campaigns, these words/phrases will be passed to our internet scraper to find detailed info of these campaigns. ur response should be in a json format under one key, \"keywords-phrases\", do not forget to close you json, you are only allowed 480 tokens so finish your reposne before that and close it.",
    "competition-finding": ""
  },
  "AstraDB-4pww4": {
    "advanced_search_filter": "{}",
    "api_endpoint": "https://f0d66d75-31da-4b86-8f93-13823e7f1f09-us-east-2.apps.astra.datastax.com",
    "batch_size": None,
    "bulk_delete_concurrency": None,
    "bulk_insert_batch_concurrency": None,
    "bulk_insert_overwrite_concurrency": None,
    "collection_indexing_policy": "",
    "collection_name": "product_company_store",
    "embedding_choice": "Embedding Model",
    "keyspace": "",
    "metadata_indexing_exclude": "",
    "metadata_indexing_include": "",
    "metric": "cosine",
    "number_of_results": 4,
    "pre_delete_collection": False,
    "search_filter": {},
    "search_input": "",
    "search_score_threshold": 0,
    "search_type": "Similarity",
    "setup_mode": "Sync",
    "token": "ASTRA_DB_APPLICATION_TOKEN"
  },
  "TextInput-nKikC": {
    "input_value": "use the values that have been entered most recently"
  },
  "Google Generative AI Embeddings-Hvq4z": {
    "api_key": "gemini_API_KEY",
    "model_name": "models/text-embedding-004"
  },
  "TextInput-mNnpM": {
    "input_value": "use any data that u think will be useful "
  },
  "AstraDB-c6VBS": {
    "advanced_search_filter": "{}",
    "api_endpoint": "https://f0d66d75-31da-4b86-8f93-13823e7f1f09-us-east-2.apps.astra.datastax.com",
    "batch_size": None,
    "bulk_delete_concurrency": None,
    "bulk_insert_batch_concurrency": None,
    "bulk_insert_overwrite_concurrency": None,
    "collection_indexing_policy": "",
    "collection_name": "reddit_data",
    "embedding_choice": "Embedding Model",
    "keyspace": "",
    "metadata_indexing_exclude": "",
    "metadata_indexing_include": "",
    "metric": "cosine",
    "number_of_results": 4,
    "pre_delete_collection": False,
    "search_filter": {},
    "search_input": "",
    "search_score_threshold": 0,
    "search_type": "Similarity",
    "setup_mode": "Sync",
    "token": "ASTRA_DB_APPLICATION_TOKEN"
  },
  "ParseData-KVgm3": {
    "sep": "\n",
    "template": "{text}"
  },
  "Prompt-JXn6V": {
    "template": "{context}",
    "context": ""
  },
  "GoogleGenerativeAIModel-vWATi": {
    "google_api_key": "gemini_API_KEY",
    "input_value": "",
    "max_output_tokens": 500,
    "model": "gemini-1.5-pro",
    "n": None,
    "stream": False,
    "system_message": "",
    "temperature": 0.1,
    "top_k": None,
    "top_p": None
  },
  "AstraDB-UkiMI": {
    "advanced_search_filter": "{}",
    "api_endpoint": "https://f0d66d75-31da-4b86-8f93-13823e7f1f09-us-east-2.apps.astra.datastax.com",
    "batch_size": None,
    "bulk_delete_concurrency": None,
    "bulk_insert_batch_concurrency": None,
    "bulk_insert_overwrite_concurrency": None,
    "collection_indexing_policy": "",
    "collection_name": "youtube_data",
    "embedding_choice": "Embedding Model",
    "keyspace": "",
    "metadata_indexing_exclude": "",
    "metadata_indexing_include": "",
    "metric": "cosine",
    "number_of_results": 4,
    "pre_delete_collection": False,
    "search_filter": {},
    "search_input": "",
    "search_score_threshold": 0,
    "search_type": "Similarity",
    "setup_mode": "Sync",
    "token": "ASTRA_DB_APPLICATION_TOKEN"
  },
  "AstraDB-UimWr": {
    "advanced_search_filter": "{}",
    "api_endpoint": "https://f0d66d75-31da-4b86-8f93-13823e7f1f09-us-east-2.apps.astra.datastax.com",
    "batch_size": None,
    "bulk_delete_concurrency": None,
    "bulk_insert_batch_concurrency": None,
    "bulk_insert_overwrite_concurrency": None,
    "collection_indexing_policy": "",
    "collection_name": "insta_data",
    "embedding_choice": "Embedding Model",
    "keyspace": "",
    "metadata_indexing_exclude": "",
    "metadata_indexing_include": "",
    "metric": "cosine",
    "number_of_results": 4,
    "pre_delete_collection": False,
    "search_filter": {},
    "search_input": "",
    "search_score_threshold": 0,
    "search_type": "Similarity",
    "setup_mode": "Sync",
    "token": "ASTRA_DB_APPLICATION_TOKEN"
  },
  "ParseData-unVKE": {
    "sep": "\n",
    "template": "{text}"
  },
  "ParseData-BbnE4": {
    "sep": "\n",
    "template": "{text}"
  },
  "Prompt-tUP7D": {
    "template": "{context}",
    "context": ""
  },
  "Prompt-UYvst": {
    "template": "{context}",
    "context": ""
  },
  "GoogleGenerativeAIModel-fOzQ6": {
    "google_api_key": "gemini_API_KEY",
    "input_value": "",
    "max_output_tokens": 500,
    "model": "gemini-1.5-pro",
    "n": None,
    "stream": False,
    "system_message": "",
    "temperature": 0.1,
    "top_k": None,
    "top_p": None
  },
  "GoogleGenerativeAIModel-QTFy7": {
    "google_api_key": "gemini_API_KEY",
    "input_value": "",
    "max_output_tokens": 500,
    "model": "gemini-1.5-pro",
    "n": None,
    "stream": False,
    "system_message": "",
    "temperature": 0.1,
    "top_k": None,
    "top_p": None
  }
}

result = run_flow_from_json(flow="Untitled document (1).json",
                            session_id="", # provide a session id if you want to use session state
                            fallback_to_env_vars=True, # False by default
                            tweaks=TWEAKS)