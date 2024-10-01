import tkinter as tk
import requests
from PIL import Image, ImageTk
from io import BytesIO
import pandas as pd
from collections import defaultdict
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score
import numpy as np
'''
- Fazer Tela de espera do treinamento v
- Fazer Tela de listagem de recomendados e não recomendados
'''
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Recomendação")
        self.geometry("400x350")
        self.url_detalhado = f'https://www.freetogame.com/api/game'
        self.url_geral = 'https://www.freetogame.com/api/games'
        options = Options()
        options.add_argument('--headless') 
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        response = requests.get(self.url_geral)
        dados = response.json()
        self.dados = dados.copy()
        self.modelo_svm = None
        self.predicoes = []
        self.accuracia = 0
        self.criado = False
        self.lista_thumbs = ['https://www.freetogame.com/g/582/thumbnail.jpg']
    # Dicionário para armazenar as telas
        self.frames = {}

        # Criar as telas
        for F in (TelaUsuario,TelaRecomendado):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Mostrar a tela inicial
        self.show_frame("TelaUsuario")

    def show_frame(self, page_name):
        '''Mostra a tela especificada pelo nome'''
        frame = self.frames[page_name]
        frame.tkraise()  # Traz o frame para a frente


class TelaRecomendado(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        # Inicializar o índice para o carrossel
        self.thumb_index = 0

        # Label para mostrar a imagem
        self.img_label = tk.Label(self)
        self.img_label.pack()

        # Botões de navegação
        btn_prev = tk.Button(self, text="Anterior", command=self.mostrar_anterior)
        btn_prev.pack(side="left", padx=20)
        btn_next = tk.Button(self, text="Próximo", command=self.mostrar_proximo)
        btn_next.pack(side="right", padx=20)

        # Mostrar a primeira imagem
        self.mostrar_imagem()

    def mostrar_imagem(self):
        # Pegar o link do thumbnail atual
        url = self.parent.lista_thumbs[self.thumb_index]

        # Fazer a requisição da imagem
        response = requests.get(url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))


        # Atualizar a imagem do Label
        self.img_tk = ImageTk.PhotoImage(img)
        self.img_label.config(image=self.img_tk)

    def mostrar_anterior(self):
        # Vai para a imagem anterior no carrossel
        if self.thumb_index > 0:
            self.thumb_index -= 1
        else:
            self.thumb_index = len(self.parent.lista_thumbs) - 1  # Volta ao último item
        self.mostrar_imagem()

    def mostrar_proximo(self):
        # Vai para a próxima imagem no carrossel
        if self.thumb_index < len(self.parent.lista_thumbs) - 1:
            self.thumb_index += 1
        else:
            self.thumb_index = 0  # Volta ao primeiro item
        self.mostrar_imagem()

            
        

