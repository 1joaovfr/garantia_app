import seaborn as sns
from database.setup import criar_banco_de_dados
from ui.main_window import App

if __name__ == "__main__":
    """
    Ponto de entrada da aplicação.
    1. Garante que o banco de dados e suas tabelas existam.
    2. Configura o estilo visual dos gráficos.
    3. Inicia a janela principal da aplicação.
    """
    print("Inicializando o sistema...")
    criar_banco_de_dados()
    
    sns.set_style("whitegrid")
    
    app = App(themename="cosmo")
    app.mainloop()
    print("Sistema finalizado.")