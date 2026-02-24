# 📦 Monitoramento de Estoque de Medicamentos do SUS

Projeto para consulta e monitoramento de estoque de medicamentos por estabelecimento (CNES), utilizando:

- WebScraping para obtenção do código CATMAT
- API do BNAFAR (Base Nacional da Assistência Farmacêutica)
- API do IBGE para dados complementares
- Frontend interativo em Streamlit

---

## 🎯 Objetivo

Permitir a visualização do estoque real de medicamentos por local (CNES), considerando:

- Soma total de estoque
- Filtro de quantidade_estoque > 0
- Agrupamento por estabelecimento
- Bloqueio de datas futuras
- Consulta dinâmica por medicamento

---

## 🏗️ Arquitetura do Projeto

1. WebScraping → Busca código CATMAT no sistema do governo
2. Consulta API BNAFAR → Retorna estoque por CNES
3. Consulta API IBGE → Enriquecimento de dados por município
4. Processamento → Filtros e agregações
5. Streamlit → Visualização interativa

---

## 🔎 1️⃣ WebScraping - Código CATMAT

Foi desenvolvido um scraper para buscar o código CATMAT no portal do governo.

Arquivo: scraper.py
