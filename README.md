# Calculadora de Divisão Ponderada

Uma aplicação web desenvolvida em Streamlit para calcular a divisão ponderada de rendimentos fixos baseada em contratos de vendedores.

## 🚀 Funcionalidades

- **Upload de Planilhas**: Suporte para arquivos Excel (.xlsx) e CSV (.csv)
- **Processamento Automático**: Extrai automaticamente dados de vendedores, contratos e valores
- **Cálculo Ponderado**: Distribui rendimentos fixos (salário + auxílio) proporcionalmente aos contratos
- **Interface Intuitiva**: Interface amigável com abas organizadas
- **Exportação de Resultados**: Download dos resultados em formato CSV
- **Validação de Dados**: Verifica colunas obrigatórias e formatação

## 📋 Requisitos

- Python 3.7+
- Dependências listadas em `requirements.txt`

## 🛠️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/calculadora-divisao-ponderada.git
cd calculadora-divisao-ponderada
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
streamlit run app.py
```

## 📊 Como Usar

### 1. Preparar a Planilha
A planilha deve conter as seguintes colunas:
- `vendedor`: Nome do vendedor
- `contrato`: Identificador do contrato
- `valor`: Valor do contrato (formato numérico)

### 2. Upload e Configuração
- Faça upload da planilha na aba "Upload e Dados"
- Insira o salário fixo e auxílio para cada vendedor
- A aplicação calculará automaticamente os totais

### 3. Análise dos Resultados
- Na aba "Resultados e Análise", selecione um vendedor
- Visualize a divisão ponderada dos rendimentos fixos
- Baixe os resultados em formato CSV

## 🔧 Estrutura do Projeto

```
calculadora-divisao-ponderada/
├── app.py              # Aplicação principal Streamlit
├── requirements.txt    # Dependências Python
├── config.toml        # Configurações do Streamlit
└── README.md          # Este arquivo
```

## 📱 Tecnologias Utilizadas

- **Streamlit**: Framework para aplicações web em Python
- **Pandas**: Manipulação e análise de dados
- **OpenPyXL**: Leitura de arquivos Excel
- **NiceGUI**: Interface gráfica alternativa

## 🎨 Personalização

O arquivo `config.toml` permite personalizar:
- Cores do tema
- Configurações visuais
- Comportamento da aplicação

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.

---

Desenvolvido com ❤️ usando Streamlit e Python
