# -*- coding: utf-8 -*-
"""
Created on Wed Nov 08 17:46:45 2017

@author: apfranco
"""

import numpy as np
import scipy
from scipy.optimize import leastsq


def RockPhysicsCalibration(agd, OM):
    
    #        ALGORITMO PARA CALIBRACAO DE MODELOS DE FISICA DE ROCHA
    #
    # MODELOS
    # 1 - porosidade de neutrons:     
        #          phi = A + B phiE + C vsh ou
        # 2 - raios gama:
            #          gr = grmin + (grmax - grmin) vsh
            # 3 - modelo densidade: 
                #          rho = rhoq + (rhof-rhoq) * phiE + (rhoc-rhoq) * vsh * (1 - phiE);
                # 4 - resistividade:
                    #         1/ Rt = ( phiE**m Sw**n ) / ( a Rw (1-chi) )  + ( chi Sw ) /  Rsh
                    #
                    # DESCRICAO GERAL:
                        # O programa deve ser rodado para gerar os coefientes e densidades acima descritos
                        # para serem usados em etapas posteriores de inferencia de porosidade,
                        # volume de argila e saturacao. O programa fornece opcao de entrada de
                        # limites estratigraficos conhecidos, realizando uma calibracao geral para
                        # todo o pacote e tambem em grupos separados em funcao do volume de
                        # folhelho como funcao de um valor de corte (cutclay). O programa fornece 3
                        # opcoes de saida envolvendo calibracao em todo o segmento analizado, em
                        # segmentos menores definidos na entrada (secHoriz) ou em nesses mesmos segmentos
                        # menores subdivididos ainda mais em funcao do conteudo de folhelho.
                        #
                        # PARAMETROS DE ENTRADA:
                            # dados de perfis - raios gama, porosidade, densidade, VP e VS
                            # dados de testemunho (se disponiveis) - volume de argila, porosidade, densidade
                            # top, bot - limites superior e inferior da secao a ser analisada 
                            # phiSand  - porosidade de areia homogenea (zero em conteudo de argila)
                            # grmin, grmax - valores minimo e maximo para a conversao de raios gama em volume de folhelho
                            # cutclay - valor limite para a transicao de areia para folhelho (grao para matriz suportada)
                            # secHoriz - Matriz (nFac x 2) contendo os limites superior e inferior de cada unidade estratigrafica
                            # satUncert - =0 desliga seletor de calibracao para horizonte com oleo.
                            #                Caso contrario iOut necesariamente igual a 3
                            # iOut - seletor de detalhamento de facies para saida de parametros 1, 2,
                            #        ou 3, conforme explicado acima.
                            # modPhiC - seletor do tipo de porosidade de calibracao (porosidade
                            #           efetiva): = 1 perfil porosidade de neutros; = 2 porosidade
                            #           efetiva independente (ex. testemunho); = 3 porosidade efetiva
                            #           calculada pela formula 1 acima.
                            # OBS: CUIDADO opcao modPhiC = 3 carece de aprimoramentos devendo ser usada em
                            # casos muito especificos. Em geral produz matrizes mal condicionadas.
                            #
                            # PARAMETROS DE SAIDA:
                                # calibData_nomePoco - arquivo contendo os dados de referencia para o processo de calibracao
                                #    phiC 
                                #    clayC 
                                #    rhoC
                                #    resC
                                # calibCPR_Vel_nomePoco - arquivo contendo os parametros do modelo linear de velocidade de Han
                                #    facies 
                                #    phiSand 
                                #    neutron 
                                #    denLitho 
                                #    cValuesPhi 
                                #    cValuesChi 
                                #    covMatrixPar
                                #    coefVP 
                                #    coefVS
                                #    fluidProp 
                                #    fluidPars
    print "CHAMANDO A FUNCAO EM ALGO"
    #Parametros de entrada
    inputPars = agd.get_input() 
    well_uid = agd.get_well_uid()
    
    log_index = OM.list('log', well_uid)[0]
    indexes = log_index.get_index()[0]
    z = indexes[0].data
    
    topCL = inputPars.get('topCL', None)    #Intervalo para calibracao (com agua)
    botCL = inputPars.get('botCL', None)
    top = inputPars.get('top', None)        #Intervalo para inferencia 
    bot = inputPars.get('bot', None)
    
    indLog = np.argwhere(np.logical_and(z>=top, z<=bot))
    indLog = np.squeeze(indLog,1)
    
    #Input dos Perfis de pressao
    press_file = np.loadtxt('U:/bkp_Windows06nov2017/Documents/Pocos_Morena/MA20.prs')
    
    z = z[indLog]      

    gr = inputPars.get('gr', None )
    gr = gr[indLog]  
    
    gr = logInterp(gr,z)      
    
    phi = inputPars.get('phi', None ) 
    phi = phi[indLog]
    phi = logInterp(phi,z)     
    
    rhoFull = inputPars.get('rho', None )
    rho = rhoFull[indLog]
    rho = logInterp(rho,z)      
        
    res = inputPars.get('res', None )
    res = res[indLog]
    if (np.all(res == np.NaN)):     
        res = np.empty(np.size(indLog))
    else:
        res = logInterp(res,z)
    
    fac = inputPars.get('fac', None )
    fac = fac[indLog]
    fac = np.array(np.floor(fac), dtype=int)
    fac = logInterp(fac,z)
    
    #Input dos Perfis de pressao
    zProv = indexes[0].data
    mpp = 0.0980665*press_file[:,0]
    mtzp = press_file[:,1]     
    lpres, cpres = np.shape(press_file)
    if (cpres == 3):
        mmzp = press_file[:,cpres - 1]
    else:
        mmzp = np.empty([0,0])
    
    nDP = np.size(mtzp)  
    tvdss = inputPars.get('tvdss', None )
    tvdss = tvdss[indLog]
    izp = np.empty(nDP, dtype=int)
    if (np.size(mmzp) == 0):
        indr = indLog
        lindr = np.size(indr) - 1
        tol = 0.1
        for i in range (0, nDP):
            indp = np.argwhere(np.logical_and(tvdss <= (mtzp[i] + tol), tvdss >= (mtzp[i] - tol)))
            indp= np.squeeze(indp,1)
            cizp = np.argwhere(np.logical_and(indp >= indr[0], indp <= indr[lindr]))
            cizp= np.squeeze(cizp,1)
            if (np.size(cizp) == 0):
                izp[i] = np.argmin(np.abs(tvdss - mtzp[i]))
            else:
                izp[i] = indp[cizp[0]]
        mzp = zProv[izp]
        matsort = np.concatenate([[mzp],[mpp], [mtzp],[izp]]).T    
        indsort = np.argsort(matsort[:,0],0)   
        matsort = np.array([[matsort[indsort,0]],[matsort[indsort,1]],[matsort[indsort,2]],[matsort[indsort,3]]]).T
        matsort = np.squeeze(matsort)
        mzp = matsort[:,0]
        mpp = matsort[:,1]
        mtzp = matsort[:,2]
        izp = matsort[:,3].astype(int)
        zp = zProv[izp[0]:izp[nDP - 1] + 1]
        rhopp = rhoFull[izp[0]:izp[nDP - 1] + 1]
        rhopp = logInterp(rhopp, zp)
    else:
        mzp = mmzp
        for i in range (0, nDP):
            izp[i] = np.argmin(np.abs(zProv - mzp[i]))
        zp = zProv[izp[0]:izp[nDP - 1] + 1]
        rhopp = rhoFull[izp[0]:izp[nDP - 1] + 1] 
        rhopp = logInterp(rhopp, zp)
        
    phiCore = np.empty([0,0])
    secHoriz = np.array([top, bot])  
    
    #Parametros e dados de calibracao e saida
    nFac = 4
    modPhiC = 1  #indicador do tipo de dado de calibracao a ser usado como porosidade efetiva
                 #1: perfil de neutrons  2: perfil de porosidade efetiva
    useCore = 0
    iOut = 2     
    #iuseclay = 0  #indicador do tipo de argilosidade a ser usado
                  #0: vsh direto do perfil 1: clay (calculada atraves do GR) 
    #Parametros de densidade
    rhoMin = np.array([2.55, 2.569, 2.623, 2.707])  #Existem 4 facies na regiao relatada    
    
    #Parametros de resistividade
    mP = 2.0      # expoente de cimentacao em areias limpas: 1.3 (inconsolidado) - 2.0 (consol.)
    nS = 2.0      # expoente de saturacao em areias limpas 1.5 - 2.0. 
                  # E reduzido na presenca de laminacao e microporosidade 
    aT = 0.8      # constante da eq. de Archie
    Rw = 0.028    # resistividade da agua
    Rsh = 2.048   # resistividade do folhelho
    
    resCoef = np.array([[mP, nS, aT*Rw, Rsh], [1.5, nS, aT*Rw, Rsh], [2.0, nS, aT*Rw, Rsh], [2.0, nS, aT*Rw, Rsh]])
    # Secao de Propriedades dos fluidos e matrizes de areia e folhelho
    #Parametros 
    
    #calculo da pressao
    pres_poros = np.mean(mpp) # pressao de poro referencia para o calc da densidade
    temp       = 89.0         # temperatura oC
    sal        = 102400       # salinidade
    RGO        = 75.0         # razao gas oleo
    API        = 29.0         # grau API
    G          = 0.835        # gravidade especifica    
    #Ordenar parametros no vetor para chamada da funcao
    fluidPars = np.array([pres_poros, temp, sal, RGO, API, G])  
    
    #AQUI COMECA O CODIGO secCalibVshPhiRhoRes_vpHan
    
    #Trecho de calibracao
    indCL = np.where(np.logical_and(z>=topCL, z<=botCL))  
    nData = np.size(z)
    
    # Calculo de porosidade efetiva e vsh com estimativa dos valores
    # de grmin e grmax em todo o pacote coberto pelos dados
    # Transformacao dos dados observados 
    # Volume de folhelho a partir de rais gama
    
    indSh = np.argwhere(fac==4)
    indSh= np.squeeze(indSh,1)
    indSd = np.argwhere(fac == 1)
    indSd= np.squeeze(indSd,1)
    
    if (np.size(indSh) == 0 and np.size(indSd) == 0):
        grmax = np.percentile(gr, 95)
        grmin = np.percentile(gr, 5)
    else:
        grmax = np.percentile(gr[indSh], 95) #146.3745 
        grmin = np.percentile(gr[indSd], 5) #54.2600 
    
    claye = vshGRcalc(gr, grmin, grmax)
    
    #Por enquanto usando apenas modPhic == 1
    if modPhiC == 1:
        grlim = grmax
        ind = np.where (gr>= grlim)
        phiNsh = np.median(phi[ind])
        phiEe = np.fmax(0.01, phi - claye*phiNsh)
        modPhiC =2
    elif (modPhiC == 2 and np.size(phiCore) == 0):
        print "Nao existe a funcao chamada aqui dentro"
        #phiEe = phiSd2phiE (zR, claye, phiSand, secHoriz)   
    elif (modPhiC == 2 and useCore == 1 ):
        phiEe = phiCore
    
    #fluidProp matriz com valores para Kf e densidade para fases salmoura,
    #oleo e gas, ordenados da seguinte forma:
    #bulk_salmoura, bulk_oleo, bulk_gas (modulo variavel com a pressao
    #rho_salmoura, rho_oleo, rho_gas  (so a densidade sera fixa)
    nDP = np.size(mpp)
    
    fluidPropP = np.empty([nDP, 2, 3])   #esqueleto de nDP 'paginas' que guardara 
                                         #as matrizes 2x3 de retorno da funcao seismicPropFluids
    for i in np.arange(0, nDP):
        #atualizar pressao de poro
        fluidPars[0] = mpp[i]
        fluidPropP[i] = seismicPropFluids(fluidPars)
        
    fluidProp = np.mean(fluidPropP, 0)
    rhoFluids = fluidProp[1]
    rhoW = rhoFluids[0]
    rhoO = rhoFluids[1]
    
    #rock physics model calibration
    #selecao de perfis apenas na regial de calibracao com agua
    phiC = phiEe[indCL]
    clayC = claye[indCL]
    rhoCL = rho[indCL]
    resCL = res[indCL]
    phiCL = phi[indCL]
    facCL = fac[indCL]
    
    # Calibracao para toda a secao
    rhoMin_T = np.median(rhoMin);
    opt = 2
    
    if (opt == 1):
        [cPhi_T, phiMod_T, cRho_T, rhoMod_T, cRes_T, resMod_T] = calibClayPhiRhoRes(phiCL, rhoCL, resCL, clayC, phiC, rhoMin_T, resCoef, modPhiC)
        rhoSd = cRho_T[0]
        rhoWe = cRho_T[1]
        rhoSh = cRho_T[2]
        rhoDisp = cRho_T[2]
    else:
        [cPhi_T, phiMod_T, cRho_T, rhoMod_T, cRes_T, resMod_T] = calibClayPhiRhoRes2(phiCL, rhoCL, resCL, clayC, phiC , rhoW, resCoef, modPhiC)
        rhoSd = cRho_T[0]
        rhoWe = rhoW
        rhoSh = cRho_T[1]
        rhoDisp = cRho_T[1]
    
    phiPar_T = np.concatenate([[cPhi_T[0]], [cPhi_T[1]], [cPhi_T[2]]])
    denPar_T = np.concatenate([[rhoSd], [rhoWe], [rhoO], [rhoSh], [rhoDisp]])
    resPar_T = cRes_T
    [phiMod_T, rhoMod_T, resMod_T] = calibCPRRreMod(phiEe, claye, phiPar_T , denPar_T, resPar_T, modPhiC)
    facies_T = np.ones((nData,1))
    phiMod = np.zeros((nData,1))
    rhoMod = np.zeros((nData,1))
    resMod = np.zeros((nData,1))
    
    phiPar = np.empty([nFac,3])
    denPar = np.empty([nFac,5])
    resPar = np.empty([nFac,4])
    facH = np.zeros([np.size(facCL),1])
    for i in range(0,nFac):
        ind = np.argwhere(facCL == i + 1)
        ind= np.squeeze(ind,1)
        secPhi = phiCL[ind]
        secRho = rhoCL[ind]
        secRes = resCL[ind]
        secClayC = clayC[ind]
        secPhiC = phiC[ind]
        #[cHan,vpMod(ind),s2] = calibHan(secVP,secPhiC,secClayC);
        #coefHanVP(i,:) = cHan';    
        
        # a parte de porosidade de neutrons e densidade nao utiliza separacao
        # e calibracao distinta para grupamentos em termos de volume de
        # folhelho. Os coeficientes sao repetidos (iguais) para areia e folhelho
        resCoef_line = np.empty((resCoef.shape[0],1))
        resCoef_line[:,0] = resCoef[i]
        if (opt == 1):
            [cPhi, dataPhi, cRho, dataRho, cRes, dataRes] = calibClayPhiRhoRes(secPhi, secRho, secRes, secClayC, secPhiC , rhoMin[i], resCoef_line, modPhiC)
            rhoSd = cRho_T[0]
            rhoWe = cRho_T[1]
            rhoSh = cRho_T[2]
            rhoDisp = cRho_T[2]
        else:
            [cPhi, dataPhi, cRho, dataRho, cRes, dataRes] = calibClayPhiRhoRes2(secPhi, secRho, secRes, secClayC, secPhiC , rhoW, resCoef_line, modPhiC)
            rhoSd = cRho_T[0]
            rhoWe = rhoW
            rhoSh = cRho_T[1]
            rhoDisp = cRho_T[1]
       
        phiPar[i] = np.array([cPhi[0], cPhi[1], cPhi[2]])
        denPar[i] = np.array([rhoSd, rhoWe, rhoO, rhoSh, rhoDisp])
        resPar[i] = cRes
        facH[ind] = i + 1
        resPar_line = np.empty([1,nFac])   
        resPar_line[0,:] = resPar[i]
        ind = np.argwhere(fac == i + 1)
        ind= np.squeeze(ind,1)
        passArg = np.array([rhoSd, rhoW, rhoSh])
        [dataPhi, dataRho, dataRes] = calibCPRRreMod(phiEe[ind], claye[ind], phiPar[i],passArg, resPar_line, modPhiC)
        phiMod[ind,0] = dataPhi
        rhoMod[ind,0] = dataRho
        resMod[ind] = dataRes
    
    if (iOut == 1):
        nOutFac = 1
        facies = facies_T
        neutron = phiPar_T
        denLitho = denPar_T
        rhoComp = rhoMod_T
        phiComp = phiMod_T
        resComp = resMod_T
    elif (iOut == 2):
        nOutFac = np.ones([nFac,1])
        facies = facH
        neutron = phiPar
        denLitho = denPar
        denLitho[:,4] = neutron[:,2]
        rhoComp = rhoMod
        phiComp = phiMod
        resComp = resMod
    else:
        raise Exception ('Seletor de saida deve ser 1 ou 2')
        
    r2Phi = rsquared (phiComp, phi)
    r2Rho = rsquared (rhoComp, rho)
    r2Res = rsquared (resComp, res)
    
    print "Fim da calibracao, com seguintes ajustes R2:\n Phi = %7.2f\n RHO = %7.2f\n RES = %7.2f\n" % (r2Phi, r2Rho, r2Res)
    
    #Saida de Dados
    
            
