# GRIPy

## Geofísica de Reservatório Interativa em Python

O **GRIPy** é um software para manipulação de perfis de poço. É desenvolvido pelos pesquisadores [GIR](http://www.giruenf.net/) na [UENF](http://www.uenf.br/).

## Requisitos
* Python 3.6
* NumPy 1.8.2
* Matplotlib 2.2
* SciPy 0.14.0
* scikit-learn 0.15.2
* PyMC 2.3.4
* wxPython 4.0.0

Sugerimos que utilizem o [Anaconda](https://www.continuum.io/downloads), pois já conta com todas as bibliotecas necessárias (exceto o versão wxPython), assim como com um ambiente de desenvolvimento completo.

O wxPython 4.0.x pode ser instalado através de PIP, utilizando o comando

    pip install --pre --find-links http://wxpython.org/Phoenix/snapshot-builds/ wxPython

## Instalação com wxPython Phoenix e Python 2.7 no Linux

### Ubuntu 16.04 e 17.04, sem utilizar o conda (ou miniconda)

1. Instalar dependências do wxPython (pode usar um único comando) tomando cuidado para utilizar as versões apropriadas

        sudo apt-get install dpkg-dev
        sudo apt-get install build-essential
        sudo apt-get install python2.7-dev
        sudo apt-get install libwebkitgtk-dev
        sudo apt-get install libjpeg-dev
        sudo apt-get install libtiff-dev
        sudo apt-get install libgtk2.0-dev
        sudo apt-get install libsdl1.2-dev
        sudo apt-get install libgstreamer-plugins-base1.0-dev
        sudo apt-get install libnotify-dev
        sudo apt-get install freeglut3
        sudo apt-get install freeglut3-dev
        sudo apt-get install python-pip
    
    > **Observação:** No caso de a biblioteca `libgstreamer-plugins-base1.0-dev` não estar disponível deve-se utilizar a versão `libgstreamer-plugins-base0.10-dev`

2. (**Somente para Ubuntu 17.04**) Baixar libpng12-0 em [https://packages.ubuntu.com/xenial/amd64/libpng12-0/download](https://packages.ubuntu.com/xenial/amd64/libpng12-0/download)

3. (**Somente para Ubuntu 17.04**) Instalar libpng12-0

        sudo dpkg -i nomedoarquivo.deb
      
4. Atualizar o pip

        pip install --upgrade pip
    
    > **Observação:** Caso algum dos comandos `pip` dê erro deve-se adicionar `sudo -H` ao seu início (por exemplo, `sudo -H pip install ...`)

5. Instalar wxPython 4

        pip install -U --pre -f https://wxpython.org/Phoenix/snapshot-builds/linux/gtk3/ubuntu-16.04 wxPython

6. Instalar outras bibliotecas

        pip install numpy scipy matplotlib enum34

7. Instalar o git (também há a opção de baixar o GRIPy diretamente do [repositório](https://github.com/giruenf/GRIPy) sem instalar o git)

        sudo apt-get install git

8. Clonar repositório do GRIPy

        git clone git://github.com/giruenf/GRIPy.git NOMEDODIRETORIODEDESTINO

9. Pronto! Para rodar o GRIPy basta ir ao diretório em que ele foi isntalado e digitar

        python main.py
