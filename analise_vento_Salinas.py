# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 17:32:12 2017
ANALISE DOS DADOS DE VENTO
@author: aline
"""
import pandas as pd
import numpy as np
import wx
from pandas import Series, DataFrame, Panel
#import datetime
import matplotlib.pyplot as plt
from windrose import WindroseAxes
import matplotlib as mpl
#import os
from matplotlib import colors as mcolors
from collections import OrderedDict
import seaborn as sns


# A quick way to create new windrose axes #,radialaxis='%'
def new_axes():
    fig = plt.figure(figsize=(13, 8), dpi=80, facecolor='w', edgecolor='w')
    rect = [0.1, 0.1, 0.8, 0.8]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)
    return ax


# ...and adjust the legend box
def set_legend(ax):
    l = ax.legend(borderaxespad=-0.10, bbox_to_anchor=[-0.1, 0.5],
                  loc='centerleft', title="m/s")
    plt.setp(l.get_texts(), fontsize=20)


# Para selecionar o arquivo de analise
def get_path(wildcard):
    app = wx.App(None)
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    dialog = wx.FileDialog(None, 'Open', wildcard=wildcard, style=style)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
        direc = dialog.GetDirectory()
        # f = dialog.GetFilename()
    else:
        path = None
    dialog.Destroy()
    return path, direc

label_size = 18
fontsize = 16
meses_label = OrderedDict([('Jan', 1), ('Fev', 2), ('Mar', 3),
                           ('Abr', 4), ('Mai', 5), ('Jun', 6),
                           ('Jul', 7), ('Ago', 8), ('Set', 9),
                           ('Out', 10), ('Nov', 11), ('Dez', 12)])

cores = sns.color_palette(palette="viridis", n_colors=15)

"*************************************************************"
"*                                                           *"
"*                 LEITURA DO ARQUIVO                        *"
"*                                                           *"
"*************************************************************"
# escolhendo o arquivo de entrada
print('ESCOLHA O ARQUIVO DE VENTO REESCRITO DO INMET')
filename, pathname = get_path('*')

"Lendo arquivo do INMET"
# Juntando data em uma unica coluna
# Detalhe que o dataparse precisa do padrão %Y %m %d separado por espacos
# indicando que cada variavel esta em uma coluna diferente
dateparse = lambda x: pd.datetime.strptime(x, '%Y %m %d %H')
dados = pd.read_csv(filename, sep=';',
                    header=0, 
                    na_values='NaN',
                    parse_dates={'datahora': ['Ano', 'Mes', 'Dia',
                                             'Hora']},
                    date_parser=dateparse, 
                    squeeze=True, 
                    index_col=0)

"*************************************************************"
"*                                                           *"
"*                 SERIE COMPLETA VENTO                      *"
"*                                                           *"
"*************************************************************"

#if grafico == 1:
mpl.rcParams['xtick.labelsize'] = label_size
mpl.rcParams['ytick.labelsize'] = label_size
mpl.rcParams['font.size'] = label_size

fig, ax = plt.subplots(figsize=[13, 6])    

serie1 = plt.plot(dados.Velvento, label='Intensidade', color=cores[1])
plt.ylabel(u'Velocidade do vento (m/s)')
plt.xlabel('Dia')
plt.legend()
ax2 = ax.twinx()
ax2.plot(dados.Ventodir, color=cores[7], label=u'Direção')
ax2.set_ylabel(u'Direção do vento (graus)')
ax2.tick_params('y')
#plt.title('Distribuicao de chuva ao longo do dia')
# mpl.rc('font', **font)

"*************************************************************"
"*                                                           *"
"*                 ANALISE VENTO                             *"
"*                 MEDIAS MENSAIS                            *"
"*                                                           *"
"*************************************************************"
media_vento_mensal = dados.groupby(dados.index.month).mean()
std_vento_mensal = dados.groupby(dados.index.month).std()
quantil10_vento = dados.groupby(dados.index.month).quantile(q=0.10)
quantil25_vento = dados.groupby(dados.index.month).quantile(q=0.25)
quantil75_vento = dados.groupby(dados.index.month).quantile(q=0.75)
quantil90_vento = dados.groupby(dados.index.month).quantile(q=0.90)

"Plotando figuras"
plt.plot(media_vento_mensal.Velvento, color= cores[14], alpha=0.8)
plt.fill_between(x=media_vento_mensal.index, y1=quantil10_vento.Velvento,
                 y2=quantil90_vento.Velvento, interpolate=True,
                 color=cores[13], linestyle='--', alpha=0.3) #'#b1c4dd', 
plt.fill_between(x=media_vento_mensal.index, y1=quantil25_vento.Velvento,
                 y2=quantil75_vento.Velvento, interpolate=True,
                 color=cores[12], linestyle='--', alpha=0.6) #'#95b5df'
plt.title(u'Número médio de dias de chuva por mês')
plt.xlabel(u'Mês')
plt.xticks(index)
plt.ylabel('Dias de chuva')
plt.ylim([0,31])
plt.xlim([1,12])
plt.savefig(pathname + '\media_dias_chuva.png', format='png', dpi=1200)

plt.figure(figsize=[13, 7])
plt.errorbar(index, media_chuva_mensal, yerr=std_chuva_mensal, fmt='ok',
             label=u'Desvio Padrão')
plt.plot(ano2016_inmet, '--*', label='Media Mensal: 2016',
             color=sns.set_palette("PuBuGn_d", 2))
rects1 = plt.bar(index, media_chuva_mensal, bar_width, alpha=opacity,
                 label='Chuva Mensal Media: 1977 - 2016',
                 color=sns.color_palette("PuBuGn_d", 3))
plt.legend()
plt.ylabel('Chuva acumulada (mm)')
plt.xticks(index, meses_label.keys())
plt.ylim([0, 899])
plt.savefig(pathname + '\\compara_clima_2016.png', format='png', dpi=1200)


"*************************************************************"
"*                                                           *"
"*                 SEPARANDO DADOS                           *"
"*                   POR DIRECAO                             *"
"*                                                           *"
"*************************************************************"
N = dados[dados.Ventodir >= 22.5 and dados.Ventodir < 67.5]
"""
ROSA DOS VENTOS PARA TODA A SERIE