def calibClayPhiRhoRes(phi, rho, Rt, vsh, phiE, rhoMin, RtCoef, mode):
   
    """ FINALIDADE: calcular parametros dos modelos de porosidade e densidade
    a partir do ajuste dos dados de perfis de porosidade de neutrons e de 
    densidade, usando informacoes de volume de folhelho e de porosidade efetiva 
    com 3 opcoes distintas para a porosidade efetiva:
     
    1 - usa o proprio perfil de neutrons como porosidade efetiva (identidade)
    2 - usa um perfil independente de porosidade efetiva (ex. testemunho)

    ENTRADA:
       
    phi - perfil de neutrons 
    rho - perfil de densidade
    vsh - volume de folhelho (normalmente extraido do perfil de raios gama)
    phiE - perfil de porosidade efetiva 
    rhoMin  - densidade media dos graos minerais constituintes da matriz da rocha
    RtCoef - 
 
    mode - indicador de porosidade efetiva, sendo 1, 2 ou 3 conforme os
           casos acima descritos.

    SAIDA:
 
    phiPar  - parametros de ajuste do modelo de porosidade de neutrons
    phiComp - perfil calculado de porosidade de neutrons
    rhoPar  - parametros de ajuste do modelo de densidade
    rhoComp - perfil calculado de densidade

    MODELOS
       
    porosidade de neutrons:     
        phi = A + 1.0 phiE + C vsh 
    modelo de densidade: 
        rho = rhoq + (rhof-rhoq) * phiE + (rhoc-rhoq) * vsh;
    modelo de resistividade:
        Rt = ( phiE**m Sw**n ) / ( a Rw (1-chi) )  + ( chi Sw ) /  Rsh
    """
    if((mode != 1) and (mode != 2) and (mode != 3)):
        raise Exception("Seletor de porosidadade efetiva de entrada deve ser 1 ou 2!")
    
    n = np.size(vsh)  
    
    if (np.size(phi) != n or np.size(rho) != n):
        raise Exception("Vetores de entrada devem ter as mesmas dimensoes")
        
    if (mode == 1 or mode == 2 and np.size(phiE) != n ):
        raise Exception ("Vetor de entrada de porosidade efetiva nao esta com dimensao apropriada")

    options = np.empty([0,0])
    lb = np.array([0.0, 0.5])
    ub = np.array([0.5, 4.0])
    x0 = RtCoef[2:4,0]
    cRes = RtCoef[0:2,0]
    
    phiPar = np.empty(3)    
    rhoPar = np.empty(3)
    if (mode == 1):
        # o proprio perfil de neutrons fornece a porosidade efetiva, segundo o
        # modelo phiN = phiE
        phiPar = np.array([0.0, 1.0, 0.0])
        phiComp = phiE
    elif (mode == 2):
        #nesse caso phiE e' um vetor de porosidade efetiva 
        col1 = 1 - (phiE + vsh)     
        A = np.concatenate([[col1], [phiE], [vsh]]).T
        xPhi2 = fitNorm1(A,phi,10)
        # parametros do modelo para ajuste da porosidade de neutrons
        phiPar[0] = xPhi2[0]
        phiPar[1] = xPhi2[1]
        phiPar[2] = xPhi2[2]
        phiComp = col1 * phiPar[0] + phiE * phiPar[1] + vsh * phiPar[2]
    elif (mode ==3):
        phiSand = 0.25
        #nesse caso phiE e' um vetor de porosidade efetiva 
        col1 = 1 - (phiSand + vsh)
        col2 = np.ones(n)*phiSand
        A = np.concatenate([[col1], [col2], [vsh]]).T
        xPhi2 =   fitNorm1(A,phi,10)
        #parametros do modelo para ajuste da porosidade de neutrons
        phiPar[0] = xPhi2[0]
        phiPar[1] = xPhi2[1]
        phiPar[2] = xPhi2[2]
        phiComp = col1 * phiPar[0] + phiE * phiPar[1] + vsh * phiPar[2]
    
    vecConc = vsh*(1-phiE)
    B = np.concatenate([[phiE], [vecConc]])
    xRho1 = fitNorm1(B, (rho - rhoMin), 10)
    rhoPar[0] = rhoMin
    rhoPar[1] = xRho1[0] + rhoMin
    rhoPar[2] = xRho1[1] + rhoMin
    rhoComp = np.dot(B,xRho1) + rhoMin
    xRes = scipy.optimize.leastsq(ofSimandouxPhiChiSw100, x0, args=(Rt, cRes, phiE, vsh))[0]  #checar como vai se comportar sem lb e ub
    RtPar = np.concatenate([cRes, xRes])
    RtPar = RtPar.reshape(1, RtPar.size)
    facies = np.ones((n,1))
    RtComp = dCompSimandouxPhiChiSw100(phiE,vsh,facies,RtPar)
    
    return phiPar, phiComp, rhoPar, rhoComp, RtPar, RtComp

