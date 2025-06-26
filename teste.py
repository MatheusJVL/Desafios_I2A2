import pandas as pd


base_climatica = pd.read_csv('base_climatica.csv')
base_socioeconomica = pd.read_csv('base_socioeconomica.csv')

#vejo as linhas duplicadas de cada base e as removo
##print(base_climatica.duplicated().sum())
#print(base_socioeconomica.duplicated().sum())
base_climatica = base_climatica.drop_duplicates()
base_socioeconomica = base_socioeconomica.drop_duplicates()

#print(base_climatica.describe())  # vejo os possiveis outliers da base climatica e os suavizo pela mediana da coluna

mediana_chuvas_previstas = base_climatica['chuvas_previstas_mm'].median()
base_climatica['chuvas_previstas_mm'] = base_climatica['chuvas_previstas_mm'].apply(lambda x: mediana_chuvas_previstas if x < 5 else x)

mediana_chuvas_reais = base_climatica['chuvas_reais_mm'].median()
base_climatica['chuvas_reais_mm'] = base_climatica['chuvas_reais_mm'].apply(lambda x: mediana_chuvas_reais if x > 400 or x < 5 else x)

mediana_temperatura = base_climatica['temperatura_media_C'].median()
base_climatica['temperatura_media_C'] = base_climatica['temperatura_media_C'].apply(lambda x: mediana_temperatura if x > 40 or x < 15 else x)

mediana_indice_umidade_solo = base_climatica['indice_umidade_solo'].median()
base_climatica['indice_umidade_solo'] = base_climatica['indice_umidade_solo'].apply(lambda x: mediana_indice_umidade_solo if x > 100 or x < 5 else x)

#print(base_climatica.describe())



#print(base_socioeconomica.describe())  vejo os possiveis outliers da base socioeconomica e os suavizo pela mediana da coluna                                                                                                                                                                         
mediana_producao_tons = base_socioeconomica['volume_producao_tons'].median()
base_socioeconomica['volume_producao_tons'] = base_socioeconomica['volume_producao_tons'].apply(lambda x: mediana_producao_tons if x > 50 or x < 5 else x)

mediana_incidencia_doencas = base_socioeconomica['incidencia_doencas'].median()
base_socioeconomica['incidencia_doencas'] = base_socioeconomica['incidencia_doencas'].apply(lambda x: mediana_incidencia_doencas if x > 6 else x)

#print(base_socioeconomica.describe())



#print(base_climatica.isnull().sum()) #vejo as colunas com dados nulos na base climatica e os troco pela média da coluna

base_climatica_cols_com_nulos = ["chuvas_reais_mm", "temperatura_media_C","indice_umidade_solo"]

for col in base_climatica_cols_com_nulos:
    base_climatica[col] = base_climatica[col].fillna(base_climatica[col].mean())

#print(base_climatica.isnull().sum()) 



#print(base_socioeconomica.isnull().sum()) #vejo as colunas com dados nulos na base socioeconomica e os troco pela média da coluna

base_socioeconomica_cols_com_nulos = ["volume_producao_tons", "incidencia_doencas"]

for col in base_socioeconomica_cols_com_nulos:
    base_socioeconomica[col] = base_socioeconomica[col].fillna(base_socioeconomica[col].mean())

#print(base_socioeconomica.isnull().sum())



#vejo as colunas que contenham respostas de sim ou não e as padronizo para sim ou nao
#print(base_climatica['variacao_climatica'].unique())
#print(base_socioeconomica['acesso_agua_potavel'].unique())

base_climatica['variacao_climatica'] = base_climatica['variacao_climatica'].str.lower().str.strip().apply(lambda x: 'nao' if x.startswith('n') else ('sim' if x.startswith('s') else pd.NA))

base_socioeconomica['acesso_agua_potavel'] = base_socioeconomica['acesso_agua_potavel'].str.lower().str.strip().apply(lambda x: 'nao' if x.startswith('n') else ('sim' if x.startswith('s') else pd.NA))

#print(base_climatica['variacao_climatica'].unique())
#print(base_socioeconomica['acesso_agua_potavel'].unique())



# convertendo a coluna data de ambas as bases que são do tipo object para datetime

