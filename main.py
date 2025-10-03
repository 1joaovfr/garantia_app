# main.py
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
    
    # Esta linha é CRUCIAL e deve vir ANTES da criação do App
    criar_banco_de_dados()
    
    print("Estrutura do banco de dados verificada.")
    
    sns.set_style("whitegrid")
    
    # Só depois de criar o banco, a aplicação é iniciada
    app = App(themename="cosmo")
    app.mainloop()
    
    print("Sistema finalizado.")