def calibClayPhiRhoRes2(phi, rho, Rt, vsh, phiE, rhoWater, RtCoef, mode):
   
    """ FINALIDADE: calcular parametros dos modelos de porosidade e densidade
    a partir do ajuste dos dados de perfis de porosidade de neutrons e de 
    densidade, usando informacoes de volume de folhelho e de porosidade efetiva 
    com 3 opcoes distintas para a porosidade efetiva:
     
    1 - usa o proprio perfil de neutrons como porosidade efetiva (identidade)
    2 - usa um perfil independente de porosidade efetiva (ex. testemunho)

    ENTRADA:
       
    phi - perfil de neutrons 
    rho - perfil de densidade
    vsh - volume de folhelho (normalmente extraido do perfil de raios gama)
    phiE - perfil de porosidade efetiva 
    rhoWater  - densidade da agua
    RtCoef - 
 
    mode - indicador de porosidade efetiva, sendo 1, 2 ou 3 conforme os
           casos acima descritos.

    SAIDA:
 
    phiPar  - parametros de ajuste do modelo de porosidade de neutrons
    phiComp - perfil calculado de porosidade de neutrons
    rhoPar  - parametros de ajuste do modelo de densidade
    rhoComp - perfil calculado de densidade

    MODELOS
       
    porosidade de neutrons:     
        phi = A + 1.0 phiE + C vsh 
    modelo de densidade: 
        rho = rhoq + (rhof-rhoq) * phiE + (rhoc-rhoq) * vsh;
    modelo de resistividade:
        Rt = ( phiE**m Sw**n ) / ( a Rw (1-chi) )  + ( chi Sw ) /  Rsh
    """
    if((mode != 1) and (mode != 2) and (mode != 3)):
        raise Exception("Seletor de porosidadade efetiva de entrada deve ser 1 ou 2!")
    
    n = np.size(vsh)  
    
    if (np.size(phi) != n or np.size(rho) != n):
        raise Exception("Vetores de entrada devem ter as mesmas dimensoes")
        
    if (mode == 1 or mode == 2 and np.size(phiE) != n ):
        raise Exception ("Vetor de entrada de porosidade efetiva nao esta com dimensao apropriada")

    options = np.empty([0,0])
    lb = np.array([0.0, 0.5])
    ub = np.array([0.5, 4.0])
    x0 = RtCoef[2:4,0]
    cRes = RtCoef[0:2,0]
    phiPar = np.empty(3)
    if (mode == 1):
        # o proprio perfil de neutrons fornece a porosidade efetiva, segundo o
        # modelo phiN = phiE
        phiPar = np.array([0.0, 1.0, 0.0])
        phiComp = phiE
    elif (mode == 2):
        #nesse caso phiE e' um vetor de porosidade efetiva 
        col1 = 1 - (phiE + vsh)     
        A = np.concatenate([[col1], [phiE], [vsh]]).T
        xPhi2 = fitNorm1(A,phi,10)
        # parametros do modelo para ajuste da porosidade de neutrons
        phiPar[0] = xPhi2[0]
        phiPar[1] = xPhi2[1]
        phiPar[2] = xPhi2[2]
        phiComp = col1 * phiPar[0] + phiE * phiPar[1] + vsh * phiPar[2]
    elif (mode ==3):
        phiSand = 0.25
        #nesse caso phiE e' um vetor de porosidade efetiva 
        col1 = 1 - (phiSand + vsh)
        col2 = np.ones(n)*phiSand
        A = np.concatenate([[col1], [col2], [vsh]]).T
        xPhi2 =   fitNorm1(A,phi,10)
        #parametros do modelo para ajuste da porosidade de neutrons
        phiPar[0] = xPhi2[0]
        phiPar[1] = xPhi2[1]
        phiPar[2] = xPhi2[2]
        phiComp = col1 * phiPar[0] + phiE * phiPar[1] + vsh * phiPar[2]
    
    col2 = vsh*(1-phiE)
    col1 = (1-vsh)*(1-phiE)
    B = np.concatenate([[col1], [col2]]).T
    rhoCte = rhoWater * phiE    
    xRho = fitNorm1(B, (rho - rhoCte),10)
    rhoPar = np.empty(2)
    rhoPar[0] = xRho[0]
    rhoPar[1] = xRho[1]
    rhoComp = np.dot(B, xRho) + rhoCte
    xRes = scipy.optimize.leastsq(ofSimandouxPhiChiSw100, x0, args=(Rt, cRes, phiE, vsh))[0]  
    print "VALORES DE xRES", xRes
    RtPar = np.concatenate([cRes, xRes])
    RtPar = np.reshape(RtPar,(1,np.size(RtPar)))
    facies = np.ones((n,1))
    RtComp = dCompSimandouxPhiChiSw100(phiE,vsh,facies,RtPar)
    
    return phiPar, phiComp, rhoPar, rhoComp, RtPar, RtComp

