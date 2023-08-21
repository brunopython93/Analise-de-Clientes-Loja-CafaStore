# IMPORTANDO DADOS DO SISTEMA DA LOJA

import requests
import pandas as pd
from pandas import json_normalize
import json

BLING_SECRET_KEY = "{chave api}}"


def list_products(page=1):
    url = f'https://bling.com.br/Api/v2/pedidos/page={page}/json/'
    payload = {'apikey': BLING_SECRET_KEY, }
    all_products = {'retorno': {'pedidos': []}}

    for i in range(150):
        page = i+1
        url = f'https://bling.com.br/Api/v2/pedidos/page={page}/json/'
        produtos = requests.get(url, params=payload)
        try:
            pagina = produtos.json()['retorno']['pedidos']
            for item in pagina:
                all_products['retorno']['pedidos'].append(item)
        except KeyError:

            break

    df = json_normalize(all_products, meta=['pedidos'])
    return df
produtos = list_products()
df = pd.json_normalize(produtos.explode('retorno.pedidos')['retorno.pedidos'])
#df = df.explode("pedido.itens")

df.to_excel("pedidos completos.xlsx", index=False)
df = pd.read_excel("pedidos completos.xlsx")
for item in df:
    df.rename(columns={item: item[7:]}, inplace = True)
tabela = df[["data", "totalvenda", "cliente.fone", "cliente.nome", "situacao"]]
tabela = tabela[tabela["situacao"]=="Atendido"]
tabela = tabela.drop("situacao", axis=1)

# BUSCANDO CLIENTES ASSÍDUOS QUE NÃO COMPRARAM NO ÚLTIMO MÊS (NESTA PARTE INFORME AS DATAS)
tabela = tabela.dropna(subset=["data", "cliente.nome"])
tabela["data"] = pd.to_datetime(tabela["data"])
lista = []
lista1 = []
lista2 = []
lista3 = []

for i, item in enumerate(tabela["data"]):
    if item >= pd.Timestamp(2023, 4, 1):
        lista.append(tabela.iloc[i, 3])

for i, item in enumerate(tabela["data"]):
    if item >= pd.Timestamp(2023, 4, 1) and item < pd.Timestamp(2023, 5, 1):
        if tabela.iloc[i, 3] in lista:
            lista1.append(tabela.iloc[i, 3])

for i, item in enumerate(tabela["data"]):
    if item >= pd.Timestamp(2023, 5, 1) and item < pd.Timestamp(2023, 6, 1):
        if tabela.iloc[i, 3] in lista1:
            lista2.append(tabela.iloc[i, 3])

for i, item in enumerate(tabela["data"]):
    if item >= pd.Timestamp(2023, 6, 1) and item < pd.Timestamp(2023, 7, 1):
        if tabela.iloc[i, 3] in lista1:
            lista3.append(tabela.iloc[i, 3])
lista4 = lista2.copy()
for item in lista3:
    if item in lista4:
        lista4.remove(item)
tab = tabela[tabela["data"]>pd.Timestamp(2023,4,1)]
tab = tab.drop("data", axis=1)
novotab = pd.DataFrame(columns=["totalvenda", "cliente.fone", "cliente.nome"])
for item in lista4:
    x = (tab[tab["cliente.nome"] == item])
    novotab = pd.concat([novotab, x])

novotab = novotab.groupby(["cliente.nome", "cliente.fone"]).sum()
novotab = novotab[novotab["totalvenda"]>200.0]
display(novotab)

# BUSCANDO CLIENTES NOVOS (INFORME A DATA AO QUAL SE REFERE A CLIENTES NOVOS)
tab = tabela[tabela["data"]>pd.Timestamp(2023,4,1)]
tab = tab.drop("data", axis=1)
novotab = pd.DataFrame(columns=["totalvenda", "cliente.fone", "cliente.nome"])
for item in lista4:
    x = (tab[tab["cliente.nome"] == item])
    novotab = pd.concat([novotab, x])

novotab = novotab.groupby(["cliente.nome", "cliente.fone"]).sum()
novotab = novotab[novotab["totalvenda"]>200.0]
display(novotab)