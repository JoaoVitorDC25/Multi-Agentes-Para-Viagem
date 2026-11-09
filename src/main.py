import os
import streamlit as st
import traceback

from travel_crew import criar_equipe_viagem

st.set_page_config(page_title="Multi-Agentes Para Viagem", page_icon = ":100:", layout="wide")

with st.sidebar:
    
    st.title("Configuração")
    groq_api_key = st.text_input("Insira sua chave de API Groq:", type="password")
    tavily_api_key = st.text_input("Insira sua chave de API Tavily:", type="password")
    
    st.sidebar.info("Aviso: IA pode gerar respostas imprecisas, incompletas ou erradas. Sempre verifique a informação")
    
    with st.sidebar.expander("Suporte / Fale conosco", expanded=False):
        st.write("Se você tiver alguma dúvida ou precisar de suporte, entre em contato conosco:")
        st.write("Email: joaovitordiasc.25@gmail.com")
        
st.title("Multi-Agentes Para Viagem")
st.subheader("Planeje sua viagem com a ajuda de agentes especializados!")

st.markdown(
    "<h3 style='font-size: 22px; '>Forneça os detalhes da sua viagem e uma equipe de Agenter de IA criará seu roteiro.</h3>",
    unsafe_allow_html=True
)

st.divider()

os.environ["TAVILY_API_KEY"] = tavily_api_key or os.environ.get("TAVILY_API_KEY", "")

os.environ["OPENAI_API_KEY"] = ""

col1, col2 = st.columns(2)

with col1:
    
    city = st.text_input("Cidade de destino:", placeholder="Ex: Paris, França")
    days = st.number_input("Número de dias da viagem:", min_value=1, max_value=30, value=3)

with col2:
    
    interests = st.text_area("Interesses e preferências:", placeholder="Ex: Museus, gastronomia, vida noturna, natureza")

col_btn, col_box =st.columns([2, 1])

with col_btn:
    start_button = st.button("Gerar Roteiro")
    
    
if start_button:
    
    if not groq_api_key:
        st.error("Por favor, insira sua chave de API Groq na barra lateral.")
    
    elif not tavily_api_key:
        st.error("Por favor, insira sua chave de API Tavily na barra lateral.")
        
    elif not city or not days or not interests:
        st.error("Por favor, preencha todos os campos antes de gerar o roteiro.")
        
    else:
        os.environ["GROQ_API_KEY"] = groq_api_key 
        os.environ["TAVILY_API_KEY"] = tavily_api_key
        os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
        
        try:
            
            with st.spinner("Gerando roteiro..."):
                
                equipe_agentes_ia = criar_equipe_viagem(
                    city=city,
                    days=days,
                    interests=interests,
                    groq_api_key=groq_api_key,
                    tavily_api_key=tavily_api_key,
                )

                result = equipe_agentes_ia.kickoff()
                
                with st.expander("Ver resultados de cada agente"):
                    for indice, saida in enumerate(result.tasks_output, start=1):
                        st.markdown(f"### Resultado do agente {indice}")
                        st.markdown(saida.raw)
                
                st.success("Seu roteiro de viagem personalizado está pronto!")
                
                st.markdown(result.raw)

        except Exception as e:
            print("\nERRO AO GERAR O ROTEIRO:", flush=True)
            traceback.print_exc()

            st.error(f"Ocorreu um erro ao gerar o roteiro: {e}")

            with st.expander("Detalhes técnicos do erro"):
                st.code(traceback.format_exc(), language="text")        