def calibCPRRreMod(phiE, vsh, phiPar, rhoPar, RtPar, mode):
    # FINALIDADE: calcular os dados modelados usando os modelos calibrados 
    # em outro intervalo do poco, seguindo as 3 opcoes distintas para a porosidade efetiva:
        # 1 - usa o proprio perfil de neutrons como porosidade efetiva (identidade)
        # 2 - usa um perfil independente de porosidade efetiva (ex. testemunho)
        #
        # ENTRADA:
            # phi - perfil de neutrons 
            # rho - perfil de densidade
            # vsh - volume de folhelho (normalmente extraido do perfil de raios gama)
            # phiE - perfil de porosidade efetiva 
            # phiPar
            # rhoPar  - densidade da agua
            # RtPar - 
            # mode    - indicador de porosidade efetiva, sendo 1, 2 ou 3 conforme os
            #           casos acima descritos.
            #
            # SAIDA:
                # phiComp - perfil calculado de porosidade de neutrons
                # rhoComp - perfil calculado de densidade
                # RtComp
                #
                #
                # MODELOS
                # porosidade de neutrons:     
                    #    phi = A + 1.0 phiE + C vsh 
                    # modelo de densidade: 
                        #    rho = rhoq + (rhof-rhoq) * phiE + (rhoc-rhoq) * vsh;
                        # modelo de resistividade:
                            #          Rt = ( phiE**m Sw**n ) / ( a Rw (1-chi) )  + ( chi Sw ) /  Rsh
    if (mode != 1 and mode != 2 and mode != 3):
        raise Exception ('Seletor de porosidadade efetiva de entrada deve ser 1 ou 2')
    n = np.size(vsh)
    
    if (mode == 1 or mode == 2 and np.size(phiE) != n ):
        raise Exception ('Vetor de entrada de porosidade efetiva nao esta com dimensao apropriada');
    
    if (mode == 1):
        # o proprio perfil de neutrons fornece a porosidade efetiva, segundo o
        # modelo phiN = phiE
        phiPar = np.array([0.0, 1.0, 0.0])
        phiComp = phiE
    elif (mode ==2):
         #nesse caso phiE e' um vetor de porosidade efetiva    
        col1 = 1 - phiE + vsh
        phiComp = col1 * phiPar[0] + phiE * phiPar[1] + vsh * phiPar[2]
    elif (mode == 3):
        phiSand = 0.25        
        # nesse caso phiE e' um vetor de porosidade efetiva
        col1 = 1 - (phiSand + vsh)
        phiPar[0] = xPhi2[0]
        phiPar[1] = xPhi2[1]                   #Verificar o uso desse mode 3, talvez seja melhor cortar fora do if la em cima
        phiPar[2] = xPhi2[2]
        phiComp = col1 * phiPar[0] + phiE * phiPar[1] + vsh * phiPar[2]
    
    col2 = vsh*(1-phiE)
    col1 = (1-vsh)*(1 - phiE)
    B = np.concatenate([[col1], [col2]])
    rhoCte = rhoPar[1]*phiE
    rhoComp = col1 * rhoPar[0] + col2*rhoPar[2] + rhoCte
    
    facies = np.ones((n,1))
    RtComp = dCompSimandouxPhiChiSw100(phiE,vsh,facies,RtPar)

    return phiComp, rhoComp, RtComp
    
