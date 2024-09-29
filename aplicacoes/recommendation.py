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
class Tela:
    def __init__(self) -> None:
        self.url_detalhado = f'https://www.freetogame.com/api/game'
        self.url_geral = 'https://www.freetogame.com/api/games'
        options = Options()
        options.add_argument('--headless')  # Executar em modo headless
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        response = requests.get(self.url_geral)
        dados = response.json()
        self.dados = dados.copy()
        self.root = tk.Tk()
        self.root.title("Sistema de Recomendação")
        self.root.geometry("400x350")
        self.cont = 0
        self.dado_atual = None
        self.tamanho_total = len(self.dados)
        self.image = self.pegar_imagem(self.cont)
        self.photo = ImageTk.PhotoImage(self.image)
        self.label = tk.Label(self.root, image=self.photo)
        self.dicionario_curtiu = defaultdict(list)
        self.like = False
        self.dislike = False
        
        
        
    
    def pegar_imagem(self, cont):
        game_renderizado = self.dados[cont]
        url_image = game_renderizado['thumbnail']
        response = requests.get(url_image)
        img_data = response.content
        return Image.open(BytesIO(img_data))

    def on_button_antes(self):
        self.cont -= 1
        if self.cont < 0:
            self.cont = self.tamanho_total - 1
        self.image = self.pegar_imagem(self.cont)
        self.atualizar_imagem()
        self.dislike = False
        self.like = False

    def on_button_proximo(self):
        self.cont += 1
        if self.cont >= self.tamanho_total:
            self.cont = 0
        self.image = self.pegar_imagem(self.cont)
        self.atualizar_imagem()
        self.dislike = False
        self.like = False


    def atualizar_imagem(self):
        self.photo = ImageTk.PhotoImage(self.image)
        self.label.config(image=self.photo)  # Atualiza a imagem do label

    def on_curtir(self):
        if not self.like and not self.dislike:
            self.dado_atual = self.dados[self.cont].copy()
            print(self.url_detalhado + f'?id={self.dado_atual["id"]}')
            response_detalhados = requests.get(self.url_detalhado + f'?id={self.dado_atual["id"]}')
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
            self.driver.get(url)
            div = self.driver.find_element(By.CLASS_NAME, 'pcc-percents-wrapper')
            percent = div.find_element(By.TAG_NAME, 'span').text
            percent = percent.replace('%', '')
            self.dicionario_curtiu['review'].append(int(percent))
            print(f'O valor extraído é: {percent}')
            self.dicionario_curtiu['like'].append(1)
            self.like = True


    def on_nao_curtir(self):
        if not self.dislike and not self.like:
            self.dado_atual = self.dados[self.cont].copy()
            response_detalhados = requests.get(self.url_detalhado + f'?id={self.dado_atual["id"]}')
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
            # Configurar o Selenium
            

            # URL para a requisição
            url = dados_detalhados['freetogame_profile_url']
            self.driver.get(url)
            div = self.driver.find_element(By.CLASS_NAME, 'pcc-percents-wrapper')
            percent = div.find_element(By.TAG_NAME, 'span').text
            percent = percent.replace('%', '')
            self.dicionario_curtiu['review'].append(int(percent))
            print(f'O valor extraído é: {percent}')
            self.dicionario_curtiu['like'].append(0)
            self.dislike = True

    def on_to_pandas_csv(self):
        df = pd.DataFrame(self.dicionario_curtiu)
        df.to_csv('treino.csv', index=False)
        self.root.quit()

    def renderizar(self):
        

        self.photo = ImageTk.PhotoImage(self.image)
        

        # Crie um rótulo (label)
        self.label = tk.Label(self.root, image=self.photo)
        self.label.pack(pady=20)

        like_frame = tk.Frame(self.root)
        like_frame.pack(pady=10) 


        curtir = tk.Button(like_frame, text="Curtir", command=self.on_curtir)
        curtir.pack(side=tk.LEFT, padx=5)  

        nao_curtir = tk.Button(like_frame, text="Não Curtir", command=self.on_nao_curtir)
        nao_curtir.pack(side=tk.LEFT, padx=5) 

        csv = tk.Button(like_frame, text="Para CSV", command=self.on_to_pandas_csv)
        csv.pack(side=tk.LEFT, padx=5) 

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10) 


        anterior = tk.Button(button_frame, text="Anterior", command=self.on_button_antes)
        anterior.pack(side=tk.LEFT, padx=5) 

        proximo = tk.Button(button_frame, text="Proximo", command=self.on_button_proximo)
        proximo.pack(side=tk.LEFT, padx=5) 
        
   
        self.root.mainloop()

if __name__ == '__main__':
    tela = Tela()
    tela.renderizar()