import re
import aiohttp
import asyncio
from functools import wraps
from time import time

# ====== Lista de CNAEs válidos ======
CNAES_VALIDOS = {
    '4623108', '4623199', '4632001', '4637107', '4639701', '4639702',
    '4646002', '4647801', '4649408', '4635499', '4637102', '4637199',
    '4644301', '4632003', '4691500', '4693100', '3240099', '4649499',
    '8020000', '4711301', '4711302', '4712100', '4721103', '4721104',
    '4729699', '4761003', '4789005', '4771701', '4771702', '4771703',
    '4772500', '4763601'
}

# ====== Cache decorador com TTL ======
def create_cache(ttl=3600):
    cache_dict = {}
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = str((args, frozenset(kwargs.items())))
            now = time()
            if key in cache_dict:
                cached_time, result = cache_dict[key]
                if now - cached_time <= ttl:
                    return result
            result = await func(*args, **kwargs)
            cache_dict[key] = (time(), result)
            return result
        return wrapper
    return decorator

# ====== Função de limpeza ======
def remover_caracteres_nao_numericos(valor: str) -> str:
    return re.sub(r'\D', '', valor)

# ====== Função principal otimizada ======
@create_cache()
async def buscar_informacoes(cnpj: str) -> tuple:
    cnpj = remover_caracteres_nao_numericos(cnpj.strip())
    if len(cnpj) != 14:
        raise ValueError("CNPJ inválido: deve conter 14 dígitos")
    
    url = f'https://minhareceita.org/{cnpj}'
    timeout = aiohttp.ClientTimeout(total=10)
    connector = aiohttp.TCPConnector(ttl_dns_cache=300)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    dados = await response.json()

                    razao_social = dados.get('razao_social', '').strip()
                    cnae_codigo = str(dados.get('cnae_fiscal', '')).strip()
                    uf = dados.get('uf', '').strip()
                    simples = dados.get('opcao_pelo_simples', False)

                    if not all([razao_social, cnae_codigo, uf]):
                        raise ValueError("Dados incompletos da API")

                    isento = cnae_codigo in CNAES_VALIDOS
                    simples_valor = bool(simples)

                    return razao_social, cnae_codigo, isento, uf, simples_valor
                else:
                    print(f"⚠️ Erro de resposta da API (status {response.status})")
                    return None, None, None, None, None

        except asyncio.TimeoutError:
            print("⏱️ Timeout: A API demorou demais para responder.")
        except aiohttp.ClientError as client_error:
            print(f"🌐 Erro de conexão com a API: {client_error}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

    return None, None, None, None, None

# ====== Processamento em lote (opcional) ======
async def processar_cnpjs(lista_cnpjs: list[str]) -> dict:
    resultados = {}
    tasks = []

    for cnpj in lista_cnpjs:
        cnpj_limpo = remover_caracteres_nao_numericos(cnpj)
        tasks.append(buscar_informacoes(cnpj_limpo))

    resultados_list = await asyncio.gather(*tasks)
    return dict(zip(lista_cnpjs, resultados_list))

def validar_cnpj(cnpj: str) -> bool:
    """Valida se o CNPJ tem 14 dígitos numéricos"""
    cnpj = remover_caracteres_nao_numericos(cnpj)
    return len(cnpj) == 14 and cnpj.isdigit()

async def buscar_informacoes_api_segura(cnpj: str) -> tuple | None:
    try:
        razao_social, cnae, isento, uf, simples = await buscar_informacoes(cnpj)
        if not all([razao_social, cnae, uf]):
            return None
        return razao_social, cnae, isento, uf, simples
    except Exception as e:
        print(f"❌ Erro ao consultar CNPJ na API: {e}")
        return None