class TelaUsuario(tk.Frame):
    def __init__(self, parent, controller) -> None:
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.cont = 0
        self.dado_atual = None
        self.tamanho_total = len(self.parent.dados)
        self.image = self.pegar_imagem(self.cont)
        self.dicionario_curtiu = defaultdict(list)
        self.like = False
        self.dislike = False
        self.photo = ImageTk.PhotoImage(self.image)
        

        # Crie um rótulo (label)
        self.label = tk.Label(self, image=self.photo)
        self.label.pack(pady=20)

        like_frame = tk.Frame(self)
        like_frame.pack(pady=10) 


        curtir = tk.Button(like_frame, text="Curtir", command=self.on_curtir)
        curtir.pack(side=tk.LEFT, padx=5)  

        nao_curtir = tk.Button(like_frame, text="Não Curtir", command=self.on_nao_curtir)
        nao_curtir.pack(side=tk.LEFT, padx=5) 

        csv = tk.Button(like_frame, text="Recomendar", command=self.on_to_pandas_csv)
        csv.pack(side=tk.LEFT, padx=5) 

        
    
    def pegar_imagem(self, cont):
        game_renderizado = self.parent.dados[cont]
        url_image = game_renderizado['thumbnail']
        response = requests.get(url_image)
        img_data = response.content
        return Image.open(BytesIO(img_data))




    def atualizar_imagem(self):
        self.photo = ImageTk.PhotoImage(self.image)
        self.label.config(image=self.photo)  # Atualiza a imagem do label

    def on_curtir(self):
        self.dado_atual = self.parent.dados[self.cont].copy()
        print(self.parent.url_detalhado + f'?id={self.dado_atual["id"]}')
        response_detalhados = requests.get(self.parent.url_detalhado + f'?id={self.dado_atual["id"]}')
        dados_detalhados = response_detalhados.json()
        self.dicionario_curtiu['title'].append(dados_detalhados['title'])
        self.dicionario_curtiu['status'].append( 1 if dados_detalhados['status'] == 'Live' else 0)
        self.dicionario_curtiu['genre'].append(dados_detalhados['genre'])
        self.dicionario_curtiu['platform'].append(dados_detalhados['platform'])
        self.dicionario_curtiu['publisher'].append(dados_detalhados['publisher'])

        data = datetime.strptime(dados_detalhados['release_date'], "%Y-%m-%d")
        ano_data = data.year
        ano_atual = datetime.now().year
        diferenca = ano_atual - ano_data
        self.dicionario_curtiu['age'].append(diferenca)
        url = dados_detalhados['freetogame_profile_url']
        self.parent.driver.get(url)
        div = self.parent.driver.find_element(By.CLASS_NAME, 'pcc-percents-wrapper')
        percent = div.find_element(By.TAG_NAME, 'span').text
        percent = percent.replace('%', '')
        self.dicionario_curtiu['review'].append(int(percent))
        print(f'O valor extraído é: {percent}')
        self.dicionario_curtiu['like'].append(1)
        self.like = True
        self.cont += 1
        if self.cont >= self.tamanho_total:
            self.cont = 0
        self.image = self.pegar_imagem(self.cont)
        self.atualizar_imagem()
            


    def on_nao_curtir(self):
        self.dado_atual = self.parent.dados[self.cont].copy()
        response_detalhados = requests.get(self.parent.url_detalhado + f'?id={self.dado_atual["id"]}')
        dados_detalhados = response_detalhados.json()
        self.dicionario_curtiu['title'].append(dados_detalhados['title'])
        self.dicionario_curtiu['status'].append( 1 if dados_detalhados['status'] == 'Live' else 0)
        self.dicionario_curtiu['genre'].append(dados_detalhados['genre'])
        self.dicionario_curtiu['platform'].append(dados_detalhados['platform'])
        self.dicionario_curtiu['publisher'].append(dados_detalhados['publisher'])

        data = datetime.strptime(dados_detalhados['release_date'], "%Y-%m-%d")
        ano_data = data.year
        ano_atual = datetime.now().year
        diferenca = ano_atual - ano_data
        self.dicionario_curtiu['age'].append(diferenca)
        url = dados_detalhados['freetogame_profile_url']
        self.parent.driver.get(url)
        div = self.parent.driver.find_element(By.CLASS_NAME, 'pcc-percents-wrapper')
        percent = div.find_element(By.TAG_NAME, 'span').text
        percent = percent.replace('%', '')
        self.dicionario_curtiu['review'].append(int(percent))
        print(f'O valor extraído é: {percent}')
        self.dicionario_curtiu['like'].append(0)
        self.dislike = True
        self.cont += 1
        if self.cont >= self.tamanho_total:
            self.cont = 0
        self.image = self.pegar_imagem(self.cont)
        self.atualizar_imagem()

    def on_to_pandas_csv(self):
        df = pd.DataFrame(self.dicionario_curtiu)
        df.to_csv('treino.csv', index=False)
        self.treino()

    def treino(self):
            print('comecou')
            df = pd.read_csv('treino.csv')
            X = df.drop(['like'], axis=1)  
            y = df['like']  

            titles = X['title']
            # Aplicar One-Hot Encoding nas colunas categóricas (genre, platform, publisher)
            encoder = OneHotEncoder(sparse_output=False)  # Usar sparse_output=False
            X_encoded = encoder.fit_transform(X[['genre', 'platform', 'publisher']])

            # Transformar X_encoded em DataFrame para combinar com colunas numéricas
            encoded_columns = encoder.get_feature_names_out(['genre', 'platform', 'publisher'])
            X_encoded_df = pd.DataFrame(X_encoded, columns=encoded_columns, index=X.index)

            # Concatenar as variáveis categóricas codificadas com as variáveis numéricas (status, age, review)
            X_numeric = X[['status', 'age', 'review']]
            X_final = pd.concat([X_numeric, X_encoded_df], axis=1)
            print(X_final.head())
            # Dividir os dados em treino (70%) e teste (30%)
            X_train, X_test, y_train, y_test, titles_train, titles_test = train_test_split(X_final, y, titles, test_size=0.3, random_state=42)

            # Criar e treinar o modelo SVM
            self.parent.modelo_svm = SVC(kernel='poly')
            self.parent.modelo_svm.fit(X_train, y_train)
            print('treino terminado')
            # Fazer previsões nos dados de teste
            y_pred = self.parent.modelo_svm.predict(X_test)
            self.acuracia = accuracy_score(y_test, y_pred)
            print(f'acuracia: {self.acuracia=}')
            self.parent.predicoes = [{'nome': title, 'predicao_curte': pred} for title, pred in zip(titles_test, y_pred)]
            print(self.parent.predicoes)
            self.parent.lista_thumbs = self.procurar_ids()
            self.controller.show_frame('TelaRecomendado')


    def procurar_ids(self):
        lista_thumbs = []
        for pred in self.parent.predicoes:
            if pred['predicao_curte'] == 1:
                procura = filter(lambda x: x['title'] == pred['nome'], self.parent.dados)
                thumb = next(procura)['thumbnail']  # Obtém o link thumbnail
                lista_thumbs.append(thumb)
        return lista_thumbs
        

       
        
   
    

if __name__ == '__main__':
    tela = App()
    tela.mainloop()