def fitNorm1(A, d, maxIt):
    
    xLS = np.linalg.lstsq(A,d)[0]
    dComp = np.dot(A,xLS)
    res = d - dComp
    rmsOld = np.sqrt(np.sum(res**2))
    drms = 1
    it = 1
    
    while (drms > 1e-07 or it == maxIt):
        R = np.diag(1./(np.abs(res) + 1e-08 ))
        B1 = np.dot(A.T, R)
        B = np.dot(B1, A)
        b = np.dot(B1,d)
        xN1 = np.linalg.lstsq(B,b)[0]
        dComp = np.dot(A,xN1)
        res = d - dComp
        rms = np.sqrt(np.sum(res**2))
        drms = rms - rmsOld
        rmsOld = rms
        it = it + 1
    
    return xN1
    
def seismicPropFluids(fluidPars):
    """ II - CONSTRUTOR DE FLUIDO (PROPRIEDADES SISMICAS DA AGUA DE FORMACAO, OLEO E GAS, BEM COMO MISTURA)
             * OBS: atentar para as unidades, dens = g/cm3, 
    
    Salinidade (ppm) - retiradas do livro WEC Brasil, pagina IV-8 (tabela: leituras caracterisiticas das ferramentas de perfilagem)
    sal = 330000 ppm @ 80 celsius
    Temperatura da formacao (Celsius)
    Pressao de poros (PSI ou KgF) 
    conversao de unidades (pressao) Aqui a unidade tem que ser em MPASCAL, o fornecido e em PSI
    1 PSI = 14,22 kgf/cm2
    1 PSI = 6894,757 Pa
    1 atm = 101,35 KPa
    1 Pa = 1,019716*10^-5 kgf/cm^2
 
    exemplo : pres_poros = 6500;
              pascal = 6500 PSI/ 14.22 = 457,10 pascals 
              1 PSI    = 6894,757 Pa
              6500 psi = X pa     =================> Pa = 44.815.920,50 =========== MPa = 44.8159205 
    exemplo : pres_poros = 287 kgf/cm2;
              287 kgf = 278/1.0197*10^-5 Pa 
                                  =================> Pa = 28.145.532,99 =========== MPa = 28.145534 
    """
    
    #Leitura das propriedades do reservatorio
    
    pres_poros = fluidPars[0];  # pressao de poro
    temp       = fluidPars[1];  # temperatura oC
    sal        = fluidPars[2];  # salinidade
    RGO        = fluidPars[3];  # razao gas oleo
    API        = fluidPars[4];  # grau API
    G          = fluidPars[5];  # gravidade especifica  
    
    # a) Agua doce
    cte_1 = -80*temp - 3.3*(temp**2) + 0.00175*(temp**3) + 489*pres_poros - 2*temp*pres_poros
    cte_2 = + 0.016*(temp**2)*pres_poros - 1.3*(10**(-5))*(temp**3)*pres_poros - 0.333*(pres_poros**2) - 0.002*temp*(pres_poros**2)
    dens_agua_doce = 1 + 1*(10**(-6))*(cte_1 + cte_2)
    
    # pesos
    w = np.empty([5,4]) 
    w[0][0] = 1402.85
    w[1][0] = 4.871
    w[2][0] = -0.04783
    w[3][0] = 1.487*10**(-4)
    w[4][0] = -2.197*10**(-7)
    w[0][1] = 1.524
    w[1][1] = -0.0111
    w[2][1] = 2.747*10**(-4)
    w[3][1] = -6.503*10**(-7)
    w[4][1] = 7.987*10**(-10)
    w[0][2] = 3.437*10**(-3)
    w[1][2] = 1.739*10**(-4)
    w[2][2] = -2.135*10**(-6)
    w[3][2] = -1.455*10**(-8)
    w[4][2] = 5.230*10**(-11)
    w[0][3] = -1.197*10**(-5)
    w[1][3] = -1.628*10**(-6)
    w[2][3] = 1.237*10**(-8)
    w[3][3] = 1.327*10**(-10)
    w[4][3] = -4.614*10**(-13)
    
    v_agua = 0
    
    for i in np.arange(0, 5):
        for j in np.arange (0,4):
            v_agua = v_agua + w[i][j]*(temp**(i))*(pres_poros**(j)) #esse -1 +1 esta assim pq veio do matlab, ajuste de indices
            
    # b) Agua de formacao - salmoura
    S = sal/1000000
    cte_3 = temp*(80 + 3*temp - 3300*S - 13*pres_poros + 47*pres_poros*S)
    cte_4 = 1*(10**(-6))*(300*pres_poros - 2400*pres_poros*S + cte_3)
    dens_salmoura = dens_agua_doce + S*(0.668 + 0.44*S + cte_4)
    
    #converter a densidade salmoura de g/cm3 para kg/m3, ie x10^3, para calcular os modulos elasticos

    cte_5 = 1170 - 9.6*temp + 0.055*(temp**2) - 8.5*(10**(-5))*(temp**3) + 2.6*pres_poros - 0.0029*temp*pres_poros - 0.0476*(pres_poros**2)
    cte_6 = (S**(1.5))*(780 - 10*pres_poros + 0.16*(pres_poros**2)) - 1820*(S**2)
    v_salmoura = v_agua + S*cte_5 + cte_6
    bulk_salmoura_Pa = dens_salmoura*(10**3)*(v_salmoura**2)
    bulk_salmoura = bulk_salmoura_Pa * 10**(-9)
    
    # c) oleo
    
    #RGO -  razao gas/oleo (litro/litro)- caracterisitica do oleo vivo.
    #API do oleo - baseado na densidade (dens_0_oleo) do oleo morto a 15,6 oC e a pressao atmosferica (condicao API) expressa em g/cm3
    #G - gravidade especifica do gas
    
    dens_0_oleo = 141.5/(API + 131.5)
    B_0 = 0.972 + 0.00038*(2.4*RGO*((G/dens_0_oleo)**(0.5)) + temp + 17.8)**(1.175)
    cte_7 = (dens_0_oleo + 0.0012*G*RGO)/B_0
    cte_8 = 0.00277*pres_poros - (1.71*(10**(-7))*(pres_poros**3))
    dens_oleo = cte_7 + cte_8*(cte_7 - 1.15)**2 + 3.49*(10**(-4))*pres_poros

    dens_linha = (dens_0_oleo)/(B_0*(1 + 0.001*RGO))
    cte_9 = ((dens_linha)/(2.6 - dens_linha))**(0.5)
    cte_10 = 4.12*((1.08/dens_linha - 1)**(0.5)) - 1
    v_oleo = 2096*cte_9 - 3.7*temp + 4.64*pres_poros + 0.0115*cte_10*temp*pres_poros
    bulk_oleo_Pa = dens_oleo*(10**3)*((v_oleo)**2)
    bulk_oleo = bulk_oleo_Pa * 10**(-9)
    
    # d) gas
    t_pr = (temp + 273.15) / (94.72 + 170.75*G)
    p_pr = pres_poros / (4.892 - 0.4048*G)
    exp_g = np.exp ( (-(0.45 + 8*((0.56-(1./t_pr))**2))*((p_pr)**(1.2))) / (t_pr) )
    E = 0.109*((3.85 - t_pr)**2)*exp_g
    cte_11 = (0.03 + 0.00527*((3.5 - t_pr)**3))
    Z = cte_11*p_pr + (0.642*t_pr - 0.007*(t_pr**4) - 0.52) + E

    dens_gas = 3.4638657*((G*pres_poros)/(Z*(temp + 273.15)))
    gamma_0 = 0.85 + (5.6/(p_pr + 2)) + (27.1/((p_pr + 3.5)**2)) - 8.7*np.exp(-0.65*(p_pr + 1))
    deriv_Z = cte_11 - (0.1308*((3.85-t_pr)**2)*(0.45 + 8*(0.56 - 1./(t_pr))**2)) * (((p_pr)**(0.2))/(t_pr)) * exp_g  
    #bulk_gas em MPa - nao esquecer de transforma p/ pascal para obter a veloc em m/s 
    bulk_gas_MPa = ((pres_poros*gamma_0)/(1-((p_pr/Z)*(deriv_Z))))   # bulk em MPa
    v_gas = ((bulk_gas_MPa*(10**6))/(dens_gas*1000))**(0.5)          #bulk MPa = 10^6 Pa, densidade g/cm3 = 1000Kg/m3
    bulk_gas = bulk_gas_MPa *10**(-3) 

    bulkNden = np.array([[bulk_salmoura, bulk_oleo, bulk_gas], [dens_salmoura, dens_oleo, dens_gas]])   
    
    return bulkNden
    
