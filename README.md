# Sistema de Gestão de Garantias

Este é um aplicativo de desktop desenvolvido em Python para gerenciar o ciclo de vida completo de garantias de autopeças, desde o recebimento da nota fiscal do cliente até o processamento da nota fiscal de retorno.

## Funcionalidades Principais

* **Lançamento de Garantias:** Cadastro de notas fiscais de garantia e seus respectivos itens.
* **Análise Técnica:** Módulo para registrar a análise de cada item (procedência, código de avaria, etc.).
* **Lançamento de Retornos:** Módulo para registrar as notas fiscais de retorno e vincular seus itens às garantias de origem.
* **Gestão de Dados:** Uma visão completa de todos os dados, com dashboards e a funcionalidade de exportação para Excel.
* **Base de Dados Local:** Utiliza SQLite para um funcionamento simples e sem necessidade de servidor.

## Pré-requisitos

* Python 3.10 ou superior.

## Instalação

Siga os passos abaixo para configurar o ambiente e rodar a aplicação.

1.  **Clone ou Baixe o Repositório:**
    Coloque todos os arquivos do projeto em uma pasta no seu computador.

2.  **Crie um Ambiente Virtual:**
    Abra o terminal na pasta do projeto e execute o comando para criar um ambiente virtual chamado `venv`.

    ```bash
    python -m venv venv
    ```

3.  **Ative o Ambiente Virtual:**
    * No **Windows**:
        ```bash
        .\venv\Scripts\activate
        ```
    * No **macOS / Linux**:
        ```bash
        source venv/bin/activate
        ```

4.  **Instale as Dependências:**
    Com o ambiente ativado, instale todas as bibliotecas necessárias a partir do arquivo `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

## Uso da Aplicação

O uso da aplicação é dividido em três etapas: criação do banco, população com dados e execução.

#### 1. Primeira Execução (Criação do Banco)

Na primeira vez que você rodar a aplicação principal, ela criará automaticamente o arquivo de banco de dados (`garantias.db`) com toda a estrutura de tabelas necessária.

```bash
python main.py
```
Após a criação, você pode fechar a aplicação para popular os dados.

#### 2. Populando o Banco de Dados (Passo Essencial)

Para que a aplicação funcione com dados, siga estes dois passos:

* **a) Popule os Dados Mestre (Clientes, Produtos, etc.):**
    Certifique-se de que a pasta `seed_data` contém os seus arquivos Excel. Em seguida, execute o script `seed.py`.

    ```bash
    python seed.py
    ```

* **b) Gere Dados de Teste (Notas Fiscais e Itens de Garantia):**
    Para ter um ambiente rico para testes, execute o `gerador_de_testes.py`. Ele criará notas fiscais com status variados (Pendente, Analisado, etc.).

    ```bash
    python gerador_de_testes.py
    ```

#### 3. Executando a Aplicação Principal

Com o banco de dados criado e populado, inicie a aplicação.

```bash
python main.py
```

---

## Guia de Funcionalidades e Dados de Exemplo

Use os dados abaixo para testar cada módulo.

### Módulo 1: Lançamento de Garantia

Esta aba serve para cadastrar uma nova nota fiscal de garantia recebida de um cliente.

| Campo | Dado de Exemplo |
| :--- | :--- |
| **CNPJ:** | `(Use um CNPJ de um cliente que exista no seu Excel)` |
| **Nº da Nota:** | `99999` |
| **Data da Nota:** | `(Escolha uma data no calendário)` |
| **Itens da Nota:** | 1. **Cód. Item:** `(Use um código de produto do seu Excel)`, **Qtd:** `10`, **Valor Unitário:** `150.75` |
| | 2. **Cód. Item:** `(Outro código)`, **Qtd:** `5`, **Valor Unitário:** `88.00`, **Ressarcimento:** `(Marque a caixa e preencha um valor)` |

### Módulo 2: Análise de Garantia

Aqui você processa os itens que estão com status "Pendente de Análise".

1.  Selecione um item na tabela superior.
2.  Preencha o formulário "Formulário de Análise" abaixo com dados de exemplo:
    | Campo | Dado de Exemplo |
    | :--- | :--- |
    | **Nº de Série:** | `BR-12345-XYZ` |
    | **Cód. Avaria:** | `(Escolha um código da lista)` |
    | **Origem:** | `Produzido` |
    | **Fornecedor:** | `Fornecedor Exemplo LTDA` |
3.  Clique em "Guardar Análise". O item desaparecerá da lista de pendentes.

### Módulo 3: Lançamento de Retorno

Este módulo registra a NF-e de retorno que a sua empresa emite.

**Cenário de Teste:** Simular o retorno de 8 unidades do produto `PROD-A`, originadas das notas `1001` e `1002`.

1.  **Preencha o Painel da Esquerda:**
    | Campo | Dado de Exemplo |
    | :--- | :--- |
    | **Número da Nota de Retorno:** | `554433` |
    | **Dados Adicionais (Referência):** | `Devolução de garantia ref. as notas 1001, 1002` |
    | **Itens da Nota (para adicionar):** | 1. **Cód. Produto:** `(Código de um item gerado pelo script)`, **Qtd:** `8` |

2.  **Busque as Origens:** Clique no botão **"Buscar Origens"**. A tabela da direita será preenchida com os itens correspondentes às notas 1001 e 1002 que já foram **analisados**.

3.  **Distribua as Quantidades:**
    * Clique em uma linha de origem na tabela da direita.
    * No campo "Qtd. para o item selecionado", digite a quantidade que está sendo retornada daquela origem específica.
    * Clique em "Definir Quantidade".
    * Repita para outras linhas até que o "Total Vinculado" fique verde e seja igual ao "Total na NF Retorno".

4.  **Finalize:** Clique em "Salvar Vínculos e Finalizar Retorno".

### Módulo 4: Gestão de Dados

Esta aba oferece uma visão completa e consolidada.

* **Visão de Tabela:** Mostra todos os itens de garantia já cadastrados. Use o botão **"Extrair para Excel"** no canto inferior direito para exportar a visão atual.
* **Visão de Dashboards:** Use os filtros de **Ano**, **Mês** e **Grupo** para visualizar os gráficos de status e ressarcimento de forma dinâmica.

## Estrutura do Projeto

O projeto segue uma arquitetura em camadas para facilitar a manutenção e escalabilidade:
* `/database/`: Scripts para criação e conexão com o banco de dados.
* `/repository/`: Camada de acesso a dados. Contém todas as queries SQL.
* `/services/`: Camada de serviço. Contém a lógica de negócio da aplicação.
* `/ui/`: Camada de apresentação. Contém toda a interface gráfica do usuário, dividida por abas.
* `main.py`: Ponto de entrada da aplicação.
