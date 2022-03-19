from functools import reduce

import numpy as np
import pandas as pd
from pandas import set_option

set_option('display.max_rows', 500)
set_option('display.max_columns', 500)
set_option('display.width', 2000)


class lojaMes:
    @property
    def margemLiquida(self):
        return self._margemLiquida

    @margemLiquida.setter
    def margemLiquida(self, valor):
        self._margemLiquida = valor

    @property
    def caixa(self):
        return self._caixa

    @caixa.setter
    def caixa(self, valor):
        self._caixa = valor

    @property
    def estoque(self):
        return self._estoque

    @estoque.setter
    def estoque(self, valor):
        self._estoque = valor

    @property
    def roa(self):
        return self._roa

    @roa.setter
    def roa(self, valor):
        self._roa = valor

    @property
    def entrou_do_mes_passado(self):
        return self._entrou_do_mes_passado

    @entrou_do_mes_passado.setter
    def entrou_do_mes_passado(self, valor):
        self._entrou_do_mes_passado = valor


class loja:

    def __init__(self):
        self._capitalizacao: list = []
        self._por_mes: list = []

    @property
    def margemLiquida(self):
        return self._margemLiquida

    @margemLiquida.setter
    def margemLiquida(self, valor):
        self._margemLiquida = valor

    @property
    def caixa(self):
        return self._caixa

    @caixa.setter
    def caixa(self, valor):
        self._caixa = valor

    @property
    def estoque(self):
        return self._estoque

    @estoque.setter
    def estoque(self, valor):
        self._estoque = valor

    @property
    def meses(self):
        return list(self._meses)

    @meses.setter
    def meses(self, valor):
        self._meses = valor

    @property
    def por_mes(self):
        return list(self._por_mes)

    @por_mes.setter
    def por_mes(self, valor):
        self._por_mes.append(valor)

    @property
    def roa(self):
        return self._roa

    @roa.setter
    def roa(self, valor):
        self._roa = valor

    @property
    def capitalizacao(self):
        return self._capitalizacao

    @capitalizacao.setter
    def capitalizacao(self, valor):
        self._capitalizacao.append(valor)



class infoPorProduto:
    def __init__(self, nome, pdc, pdv, data, qtd):
        self.nome = nome
        self.preco_custo = pdc
        self.preco_venda = pdv
        self.data = data
        self.qtd = qtd

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        self._nome = valor


def to_number(valor):
    return float(valor.split('R$ ')[1].replace('.', '').replace(',', '.'))


def valorizar(valor, mes):
    v = reduce(lambda x, y: x*y, infoLoja.capitalizacao[mes:])
    # print(v)
    return valor * v


def capitalizar(valor):
    return valor * infoLoja.capitalizacao[-1]


despesas = pd.read_csv('despesas.csv', sep=";", encoding='latin-1').dropna()
despesas['Período'] = pd.to_datetime(despesas['Período'], dayfirst=True)
despesas['Saiu'] = despesas['Saiu'].apply(to_number)
despesas['Entrou'] = despesas['Entrou'].apply(to_number)

vendas = pd.read_csv('vendas_loja.csv', sep=";", encoding='utf-8').dropna()
vendas['Pdc'] = vendas['Pdc'].apply(to_number)
vendas['Meu retorno'] = vendas['Meu retorno'].apply(to_number)
vendas['Lucro'] = vendas['Lucro'].apply(to_number)
vendas['Data'] = pd.to_datetime(vendas['Data'], dayfirst=True)


infoLoja = loja()
infoLoja.meses = set(vendas['Data'].dt.month)
infoLoja.margemLiquida = vendas['Lucro'].sum()/vendas['Meu retorno'].sum()
infoLoja.caixa = vendas['Meu retorno'].sum() - despesas['Saiu'].sum()
infoLoja.estoque = despesas[despesas['Ativo'] == 'Sim']['Saiu'].sum() - vendas['Meu retorno'].sum()
infoLoja.roa = vendas['Lucro'].sum()/despesas[despesas['Ativo'] == 'Sim']['Saiu'].sum()
# print(infoLoja.roa)

for mes in infoLoja.meses:
    analiseMensal = lojaMes()
    analiseMensal.margemLiquida = vendas[vendas['Data'].dt.month == mes]['Lucro'].sum()/vendas[vendas['Data'].dt.month == mes]['Meu retorno'].sum()
    analiseMensal.caixa = vendas[vendas['Data'].dt.month <= mes]['Meu retorno'].sum() - despesas[despesas['Período'].dt.month <= mes]['Saiu'].sum()
    analiseMensal.estoque = despesas[(despesas['Ativo'] == 'Sim') & (despesas['Período'].dt.month <= mes)]['Saiu'].sum() - vendas[vendas['Data'].dt.month <= mes]['Meu retorno'].sum()
    analiseMensal.roa = vendas[vendas['Data'].dt.month == mes]['Lucro'].sum()/(despesas[(despesas['Ativo'] == 'Sim') & (despesas['Período'].dt.month <= mes)]['Saiu'].sum() - vendas[vendas['Data'].dt.month < mes]['Meu retorno'].sum())
    analiseMensal.entrou_do_mes_passado = despesas[(despesas['Ativo'] == 'Sim') & (despesas['Período'].dt.month <= mes)]['Saiu'].sum() - vendas[vendas['Data'].dt.month < mes]['Meu retorno'].sum()
    infoLoja.por_mes = analiseMensal
# print(vendas[(vendas['Data'].dt.month >= 1) & (vendas['Data'].dt.month <= 2)].groupby(['Produto']).head())
# print(despesas[despesas['Período'].dt.month == 1])

for infoMes in infoLoja.por_mes:
    infoLoja.capitalizacao = (infoMes.roa + 1)

    # print((infoMes.entrou_do_mes_passado * (infoMes.roa + 1)) - infoMes.entrou_do_mes_passado)
# print(reduce(lambda x, y: x*y, infoLoja.capitalizacao[1:]))
mes = 3
x = vendas[(vendas['Data'].dt.month == mes)].groupby(['Produto'])['Lucro'].sum().apply(valorizar, args=(mes-1,)) - vendas[(vendas['Data'].dt.month == mes)].groupby(['Produto'])['Lucro'].sum()
print(x)
print(vendas[(vendas['Data'].dt.month == mes)].groupby(['Produto'])['Lucro'].sum())
print(infoLoja.capitalizacao)
# print(vendas.groupby([vendas['Data'].dt.month]).sum())
# print(vendas[(vendas['Data'].dt.month == mes)].groupby(['Produto'])['Meu retorno'].sum())
# print(x.apply(capitalizar) + vendas[(vendas['Data'].dt.month == mes)].groupby(['Produto'])['Meu retorno'].sum().apply(capitalizar))

#349 / 868 = 1217
#113 / 773 =
# 868 / 1217
# 777 / 1085
# 1645 / 2302