def vshGRcalc(gr, grmin, grmax):
    # Finalidade:
    # calculo da argilosidade a partir do perfil de raios gama

    # Entrada:
    # gr - dados de raio gama 
    # grmin - valor minimo de referencia - areia limpa
    # grmax - valor maximo de referencia - folhelho
        
    n = np.size(gr)
    grfa = grmax - grmin
        
    arg = np.empty(np.size(gr))        
        
    for i in np.arange(0, n):
        arg[i] = (gr[i] - grmin)/grfa
        if arg[i] < 0.0:
            arg[i] = 0.0
        if arg[i] >= 1.0:
            arg[i] = 0.98
    
    return arg
    
def ofSimandouxPhiChiSw100(x, resObs, coef, phi, chi):
    # FINALIDADE:
    # calcular o residuo do perfil de resistividade modelado usando a equacao
    # de Simandoux modificada como fc de porosidade e volume de folhelho, considerando 100 %
    # saturado em salmoura.
    #
    # Modelo de resistividade:
        #   Rt = ( phiE**m Sw**n ) / ( a Rw (1-chi) )  + ( chi Sw ) /  Rsh,
    #   com Sw = 1.0
    #
    # ENTRADA:
        # x     - parametros do modelo Simandoux a ser estimados x = [a*Rw Rsh]
        # resObs - dados observados de resistividade
        # coef - coeficientes do modelo de resistividade = [m n]
        # phi - vetor de porosidade efetiva para calculo da funcao
        # chi - vetor de volume de folhelho para calculo da funcao
    
    nPhi = np.size(phi)
    nChi = np.size(chi)
    nObs = np.size(resObs)
    if (nPhi != nChi or nPhi != nObs):
        raise Exception ("Vetores de entrade devem ter as mesmas dimensoes")
    
    T1 = ( (phi**coef[0])*1.0**coef[1])/((1 - chi)*x[0]) 
    T2 = chi/x[1]
    dComp = (T1 + T2)**(-1)
    res = resObs - dComp
    
    return res

