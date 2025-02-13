# Pygame Manager
Pygame Manager é um gerenciador de interfaces para jogos desenvolvidos com Pygame, permitindo a criação modular de telas e eventos com uma estrutura organizada e extensível.

## Recursos
- Modularidade: Registre e gerencie interfaces de forma independente.
- Eventos: Vincule eventos específicos a métodos de classes.
- Ciclo de Atualização: Organize a lógica de atualização e renderização de forma intuitiva.
- Inicialização Simplificada: Configure o jogo de forma clara e estruturada.

## Funcionamento
Crie uma instância de Game
```python
from manager import Game

game = Game()
```
Esse objeto será responsável por executar o jogo e lidar com as trocas de interfaces.
O próximo passo é criar as interfaces e registrá-las.

### Criando uma Interface
```python
from manager import Interface

interface = Interface('game')
```
O parâmetro 'name' é obrigatório. Ele serve para identificar a interface.

Você pode pegar uma determinada interface com 'get_interface'.
```python
from manager import get_interface

game_interface = get_interface('game')
```
Isso retorna a instância já criada com o nome 'game'. Caso não exista nenhuma interface com o nome fornecido, é lançada uma exceção.

### Eventos
Existem duas categorias de eventos:
 - Eventos de interface: São executados apenas na interface em que foram registrados.
 - Eventos globais: São executados em todas as interfaces.

Um exemplo de evento global seria o de fechar o jogo.
```python
from manager import QuitPygame

@game.event(pygame.QUIT)
def quit_pygame():
    raise QuitPygame()
```
Isso faz com que, em qualquer interface, se houver o evento do tipo 'pygame.QUIT', essa função seja chamada.
O gerenciador fechará o jogo ao ser lançada a exceção 'QuitPygame'.
Por padrão, esse evento já é registrado ao criar a instância de 'Game'.

Caso você queira implementar algo ao fechar o jogo, crie Game da seguinte forma:
```python
game = Game(quit = False)

@game.event(pygame.QUIT)
def quit_pygame():
    # Implemente aqui seu código
    raise QuitPygame()
```
Isso fará com que a função para fechar o jogo não seja criada automaticamente.

OBS: Você pode fechar o jogo com ctrl+c de forma segura, pois o gerenciador fechará o pygame se uma exceção ocorrer.

### Eventos de interface
Um exemplo seria um botão. Você deseja trocar de interface quando o usuário clicar nele.
```python
import pygame
from manager import SwitchInterface

interface = Interface('menu')
button_rect = pygame.Rect(350, 400, 220, 100)

@interface.event(pygame.MOUSEBUTTONDOWN, ('pos', 'button'))
def click(pos, button):
    if button == pygame.BUTTON_LEFT and button_rect.collidepoint(pos):
        raise SwitchInterface('game')
```
Em um evento de click, a função será chamada passando os valores dos atributos 'pos' e 'button' do evento pygame.
A verificação do botão e de colisão podem ser passadas diretamente no decorador:
```python
@interface.event(pygame.MOUSEBUTTONDOWN, button = pygame.BUTTON_LEFT, pos = lambda pos: button_rect.collidepoint(pos))
def click():
    raise SwitchInterface('game')
```
