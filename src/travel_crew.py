import os

from crewai import Agent, Task, Crew, Process
from crewai_tools import TavilySearchTool

from llmRetry import LLMComRetentativa


def criar_equipe_viagem(
    city,
    days,
    interests,
    groq_api_key,
    tavily_api_key,
    ):
    
    llm = LLMComRetentativa(
        model="groq/qwen/qwen3.8-27b",
        api_key=groq_api_key,
        temperature=0.5,
        max_completion_tokens=800,
        reasoning_effort="none")
    
    search_tool = TavilySearchTool(
        max_results=3,
        search_depth="basic",
        include_answer=False,
        include_raw_content=False,
        include_images=False,
        )

    if "max_content_length_per_result" in type(search_tool).model_fields:
        search_tool.max_content_length_per_result = 500
        print(
            "[Tavily] Trechos limitados a 500 caracteres por resultado.",
            flush=True,
        )
                
    # ----- Agentes -----
                
    agente_guia_viagem = Agent(
                    
        role = f"Especialista Local de {city}",
                    
        goal = f"Fornecer as melhores sugestões de locais para uma viagem de {days} dias em {city}, com foco em {interests}.",
                    
        backstory = f"Você é um guia turistico local de {city}, apaixonado por compartilhar os segredos da sua cidade.",
                    
        llm = llm,
                     
        tools = [search_tool],
                    
        allow_delegation = False,
                    
        verbose = False,
                    
        max_iter=3
    ) 
                
    agente_planejador_viagem = Agent(
        role = "Planejador Logístico de Viagens", 
                    
        goal = f"Organizar as sugestões em um roteiro lógico e eficiente para {days} dias.",    
                    
        backstory = "Você é um especialista em logística que agrupa atividades por proximidade e horários.",
                    
        llm = llm,
                    
        allow_delegation = False,
                    
        verbose = False,
                    
        max_iter=3
    )
                
    agente_gerador_de_roteiro = Agent(
        role = "Revisor e Escritor de Roteiros",
                    
        goal = "Transformar o esboço em um itinerário diário detalhado e agradável em Markdown.",
                    
        backstory = "Você é um concienrge de hotel 5 estrelas.",
                    
        llm = llm,
                    
        allow_delegation = False,
                    
        verbose = False,
                    
        max_iter=3
   )
                
    # ----- Tarefas -----
                
    tarefa_pesquisa = Task(
        description=(
            f"Use a ferramenta de pesquisa para buscar atrações e opções "
            f"gastronômicas em {city}, considerando os interesses: {interests}. "
            f"Reúna opções suficientes para distribuir uma viagem de {days} dias. "
            "Priorize fontes oficiais e identifique o bairro ou região. "
            "Não invente URLs, horários, preços ou vínculos institucionais. "
            "Se uma informação não puder ser confirmada, indique isso."
        ),

        expected_output=(
            f"Lista objetiva de aproximadamente {3 * days} opções, "
            "incluindo atrações e gastronomia. "
            "Para cada opção: nome, região, descrição de uma frase curta "
            "e URL da fonte consultada. Evite introdução."
        ),

        agent=agente_guia_viagem
    )
                
    tarefa_pesquisa.description += (
        " Faça no máximo duas consultas à ferramenta: "
        "uma sobre atrações e outra sobre gastronomia e os interesses informados. "
        "Depois, entregue a síntese com os resultados disponíveis e suas fontes. "
        "Não repita consultas apenas para obter mais detalhes. "
        "Sinalize informações que não conseguiu confirmar."
    )
                
    tarefa_planejamento = Task(
        description=(
            f"Organize as opções pesquisadas em {days} dias em {city}. "
            f"Considere os interesses: {interests}. "
            "Agrupe atividades próximas e considere o tempo de deslocamento. "
            "Inclua todos os dias, do primeiro ao último. "
            "Não apresente horários de funcionamento como confirmados "
            "quando a pesquisa não os tiver verificado."
        ),

        expected_output=(
            f"Esboço compacto contendo exatamente {days} dias numerados. "
            "Para cada dia: manhã, tarde e noite, com atividades "
            "e regiões correspondentes. Preserve as URLs das opções utilizadas. "
            "Sem introdução ou conclusão."
        ),

        agent=agente_planejador_viagem,
        context=[tarefa_pesquisa]
    )
                
    tarefa_roteiro = Task(
        description=(
            f"Escreva um roteiro em Markdown para {days} dias em {city}, "
            "usando o planejamento recebido. "
            f"Inclua obrigatoriamente todos os dias, de 1 a {days}. "
            "Comece diretamente pelo Dia 1, sem apresentação ou boas-vindas. "
            "Use tópicos curtos para manhã, tarde e noite. "
            "Distribua o espaço entre todos os dias: não detalhe excessivamente "
            "o primeiro dia deixando os demais incompletos. "
            "Preserve as fontes consultadas e não invente informações."
        ),

        expected_output=(
            f"Markdown com exatamente {days} seções, "
            "usando os títulos '## Dia 1', '## Dia 2' e assim por diante. "
            "Cada seção deve conter manhã, tarde e noite, "
            "com uma frase curta por período. "
            "Acrescente apenas dicas essenciais e links das fontes utilizadas."
        ),

        agent=agente_gerador_de_roteiro,
        context=[tarefa_planejamento]
    )

    equipe_agentes_ia = Crew(
                    
        agents = [agente_guia_viagem, agente_planejador_viagem, agente_gerador_de_roteiro],
                    
        tasks = [tarefa_pesquisa, tarefa_planejamento, tarefa_roteiro],
                    
        process = Process.sequential,
                    
        max_rpm =1,
                    
        verbose = False
        )
    
    return equipe_agentes_ia