# Pygame Manager
Pygame Manager é um gerenciador de interfaces para jogos desenvolvidos com Pygame, permitindo a criação modular de telas e eventos com uma estrutura organizada e extensível.

## Recursos
- Modularidade: Registre e gerencie interfaces de forma independente.
- Eventos: Registre os eventos do pygame no formato de decoradores.
- Inicialização Simplificada: Configure o jogo de forma clara e estruturada.

## Instalação
Você deve ter python instalado, assim como o módulo pygame.
Para instalar o pygame execute:
```bash
pip install pygame
```
Para instalar o gerenciador, navegue até a pasta que você deseja e rode o seguinte comando:
```bash
git clone https://github.com/KauanHK/pygame-manager
```

## Inicialização
Crie uma instância de Game
```python
from manager import Game

game = Game()
```
Esse objeto será responsável por executar o jogo e lidar com as trocas de interfaces.
O próximo passo é criar as interfaces e registrá-las.

## Interfaces
Criação de uma interface:
```python
from manager import Interface

interface = Interface('game')
```
O parâmetro **name** é obrigatório. Ele serve para identificar a interface.

Você pode pegar uma determinada interface com **get_interface**.
```python
from manager import get_interface

game_interface = get_interface('game')
```
Isso retorna a instância já criada com o nome '*game*'. Caso não exista nenhuma interface com o nome fornecido, é lançada uma exceção.

## Eventos
Existem duas categorias de eventos:
 - **Eventos de interface**: São executados apenas na interface em que foram registrados.
 - **Eventos globais**: São executados em todas as interfaces.

Um exemplo de evento global seria o de fechar o jogo.
```python
from manager import quit_pygame

@game.event(pygame.QUIT)
def quit():
    quit_pygame()
```
Isso faz com que, em qualquer interface, se houver o evento do tipo **pygame.QUIT**, essa função seja chamada.
A função **quit_pygame** lança a exceção QuitPygame, o que faz com que o gerenciador feche o jogo.
Por padrão, esse evento já é registrado ao criar a instância de **Game**.

Caso você queira implementar algo ao fechar o jogo, crie a instância de **Game** da seguinte forma:
```python
from manager import Game, quit_pygame

game = Game(quit = False)

@game.event(pygame.QUIT)
def quit():
    # Implemente aqui seu código
    quit_pygame()
```
Definir o parâmetro **quit** como False fará com que a função para fechar o jogo não seja criada automaticamente.
Mesmo que o evento de **pygame.QUIT** não esteja definido, você pode fechar o jogo com ctrl+c de forma segura.

### Eventos de interface
Imagine que você deseja trocar de interface quando o usuário clicar em um botão.
```python
import pygame
from manager import switch_interface

interface = Interface('menu')
button_rect = pygame.Rect(350, 400, 220, 100)

@interface.event(pygame.MOUSEBUTTONDOWN, params = ('pos', 'button'))
def click(pos, button):
    if button == pygame.BUTTON_LEFT and button_rect.collidepoint(pos):
        switch_interface('game')
```
Em um evento de click, a função será chamada passando os valores dos atributos **pos** e **button** do evento pygame.
A função **switch_interface** faz com que a interface mude para a especificada no parâmetro **name**.
A verificação do botão e de colisão podem ser passadas diretamente no decorador:
```python
@interface.event(
    pygame.MOUSEBUTTONDOWN,
    button = pygame.BUTTON_LEFT,
    pos = lambda pos: button_rect.collidepoint(pos)
)
def click():
    switch_interface('game')
```
Os kwargs passados se referem aos valores dos atributos do evento pygame. Nesse exemplo, quando houver o evento **pygame.MOUSEBUTTONDOWN**, 
o gerenciador verificará se **pygame_event.button == pygame.BUTTON_LEFT** e se **func(pygame_event.pos) == True**. 
Se todas as verificações forem verdadeiras, a função **click** será executada.

**Passar um atributo em kwargs que o evento pygame não possui poderá causar um erro durante a execução do jogo.** Por exemplo, registrar um evento do 
tipo **pygame.MOUSEBUTTONDOWN** passando o kwarg **key** poderá causar um *AttributeError*.

O gerenciador suporta funções como kwarg em eventos. Elas devem ter exatamente um parâmetro, que é o valor do atributo do evento e devem retornar um valor booleano. 
Caso seja um método, elas devem ter dois parâmetros: A instância (self), e o atributo (attr).

## Eventos em objetos
O gerenciador suporta o registro de métodos para eventos.
```python
interface = get_interface('game')

@interface.register_cls
class Button:

    def __init__(self, text: str, x: int, y: int, command: Callable) -> None:
        ...
        self.command = command
        self.rect = pygame.Rect(x, y, *self.image.get_size())

    @interface.event(
        pygame.MOUSEBUTTONDOWN,
        button = pygame.BUTTON_LEFT,
        pos = lambda self, pos: self.rect.collidepoint(pos)
    )
    def click(self) -> None:
        self.command()
```
A classe *Button* é registrada na interface com o decorador **interface.register_cls**, o  que faz com que todos os eventos dessa classe sejam tratados como instâncias dessa classe.
Neste exemplo, quando houver um evento de click com o botão esquerdo do mouse e o rect da instância colidir com a posição do mouse, será chamada o método **Button.click** 
passando a sua instância como primeiro parâmetro.

## Frame
Para registrar um frame, use o decorador **Game.frame** ou **Interface.frame**. Assim como os eventos, ele pode ser global ou de interface. 
A função do frame deve receber a tela do jogo como primeiro parâmetro.
### Frame de interface
```python
@interface.frame
def frame(screen: pg.Surface) -> None:
    screen.fill((0, 0, 0))
    for button in buttons:
        button.draw(screen)
```
### Frame global
```python
@game.frame
def frame(screen: pg.Surface) -> None:
    screen.fill((0, 0, 0))
```
O gerenciador executa primeiro os eventos e frames globais. A lógica é parecida com essa:
```python
while True:
    for event in pygame.event.get();
        run_global_event(event)
        run_interface_event(event)
    run_global_frame()
    run_interface_frame()
    clock.tick(fps)
    pg.display.flip()
```