for df in (base_climatica, base_socioeconomica):
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d', errors='coerce')

#print(base_climatica.dtypes)
#print(base_socioeco


base_completa = pd.merge(base_climatica, base_socioeconomica, on='data', how='inner', suffixes=('_climatica', '_socio'))

# ordenando a base completa pela coluna data e resetando o índice
base_completa = base_completa.sort_values('data').reset_index(drop=True)

#print(base_completa.dtypes)
# salvando a base completa em um novo arquivo CSV
#base_completa.to_csv('base_completa.csv', index=False)
#print(base_completa.shape)


#  plotando os graficos de chuvas reais e previstas ao longo do tempo

import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(12, 6))
sns.lineplot(data=base_completa, x='data', y='chuvas_reais_mm', label='Chuvas Reais (mm)', color='blue')
sns.lineplot(data=base_completa, x='data', y='chuvas_previstas_mm', label='Chuvas Previstas (mm)', color='orange')
plt.title('Chuvas Reais vs Previstas ao Longo do Tempo')
plt.xlabel('Data')
plt.ylabel('Milímetros')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig('chuvas_reais_vs_previstas.png')
plt.show()

#  plotando o grafico de temperatura_media_C vs. indice_umidade_solo

plt.figure(figsize=(8, 6))
sns.regplot(data=base_completa, x="temperatura_media_C", y="indice_umidade_solo", scatter_kws={'alpha':0.6})
plt.title("Temperatura vs. Umidade do Solo")
plt.xlabel("Temperatura Média (°C)")
plt.ylabel("Índice de Umidade do Solo")
plt.tight_layout()
plt.show()

# plotando o grafico de indice_umidade_solo vs volume_producao_tons

base_umidade = base_completa.copy()
base_umidade['faixa_umidade'] = pd.qcut(base_umidade['indice_umidade_solo'], q=4, labels=["Baixa", "Média-Baixa", "Média-Alta", "Alta"])
media_producao_por_umidade = base_umidade.groupby('faixa_umidade')['volume_producao_tons'].mean().reset_index()

plt.figure(figsize=(8, 6))
sns.barplot(data=media_producao_por_umidade, x='faixa_umidade', y='volume_producao_tons')
plt.title("Produção Média por Faixa de Umidade do Solo")
plt.xlabel("Faixa de Umidade")
plt.ylabel("Produção Média (tons)")
plt.tight_layout()
plt.show()


base_temperatura = base_completa.copy()
base_temperatura['faixa_temperatura'] = pd.qcut(base_temperatura['temperatura_media_C'], q=4, labels=["Frio", "Ameno", "Quente", "Muito Quente"])

plt.figure(figsize=(8, 6))
sns.boxplot(data=base_temperatura, x='faixa_temperatura', y='incidencia_doencas')
plt.title("Incidência de Doenças por Faixa de Temperatura")
plt.xlabel("Faixa de Temperatura")
plt.ylabel("Incidência de Doenças")
plt.tight_layout()
plt.show()

base_seg = base_completa.copy()
seg_col = 'indicador_seguranca_alimentar'
base_seg[seg_col] = base_seg[seg_col].astype(str)  # Garantir que é categórico

plt.figure(figsize=(8, 6))
sns.violinplot(data=base_seg, x=seg_col, y='volume_producao_tons', inner="box")
plt.title("Produção por Níveis de Segurança Alimentar")
plt.xlabel("Indicador de Segurança Alimentar")
plt.ylabel("Produção (tons)")
plt.tight_layout()
plt.show()




# Calcular a matriz de correlação entre variáveis numéricas
numericas = ['chuvas_previstas_mm', 'chuvas_reais_mm', 'temperatura_media_C',
             'indice_umidade_solo', 'volume_producao_tons', 
             'incidencia_doencas', 'indicador_seguranca_alimentar']
correlacao = base_completa[numericas].corr()

# Criar heatmap de correlação
plt.figure(figsize=(10, 8))
sns.heatmap(correlacao, annot=True, cmap='coolwarm', fmt=".2f", square=True)
plt.title("Mapa de Calor das Correlações")
plt.tight_layout()
plt.show()