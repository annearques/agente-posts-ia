
import streamlit as st
import os
from datetime import date
from google import genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

# Configurar API Key
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# Função para executar agente
def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])
    final_response = ""
    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text is not None:
                    final_response += part.text + "\n"
    return final_response

# Agentes
def agente_buscador(topico, data_de_hoje):
    agente = Agent(
        name="agente_buscador",
        model="gemini-2.0-flash",
        description="Busca notícias relevantes no Google",
        tools=[google_search],
        instruction="""
        Use google_search para buscar no máximo 5 lançamentos muito relevantes sobre o tópico.
        Foque em notícias recentes (último mês) e com entusiasmo do público.
        """
    )
    entrada = f"Tópico: {topico}\nData de hoje: {data_de_hoje}"
    return call_agent(agente, entrada)

def agente_planejador(topico, lancamentos):
    agente = Agent(
        name="agente_planejador",
        model="gemini-2.0-flash",
        description="Planeja postagens com base nas notícias",
        tools=[google_search],
        instruction="""
        Crie um plano para post usando os lançamentos. Use o google_search para aprofundar.
        Escolha o tema mais relevante, defina os pontos-chave e monte o plano de conteúdo.
        """
    )
    entrada = f"Tópico: {topico}\nLançamentos buscados: {lancamentos}"
    return call_agent(agente, entrada)

def agente_redator(topico, plano):
    agente = Agent(
        name="agente_redator",
        model="gemini-2.0-flash",
        description="Cria post para Instagram",
        instruction="""
        Redija um rascunho de post com base no plano. Use linguagem clara, cativante e com hashtags.
        """
    )
    entrada = f"Tópico: {topico}\nPlano: {plano}"
    return call_agent(agente, entrada)

def agente_revisor(topico, rascunho):
    agente = Agent(
        name="agente_revisor",
        model="gemini-2.0-flash",
        description="Revisa o post para Instagram",
        instruction="""
        Revise o rascunho para clareza, concisão e adequação ao público de 18-30 anos.
        Se estiver ótimo, diga: 'O rascunho está ótimo e pronto para publicar!'
        """
    )
    entrada = f"Tópico: {topico}\nRascunho: {rascunho}"
    return call_agent(agente, entrada)

# Interface Streamlit
st.set_page_config(page_title="Post Generator com IA", layout="centered")
st.title("📲 Gerador de Post para Instagram com IA")

topico = st.text_input("Digite um tópico para gerar um post de tendências:")

if st.button("Gerar post"):
    if not topico:
        st.warning("Por favor, digite um tópico.")
    else:
        data = date.today().strftime("%d/%m/%Y")
        with st.spinner("🔎 Buscando notícias..."):
            noticias = agente_buscador(topico, data)
        st.subheader("🧠 Notícias Relevantes")
        st.markdown(noticias)

        with st.spinner("📋 Planejando o conteúdo..."):
            plano = agente_planejador(topico, noticias)
        st.subheader("📌 Plano de Conteúdo")
        st.markdown(plano)

        with st.spinner("✍️ Escrevendo o post..."):
            rascunho = agente_redator(topico, plano)
        st.subheader("📝 Rascunho do Post")
        st.markdown(rascunho)

        with st.spinner("🔍 Revisando o post..."):
            revisao = agente_revisor(topico, rascunho)
        st.subheader("✅ Revisão Final")
        st.markdown(revisao)