"""
if grafico == 1:
    mpl.rcParams['xtick.labelsize'] = label_size
    mpl.rcParams['ytick.labelsize'] = label_size
    ax = new_axes()
    ax.bar(dados.Ventodir, dados.Velvento, normed=True, opening=0.8,
           edgecolor='white')
    plt.title('Intensidade e direcao do vento - 2016')
    set_legend(ax)
    # plt.title('Vel - camada 1', y=1.08,fontsize=14,fontweight='bold')
    manager = plt.get_current_fig_manager()
    manager.resize(*manager.window.maxsize())
    plt.savefig(pathname + '\windrose_anual.png')



"""
ROSA DOS VENTOS PARA O PERIODO DE psec
"""
if grafico == 1:
    label_size = 14
    mpl.rcParams['xtick.labelsize'] = label_size
    mpl.rcParams['ytick.labelsize'] = label_size
    ax = new_axes()
    ax.bar(psec.vento_dir, psec.vento_vel, normed=True,
           opening=0.8, edgecolor='white')
    plt.title('Intensidade e direcao do vento - Seco')
    set_legend(ax)
    # plt.title('Vel - camada 1', y=1.08,fontsize=14,fontweight='bold')
    manager = plt.get_current_fig_manager()
    manager.resize(*manager.window.maxsize())
    plt.savefig(pathname + '\windrose_psec.png')


"""
ROSA DOS VENTOS PARA O PERIODO DE VERAO
"""
if grafico == 1:
    mpl.rcParams['xtick.labelsize'] = label_size
    mpl.rcParams['ytick.labelsize'] = label_size
    ax = new_axes()
    ax.bar(verao.vento_dir, verao.vento_vel, normed=True, opening=0.8,
           edgecolor='white')
    plt.title('Intensidade e direcao do vento - Chuvoso')
    set_legend(ax)
    # plt.title('Vel - camada 1', y=1.08,fontsize=14,fontweight='bold')
    manager = plt.get_current_fig_manager()
    manager.resize(*manager.window.maxsize())
    plt.savefig(pathname + '\windrose_verao.pdf', format='svg', dpi=1200)
    # set_legend(ax)