def dCompSimandouxPhiChiSw100(phi,chi,facies,coef):
    
    # FINALIDADE:
    # modelar dados calculados usando o modelo de Simandoux modificado como 
    # fc de porosidade e volume de folhelho, considerando 100 % saturado em 
    # salmoura e os coeficientes variando de acordo com as facies litologicas
    # correspondentes ao dados observado.
    #
    # ENTRADA:
        # phi - valor(es) em porosidade para calculo da funcao
        # chi - valor(es) em volume de folhelho para calculo da funcao
        # facies - vetor de indicacao de facies correspondente ao aos dados
        # coef - matrix de coeficientes coeficientes do modelo petrofisico
        #        correspondendo a todas as facies existentes (uma linha para cada
        #        facies)
    
   nPhi = np.size(phi)
   nChi = np.size(chi)
   nObs = np.size(facies)
   nFac = np.size(coef)       
   if (nPhi != nChi):
       raise Exception('Vetores de entrada devem ter as mesmas dimensoes')
   
   dComp = np.zeros((nObs,1))
   
   if (nPhi ==1):
       allFacies = np.arange(1,nFac + 1)    
       indFac = ismember(allFacies, facies)
       for i in np.arange(0, nFac):
           if(indFac(i)):
               ind = np.argwhere(facies == i + 1)
               if (chi >= 1.0):
                   T1 = 0.0
               else:
                   T1 = ( (phi**coef[i][0])*(1.0**coef[i][1]) )/( coef[i][2]*(1-chi) )
               T2 = chi / coef[i][3]
               dComp[ind] = 1.0*(T1 + T2)**(-1)
   elif(nPhi ==nObs):
        for k in np.arange(0,nObs):
            ifac = facies[k][0]
            if (chi[k] >= 1.0):
                T1 = 0.0
            else:
                T1 = ( (phi[k]**coef[ifac - 1][0])*(1.0**coef[ifac - 1][1]) ) / ( (coef[ifac -1 ][2])*(1 - chi[k]) )
            T2 = chi[k] / coef[ifac - 1][3]
            dComp[k][0] = (T1 + T2)**(-1)
            
   return dComp
    
