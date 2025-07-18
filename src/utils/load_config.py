
import os
from dotenv import load_dotenv
import yaml
from pyprojroot import here
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from .improved_chain import PrepareImprovedAgent
from typing import List
import spacy

print("Environment variables are loaded:", load_dotenv())


class LoadConfig:
    def __init__(self) -> None:
        with open(here("configs/app_config.yml")) as cfg:
            self.app_config = yaml.safe_load(cfg)

        self.top_k = self.app_config["RAG_config"]["top_k"]

        # Load Gemini model
        self.load_llm_configs()
        self.load_graph_db()
        self.load_GeminiAI_models_and_gpt_agent()

    def load_llm_configs(self):
        self.model_name = os.getenv(self.app_config["llm_config"]["model_name"])
        self.temperature = os.getenv(self.app_config["llm_config"]["temperature"])
        self.embedding_model_name = os.getenv(self.app_config["llm_config"]["embedding_model_name"])
        self.system_message = self.app_config["llm_config"]["system_message"]

    def load_graph_db(self):
        
        self.graph = Neo4jGraph(url=os.getenv("NEO4J_URI"), username=os.getenv("NEO4J_USERNAME"),
                                password=os.getenv("NEO4J_PASSWORD"), database=os.getenv("NEO4J_DATABASE"))


    def embed_text(self, text:str)->List:
        """
        Embeds the given text using the specified model.

        Parameters:
            text (str): The text to be embedded.

        Returns:
            List: A list containing the embedding of the text.
        """
        self.nlp = spacy.load(self.embedding_model_name)
        doc = self.nlp(text)
        return doc.vector # 300-dim vector

    def load_GeminiAI_models_and_gpt_agent(self):
        # For the LLM
        self.llm = ChatGoogleGenerativeAI(
            model = self.model_name,
            temperature = self.temperature,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        
        self.simple_chain = GraphCypherQAChain.from_llm(
            graph=self.graph, llm=self.llm, verbose=True, allow_dangerous_requests=True)
        improved_chain_instance = PrepareImprovedAgent(graph=self.graph, llm=self.llm)
        self.improved_chain = improved_chain_instance.run_pipeline()
