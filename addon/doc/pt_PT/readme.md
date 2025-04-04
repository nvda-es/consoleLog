## Manual do extra do visualizador da consola do Windows
##Introdução

Este extra facilita a visualização do conteúdo das consolas do Windows por meio de uma caixa de diálogo interativa. É uma ferramenta válida para qualquer janela da consola do Windows, permitindo fácil navegação e opções de pesquisa integradas.

## Configuração inicial
### Atribuição de comando

Para usar este extra,  precisa atribuir uma combinação de teclas que invocará a caixa de diálogo do visualizador da consola.  pode fazer isso no seguinte caminho:

```
NVDA > Preferências > Definir comandos > Visualizador da consola > Mostrar Visualizador da consola 
```

### Restrições

* Apenas uma caixa de diálogo pode ser aberta de cada vez.
* A caixa de diálogo só pode ser invocada quando uma janela da consola do Windows estiver em foco.

## Funcionalidades de diálogo
### Navegação

* Use as teclas do cursor para navegar pelo conteúdo.
* Pressione `F1` para obter a linha e posição atual do cursor.

###Procurar

* `Ctrl + F`: Abre uma caixa de diálogo de pesquisa.
* `F3`: Mostra uma caixa de diálogo de pesquisa. Se uma pesquisa já tiver sido realizada anteriormente, irá procurar o seguinte resultado.
* `Shift + F3`: pesquisa o resultado anterior da pesquisa.
* As pesquisas não diferenciam maiúsculas de minúsculas e podem ser realizadas em palavras exatas ou fragmentos de palavras.
* Cada pesquisa bem-sucedida emitirá um som de “bipe” indicando que o cursor está agora na próxima palavra encontrada.

### Menu rápido

Acesso rápido ao menu com `Alt + R`, onde  encontrará as seguintes opções:

*Procurar
* Guardar  o conteúdo da consola num ficheiro
*Sair da consola

### Sair da caixa de diálogo

* `Alt + F4` ou `Escape`: Fecha a caixa de diálogo.

## Atualização de conteúdo

Se  abrir uma caixa de diálogo e a consola for atualizada,  terá que fechar a caixa de diálogo e invocá-la novamente para ver as atualizações.

## consolas comuns do Windows

No Windows, existem várias consolas ou terminais que  pode usar para executar comandos e scripts. Aqui está uma lista das consolas mais comuns:

1. **CMD** (Prompt de Comando): Esta é uma consola baseada em texto para executar comandos e scripts em lote.
   
2. **PowerShell**: É uma consola avançada que permite a automação de tarefas através de scripts. Oferece mais recursos do que o CMD tradicional.
   
3. **Terminal Windows**: É um aplicativo moderno que permite acesso a múltiplas consolas, como PowerShell, CMD e consola Linux (através do Subsistema Windows para Linux).
   
4. **Bash** (através do subsistema Windows para Linux): Permite executar um ambiente Linux dentro do Windows, permitindo o uso de comandos e aplicativos do Linux.

> **Nota**:  pode acessar essas consolas através do menu Iniciar do Windows ou através da pesquisa do Windows digitando o nome da consola que deseja usar.

##Registo de alterações.
###Versão 1.3.

* O suporte ao Terminal Windows foi adicionado.

Esta função está sendo testada.

No momento nos testes realizados extrai corretamente o texto e mostra-o para poder ser visualizado confortavelmente num diálogo e poder trabalhar com ele.

Esta nova função é adicionada ao visualizador das consolas cmd, powershell e bash usando a mesma combinação de teclas que adicionamos ao extra.

Ao pressionar esta combinação, o extra detectará em que tipo de consola nos concentramos e agirá de acordo.

###Versão 1.2.

* Corrigido erro crítico de negação de permissões do Windows 10 (código 5).

* O idioma e a documentação turcos (Umut KORKMAZ) foram adicionados.

* Adicionada detecção de consola sem texto.

###Versão 1.1.

* Correções de bugs em strings traduzíveis.

* Adicionado idioma inglês com tradução automática.

###Versão 1.0.

* Versão inicial.)

### Tradução Portuguesa

Ângelo Abrantes e Rui Fontes (30-05-2024)