from datetime import date
import matplotlib.pyplot as plt
from functools import reduce
import numpy as np
import calendar
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
from pandas import set_option

set_option('display.max_rows', 500)
set_option('display.max_columns', 500)
set_option('display.width', 2000)


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
    def roi(self):
        return self._roi

    @roi.setter
    def roi(self, valor):
        self._roi = valor

    @property
    def roic(self):
        return self._roic

    @roic.setter
    def roic(self, valor):
        self._roic = valor

    @property
    def passivo(self):
        return self._passivo

    @passivo.setter
    def passivo(self, valor):
        self._passivo = valor

    @property
    def venda_info_mensal(self):
        return self._venda_info_mensal

    @venda_info_mensal.setter
    def venda_info_mensal(self, valor):
        self._venda_info_mensal = valor

    @property
    def capitalizacao(self):
        return self._capitalizacao

    @capitalizacao.setter
    def capitalizacao(self, valor):
        self._capitalizacao.append(valor)


def to_number(valor):
    return float(valor.split('R$ ')[1].replace('.', '').replace(',', '.'))


def valorizar(valor, mes):
    v = reduce(lambda x, y: x*y, infoLoja.capitalizacao[mes:])
    return valor * v


def capitalizar(valor):
    return valor * infoLoja.capitalizacao[-1]


month = date.today().month
despesas = pd.read_csv('despesas.csv', sep=";", encoding='latin-1').dropna()
despesas['Período'] = pd.to_datetime(despesas['Período'], dayfirst=True)
despesas['Saiu'] = despesas['Saiu'].apply(to_number)

vendas = pd.read_csv('vendas_loja.csv', sep=";", encoding='utf-8').dropna()
vendas['Pdc'] = vendas['Pdc'].apply(to_number)
vendas['Pdc'] = vendas['Pdc'] * vendas['Qtd']
vendas['Receita'] = vendas['Receita'].apply(to_number)
vendas['Lucro'] = (vendas['Receita'] - vendas['Pdc'])
vendas['Data'] = pd.to_datetime(vendas['Data'], dayfirst=True)
vendas = vendas.drop(columns='Index')
vendas = vendas[vendas['Produto'].astype(str).str.startswith('Calça')]
# print(vendas.dtypes)

compras = pd.read_csv('compras.csv', sep=";", encoding='latin-1').dropna()
compras['Data'] = pd.to_datetime(compras['Data'], dayfirst=True)


infoLoja = loja()
infoLoja.meses = set(vendas['Data'].dt.month)
infoLoja.margemLiquida = (vendas['Lucro'].sum()/vendas['Receita'].sum()) + .034
infoLoja.caixa = vendas['Receita'].sum() - despesas[despesas['Pago'] == 'Sim']['Saiu'].sum()
infoLoja.estoque = (despesas[(despesas['Ativo'] == 'Sim') & (despesas['Pago'] == 'Sim')]['Saiu'].sum()) - ((vendas['Lucro'].sum()/infoLoja.margemLiquida) - (vendas['Lucro'].sum()))
despesa_ativo_pago = despesas[(despesas['Ativo'] == 'Sim') & (despesas['Pago'] == 'Sim') & (despesas['Prazo'] == 'Não')]['Saiu'].sum()
despesa_ativo_total = despesas[despesas['Ativo'] == 'Sim']['Saiu'].sum() - ((vendas['Lucro'].sum()/infoLoja.margemLiquida) - (vendas['Lucro'].sum()))
infoLoja.roa = vendas['Lucro'].sum()/despesas[(despesas['Ativo'] == 'Sim') & (despesas['Pago'] == 'Sim') & (despesas['Prazo'] == 'Não')]['Saiu'].sum()
# infoLoja.roi = (vendas['Receita'].sum() - despesa_ativo_pago)/despesa_ativo_pago
infoLoja.passivo = despesas[(despesas['Ativo'] == 'Sim') & (despesas['Prazo'] == 'Sim')]['Saiu'].sum()
infoLoja.roic = vendas['Lucro'].sum()/(despesa_ativo_pago + infoLoja.passivo + -infoLoja.caixa if infoLoja.caixa < 0 else 0)
roe = vendas['Lucro'].sum()/(despesa_ativo_pago - infoLoja.passivo + -infoLoja.caixa if infoLoja.caixa < 0 else 0)
# print(infoLoja.margemLiquida)
# print(infoLoja.estoque)
print(infoLoja.caixa)
print(infoLoja.roa)
# print(infoLoja.roic)
# print(roe)
# print(((1 + infoLoja.roic) * infoLoja.passivo) - infoLoja.passivo)


infoLoja.venda_info_mensal = vendas.groupby([vendas['Data'].dt.month]).sum().reset_index()
# infoLoja.venda_info_mensal['Data'] = infoLoja.venda_info_mensal['Data'].apply(lambda x: calendar.month_name[x])
infoLoja.venda_info_mensal['Margem Liquida'] = infoLoja.venda_info_mensal['Lucro']/infoLoja.venda_info_mensal['Receita']
despesas_mensal_ativo_passivo = despesas[despesas['Pago'] == 'Sim'].groupby(despesas['Período'].dt.month).sum().reset_index()
despesas_mensal = despesas[(despesas['Pago'] == 'Sim') & (despesas['Ativo'] == 'Sim')].groupby(despesas['Período'].dt.month).sum().reset_index()
infoLoja.venda_info_mensal['Obrigações'] = despesas_mensal_ativo_passivo['Saiu']
infoLoja.venda_info_mensal['Caixa'] = infoLoja.venda_info_mensal['Receita'] - despesas_mensal_ativo_passivo['Saiu']
# infoLoja.venda_info_mensal['Novo investimento'] = despesas.groupby([despesas['Período'].dt.month])['Novo investimento'].sum()
infoLoja.venda_info_mensal['Ticket médio'] = infoLoja.venda_info_mensal['Receita']/infoLoja.venda_info_mensal['Qtd']
# print(infoLoja.venda_info_mensal)


venda_produto_geral = vendas.groupby([vendas['Data'].dt.month]).sum()
# venda_produto_geral = venda_produto_geral[venda_produto_geral['week'] >= (22 - 4)].groupby('Produto').mean()
# print(venda_produto_geral)
# print(set(venda_produto_geral['Produto']))
# print(set(venda_produto_geral['Produto']) - set(compras['Produto'])) # Não vendeu nas ultimas 4 semanas
# print(set(compras['Produto']) - set(vendas['Produto'])) # Nunca vendeu


N = 7
venda_produto_semanal = vendas.groupby([vendas['Data'].dt.isocalendar().week]).sum() #.drop(columns={'Pdc'})
# venda_produto_semanal = vendas.groupby([vendas['Data']]).sum()
venda_produto_semanal['Média móvel qtd'] = venda_produto_semanal['Qtd'].rolling(N).sum()
venda_produto_semanal['Média móvel receita'] = venda_produto_semanal['Receita'].rolling(N).sum()
venda_produto_semanal['Média móvel lucro'] = venda_produto_semanal['Lucro'].rolling(N).sum()
hist = venda_produto_semanal.sort_values(by='week').reset_index()
# print(hist.describe())
# plt.plot(hist['week'], hist['Média móvel qtd'])
# plt.show()
# print(venda_produto_semanal.sort_values(by='Data'))