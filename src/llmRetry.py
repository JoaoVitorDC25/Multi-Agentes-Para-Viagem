
from crewai import LLM
import re
import time

from litellm import RateLimitError, ServiceUnavailableError

class LLMComRetentativa(LLM):
    """
    LLM com retentativa para lidar com erros de limite de taxa e indisponibilidade.
    """
    
    def call(self, *args, **kwargs):
        max_tentativas = 4  # Uma tentativa inicial e até três repetições

        mensagens = args[0] if args else kwargs.get("messages", [])

        print(
            f"[LLM] Entrada aproximada: {len(str(mensagens))} caracteres.",
            flush=True,
        )
        
        for tentativa in range(1, max_tentativas + 1):
            try:
                return super().call(*args, **kwargs)

            except (RateLimitError, ServiceUnavailableError) as erro:
                if tentativa == max_tentativas:
                    raise

                mensagem = str(erro)

                if isinstance(erro, RateLimitError):
                    # Não adianta esperar se a chamada, sozinha,
                    # já ultrapassa o limite informado.
                    valores = re.search(
                        r"Limit\s*:?\s*(\d+).*?Requested\s*:?\s*(\d+)",
                        mensagem,
                        flags=re.IGNORECASE | re.DOTALL,
                    )

                    if valores:
                        limite, solicitado = map(int, valores.groups())

                        if solicitado > limite:
                            raise

                    # Aproveita a espera informada pela Groq.
                    espera_informada = re.search(
                        r"try again in\s+([\d.]+)\s*s",
                        mensagem,
                        flags=re.IGNORECASE,
                    )

                    if espera_informada:
                        espera = float(espera_informada.group(1)) + 2
                    else:
                        # Outros limites podem exigir uma espera diferente.
                        # Sem prazo informado, deixa o erro seguir.
                        raise

                else:
                    # Sobrecarga temporária: 10, 20 e 40 segundos.
                    espera = 10 * (2 ** (tentativa - 1))

                print(
                    f"[LLM] {type(erro).__name__}. "
                    f"Aguardando {espera:.1f}s antes da tentativa "
                    f"{tentativa + 1}/{max_tentativas}.",
                    flush=True,
                )

                time.sleep(espera)