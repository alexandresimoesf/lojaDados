from datetime import date
from functools import reduce
import calendar

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
# print(despesas)

vendas = pd.read_csv('vendas_loja.csv', sep=";", encoding='utf-8').dropna()
vendas['Pdc'] = vendas['Pdc'].apply(to_number)
vendas['Pdc'] = vendas['Pdc'] * vendas['Qtd']
vendas['Meu retorno'] = vendas['Meu retorno'].apply(to_number)
vendas['Lucro'] = vendas['Meu retorno'] - (vendas['Pdc'])
vendas['Data'] = pd.to_datetime(vendas['Data'], dayfirst=True)
vendas = vendas.drop(columns='Index')


infoLoja = loja()
infoLoja.meses = set(vendas['Data'].dt.month)
infoLoja.margemLiquida = vendas['Lucro'].sum()/vendas['Meu retorno'].sum()
infoLoja.caixa = vendas['Meu retorno'].sum() - despesas['Saiu'].sum()
infoLoja.estoque = despesas[despesas['Ativo'] == 'Sim']['Saiu'].sum() - vendas['Pdc'].sum()
infoLoja.roa = vendas['Lucro'].sum()/despesas[despesas['Ativo'] == 'Sim']['Saiu'].sum()
infoLoja.passivo = despesas[despesas['Pago'] == 'Não']['Saiu'].sum()

infoLoja.venda_info_mensal = vendas.groupby([vendas['Data'].dt.month]).sum().reset_index()
infoLoja.venda_info_mensal['Margem Liquida'] = infoLoja.venda_info_mensal['Lucro']/infoLoja.venda_info_mensal['Meu retorno']
despesas_mensal = despesas.groupby(despesas['Período'].dt.month).sum().reset_index()
despesas_mensal['Cumsum'] = despesas_mensal['Saiu'].cumsum()
infoLoja.venda_info_mensal['Obrigações'] = despesas_mensal['Saiu']
infoLoja.venda_info_mensal['Caixa'] = infoLoja.venda_info_mensal['Meu retorno'].cumsum() - despesas_mensal['Cumsum']
infoLoja.venda_info_mensal['Ativos'] = despesas_mensal['Cumsum'] - infoLoja.venda_info_mensal['Pdc'].cumsum()
infoLoja.venda_info_mensal['Roa'] = infoLoja.venda_info_mensal['Lucro'] / infoLoja.venda_info_mensal['Ativos']
infoLoja.venda_info_mensal['Ticket médio'] = infoLoja.venda_info_mensal['Meu retorno']/infoLoja.venda_info_mensal['Qtd']
print(infoLoja.venda_info_mensal)

venda_produto = vendas.groupby(['Produto', vendas['Data'].dt.month]).sum().reset_index()
venda_produto['Margem Líquida'] = venda_produto['Lucro'] / venda_produto['Meu retorno'] * 100
venda_produto['Data'] = venda_produto['Data'].apply(lambda x: calendar.month_name[x])
venda_produto = venda_produto.groupby(['Data', 'Produto']).sum()
# print(venda_produto)