def ismember (A, B):

    nA = np.size(A)
    C = np.empty(nA)    
        
    for i in np.arange(0,nA):
        C[i] = np.any(A[i]==B)
        
    return C    
    
def rsquared(dataComp, dataObs):
    # FINALIDADE:
    # Funcao para medir a qualidade do ajuste entre o modelo e as observacoes,
    # baseado na medida R2. Essa medida da uma ideia da qualidade dos ajuste,
    # atraves da compaparacao com um ajuste pela media. A medida normalmente produz 
    # valores entre 0 e 1 onde zero representa um ajuste igual ao pela media e 1 um
    # ajuste exato. Valores tambem podem ocorrer revelando um ajuste pior que pela
    # media.
    #
    # ENTRADA:
        # dataComp - dados calculados a partir do modelo
        # dataObs  - dados observados
        #
        # SAIDA:
            # R2 - coeficiente R2 de medida da qualidade do ajuste
    
    nobs = np.size(dataObs)
    
    if (nobs != np.size(dataComp)):
        raise Exception ('Verifique as dimensoes dos vetores de entrada na funcao rsquared')
    
    dataMed = np.mean(dataObs)
    s1 = (dataObs - dataMed)**2
    s2 = (dataComp - dataMed)**2
    SST = np.sum(s1)  # total sum of squares or sum of squares about the mean 
    SSR = np.sum(s2)  # sum of squares of the residual
    R2 = SSR/SST
    
    return R2
    
def percentileMatlab (x,p):
    
    xx = np.sort(x)
    m = np.shape(x)[0]
    n = 1
    
    if (m == 1 or n == 1):
        m = np.fmax(m,n)
        if m == 1:
            y = x*np.ones((np.size(p),1))
            return y
        
        n = 1
        q = 100*(np.arange(0.5,m) - 0.5)/m
        xx1 = np.append(np.min(x), xx)
        xx = np.append(xx1, np.max(x))
    else:
        q = 100*(np.arange(0.5,m) - 0.5)/m
        xx1 = np.vstack((np.min(x,0),xx))
        xx = np.vstack((xx1, np.max(x,0)))
    
    q1 = np.append(0,q)
    q = np.append(q1,100)
    fy = scipy.interpolate.interp1d(q,xx)
    y = fy(p)
    
    return y
    
def logInterp (log, z):

    if (np.size(log) != np.size(z)):
        raise Exception ('Nao foi possivel interpolar. Dimensoes de log e z estao diferentes')
    
    if (np.any(log== np.NaN)):
        icut = np.argwhere(log != np.NaN)
        icut= np.squeeze(icut,1)
        zcut = z[icut]
        vcut = log[icut]
        flog = scipy.interpolate.InterpolatedUnivariateSpline (zcut, vcut, k=3)
        logInter = flog(z)
    else:
        logInter = log
    
    return logInter
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    