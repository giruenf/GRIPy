## GriPy: Geofísica de Reservatório Interativa em Python

**GriPy**, acrônimo para Geofísica de Reservatório Interativa em Python, como explicitamente indicado, é um aplicativo escrito em linguagem Python e bibliotecas especialistas, projetado especialmente para a execução de estudos de caracterização e modelagem petrofísica probabilística com integração de dados e informações de rocha-perfil-sísmica.  
O início de seu desenvolvimento ocorreu em 2013, através de um projeto patrocinado pela PETROBRAS com recursos da cláusula de P&D da Agência Nacional de Petróleo (ANP). O amadurecimento da consolidação da arquitetura do software foi seguido da proposta aprovada pela PETROBRAS de distribuição livre dos módulos básicos do GriPy na modalidade de código aberto (_open source_), com possibilidade de construção de módulos específicos na forma de _plugins_ com acesso aberto ou restrito.  
O software ainda está em estágio precoce de desenvolvimento com poucas funcionalidades para uso prático, sendo disponibilizado apenas para servir como uma plataforma de desenvolvimento de novas funcionalidades e fluxos de trabalho. O objetivo é que em breve teremos todas as funcionalidades básicas, incluindo a manipulação de arquivos (leitura e escrita), visualização (plotagem de perfis, _crossplots_, etc), edição de perfis, cálculo convencional de propriedades petrofísicas, modelagem sísmica em poços e análises de dados petrofísicos em testemunhos.  
O desenvolvimento do software é conduzido por pesquisadores do Grupo de Inferência de Reservatório [(GIR)](http://www.giruenf.net/) na Universidade Estadual do Norte Fluminense [(UENF)](http://www.uenf.br/).



## Requisitos
* Python 3.6 (ou maior)
* NumPy 1.17.2 (ou maior)
* Matplotlib 3.1.1 (ou maior)
* SciPy 1.2.1 (não pode ser maior)
* scikit-learn 0.21.3 (ou maior)
* PyMC 3.6 (ou maior) 
* wxPython 4.0.0 (ou maior)

Uma boa ferramenta para a utilização do software, embora não seja a única, é o [Anaconda](https://www.continuum.io/downloads), pois conta com todas as bibliotecas necessárias (exceto o versão wxPython), assim como com um ambiente de desenvolvimento completo.

