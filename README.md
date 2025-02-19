# Pygame Manager
Pygame Manager é um gerenciador de interfaces para jogos desenvolvidos com Pygame, permitindo a criação modular de telas e eventos com uma estrutura organizada e extensível.

## Recursos
- Modularidade: Crie interfaces de forma independente e flexível.
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
Caso queira usar no seu projeto, instale com o pip:
```bash
pip install git+https://github.com/KauanHK/pygame-manager
```

## Interfaces
Criação de uma interface:
```python
from pygame_manager import Interface

interface = Interface('example')
```
O parâmetro **name** é obrigatório. Ele serve para identificar a interface e não pode ser alterado.

Você pode pegar uma determinada interface com **get_interface**.
Isso evita dores de cabeça com 'circular import' caso use a interface em diferentes módulos.
```python
from pygame_manager import get_interface

example_interface = get_interface('example')
```
Isso retorna a instância já criada com o nome '*game*'. 
Caso não exista nenhuma interface com o nome fornecido, lança uma exceção.

### Subinterfaces
Você pode registrar subinterfaces. 
Em um jogo que mostra um popup de game over quando o jogador perde 
pode registrar esse popup como uma subinterface.
```python
game = Interface('game')
game_over = Interface('game_over')

game.register_interface(game_over)

def collided_wall():
    if player.collide_wall():
        game_over.activate()
```
Nesse exemplo, quando o player colidir com uma parede, 
a subinterface game_over será ativada.

## Eventos
Os eventos são registrados nas interfaces.

Para registrar um evento de pressionamento de uma tecla:
```python
import pygame
from pygame_manager import get_interface

example_interface = get_interface('example')
rect = pygame.Rect(200, 400, 50, 50)

@example_interface.event(pygame.KEYDOWN, key = pygame.K_RIGHT)
def move():
    rect.x += 5
```
Essa função será executada sempre que **example_interface** estiver ativa e 
houver o evento de pressionamento da tecla para a direita.

Para dar mais funcionalidades a esse *rect*, vamos criar uma classe. 
Ela terá eventos que dependem do parâmetro **self** para funcionar corretamente. 
Por isso, ao criar classes com eventos, essa classe deve ser registrada 
com o decorador .register_cls().
```python
import pygame
from pygame_manager import get_interface

interface = get_interface('example')

@interface.register_cls
class Rect:
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.vy = 0
        self.gravity = 0.2
        self.floor = 500

    @interface.event(pygame.KEYDOWN, key = pygame.K_SPACE)
    def jump(self):
        self.vy = -10
    
    def update(self):
        self.rect.y += self.vy
        if self.rect.y > self.floor:
            self.rect.y = self.floor
            self.vy = 0
        else:
            self.vy += self.gravity

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
```
O método *.jump()* será executado para todas as instâncias de Rect.

Se você criar um botão, somente um botão será clicado por vez. 
Para diferenciar os botões, você pode passar uma função nos kwargs do decorador do evento:
```python
import pygame
from pygame_manager import get_interface

interface = get_interface('example')

@interface.register_cls
class Button:
    
    def __init__(self, command, *args):
        self.command = command
        self.rect: pygame.Rect
        ...
    
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

Vamos passar o comando para o botão trocar de interface.
```python
from pygame_manager import switch_interface

button = Button(lambda: switch_interface('menu'))
```
A função **switch_interface()** desativa a interface atual e todas as suas subinterfaces 
e ativa a interface indicada.

## Group
Você pode agrupar interfaces para registrar eventos nelas.

Para registrar a classe *Button* em múltiplas interfaces, siga esta estrutura:
```python
from pygame_manager import Group

group = Group('game_over', 'menu')

@group.register_cls
class Button:
    ...
    @group.event(
        pygame.MOUSEBUTTONDOWN,
        button = pygame.BUTTON_LEFT,
        pos = lambda self, pos: self.rect.collidepoint(pos)
    )
    def click(self):
        self.command()
```
Só serão executados os eventos das interfaces do grupo que estiverem ativas.

## Frame
Para registrar um frame, use o decorador **Game.frame** ou **Interface.frame**. Assim como os eventos, ele pode ser global ou de interface. 
A função do frame deve receber a tela do jogo como primeiro parâmetro.

É executado apenas nessa interface e somente se ela estiver ativa.
```python
@interface.frame
def frame(screen: pygame.Surface) -> None:
    screen.fill((0, 0, 0))
    for button in buttons:
        button.draw(screen)
```

## Inicialização
Crie uma instância de Game, o gerenciador do jogo. 
Ele executa e gerencia as interfaces.
```python
from pygame_manager import Game

game_manager = Game()
```
Caso você queira registrar um evento para fechar o jogo 
em qualquer interface quando o usuário pressionar a tecla *esc*, 
use a instância de game:
```python
import pygame
from pygame_manager import quit_pygame

@game_manager.event(pygame.KEYDOWN, key = pygame.K_ESCAPE)
def close_game():
    quit_pygame()
```
A função **quit_pygame** lança a exceção **QuitPygame** para o gerenciador. 
Se uma exceção ocorrer durante o programa, o pygame é fechado. 
Você pode registrar quantos eventos quiser de cada tipo, com exceção de **pygame.QUIT**, 
pois o jogo será fechado imediatamente.

Por padrão, a instância de Game registra um evento para fechar o jogo. 
Se essa não for sua intenção, crie Game passando **quit = False**
```python
game = Game(quit = False)

@game.event(pygame.QUIT)
def quit():
    # Implemente aqui seu código
    quit_pygame()
```

Antes de executar o jogo, você deve registrar todas as interfaces. 
Supondo que cada interface foi criada em um módulo e que podem acontecer error, 
use Game.pygame_init() para inicializar de maneira segura. 
```python
game_manager = Game(fps = 60)
with game_manager.pygame_init():
    from . import game, menu, options
   
    game_manager.register_interface(game.interface)
    game_manager.register_interface(menu.interface)
    game_manager.register_interface(options.interface)
    
    menu.interface.activate()
    game_manager.run(pygame.display.set_mode((900, 720)))
```
Não se esqueça de registrar as subinterfaces nas interfaces e 
de ativar ao menos uma interface.
