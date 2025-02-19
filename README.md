# Pygame Manager 🎮

Um sistema modular de gerenciamento de interfaces para Pygame, projetado para simplificar o desenvolvimento de jogos com telas independentes, tratamento de eventos e arquitetura organizada.

![Versão Pygame](https://img.shields.io/badge/pygame-2.5.2-blue)
[![Licença](https://img.shields.io/badge/licença-MIT-green)](https://github.com/KauanHK/pygame-manager/blob/main/LICENSE)

## Recursos ✨
- **Interfaces Modulares**: Crie telas independentes com lógica própria
- **Decoradores de Eventos**: Registre eventos do Pygame com sintaxe intuitiva
- **Sistema Hierárquico**: Relações pai/filho entre interfaces para UIs complexas
- **Componentes Baseados em Classes**: Crie elementos reutilizáveis facilmente
- **Gerenciamento de Grupos**: Controle eventos em múltiplas interfaces
- **Renderização de Telas**: Sistema de desenho simplificado com atualização automática

---

## Instalação 📦

### Pré-requisitos
- Python 3.8+
- Pygame 2.5.2+

```bash
# Instale o Pygame primeiro
pip install pygame

# Instale o Pygame Manager
pip install git+https://github.com/KauanHK/pygame-manager
```

---

## Começo Rápido 🚀

### Configuração Básica
```python
from pygame_manager import Game, Interface, quit_pygame
import pygame

# Inicializa o gerenciador do jogo
game = Game(fps=60)

# Cria interface principal
main_menu = Interface(name='menu_principal')

@main_menu.frame
def desenhar_fundo(screen):
    screen.fill((30, 30, 30))

@main_menu.event(pygame.KEYDOWN, key=pygame.K_SPACE)
def iniciar_jogo():
    print("Jogo iniciando!")

 game.register_interface(main_menu)
 main_menu.activate()
 game.run(pygame.display.set_mode((800, 600)))
```

---

## Conceitos Principais 🔧

O Pygame Manager faz o gerenciamento das interfaces do jogo. 
As interfaces facilitam o desenvolvimento modular de diferentes telas 
e o tratamento dos eventos. Elas podem ter:
- **Subinterfaces**: Interfaces que são rodadas por cima da interface pai, 
como um popup.
- **Frames**: A renderização da interface na tela.
- **Eventos**: Possui seus próprios eventos de maneira independente.

### 1. Interfaces

Para criar uma interface, basta import `Interface` e dar um nome a ela. 
Esse nome é deve ser único e não pode ser alterado.

```python
from pygame_manager import Interface

interface_jogo = Interface(name='jogo')
menu_pausa = Interface(name='menu_pausa')

# Registra interface filha
interface_jogo.register_interface(menu_pausa)
```

#### Ativação de Interfaces

A interface deve ser ativada para ser executada. 
Use `interface.activate()` ou `activate_interface(interface)`

```python
def alternar_pausa():
    if menu_pausa.active:
        menu_pausa.deactivate()  # Você também pode usar deactivate('menu_pausa')
    else:
        menu_pausa.activate()  # Ou activate('menu_pausa')
```
### Como funciona `activate()/deactivate()`
- Ativa/desativa uma interface específica diretamente.  
- Não afeta outras interfaces  
- **Permitem sobreposição**: Você pode ter múltiplas interfaces ativas simultaneamente (útil para popups, menus em camadas).

---

### Como funciona **`switch_interface()`**  
- **Troca global de contexto**: Desativa **todas** as interfaces ativas e ativa apenas a especificada.  
- **Uso típico**: Transições entre telas principais (ex: menu → jogo, jogo → game over).

**Note:** `switch_interface()` lança uma exceção, portanto use no **final** de sua função para que toda ela seja executada.


#### Exemplo Prático:

```python
@menu.event(pygame.KEYDOWN, key = pygame.K_ESCAPE)
def retornar_menu():
   ...
   switch_interface('menu_principal')  # Executado no final da função
```

2. **`switch_interface()`**:  
   - Transições entre estados globais (ex: tela inicial → novo jogo).  
   - Resetar o estado do jogo (ex: voltar ao menu após game over).  
   ```python
   # Exemplo: Iniciar novo jogo
   def iniciar_novo_jogo():
       switch_interface('jogo')
   ```

---

### 2. Tratamento de Eventos

#### Registro Básico de Eventos

Os eventos devem ser registrados em interfaces. Para registrar um evento 
global, registre-o na instância de Game. O evento recebe o tipo do evento pygame, 
os parâmetros que devem ser passados para a função, e kwargs.

```python
@interface.event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
def tratar_escape():
    alternar_pausa()
```

#### Componentes Baseados em Classes

Para criar eventos em métodos, é necessário registrar a classe. 
Dessa forma, o evento será chamado para as instâncias da classe.

```python
@interface.register_cls
class Jogador:
    def __init__(self):
        self.rect = pygame.Rect(100, 100, 50, 50)
    
    @interface.event(pygame.KEYDOWN, key=pygame.K_d)
    def mover_direita(self):
        self.rect.x += 10
```

---

### 3. Gerenciamento de Grupos 🎚️

Gerencie eventos que devem funcionar em múltiplas interfaces.

### Como Funcionam os Grupos?
1. **Associação de Interfaces**: Vincule interfaces ao criar o grupo
2. **Processamento**: Os eventos só serão executados nas interfaces do grupo que estiverem ativas.

### Exemplo Prático:
```python
from pygame_manager import Group
import pygame

# Grupo contendo menu principal e game over
grupo_ui = Group('menu_principal', 'game_over')

@grupo_ui.register_cls
class Botao:
    def __init__(self, interface, texto, posicao):
        self.interface = interface
        self.rect = pygame.Rect(posicao[0], posicao[1], 200, 50)
        self.texto = texto

    @grupo_ui.event(
        pygame.MOUSEBUTTONDOWN,
        button=pygame.BUTTON_LEFT,
        pos=lambda self, pos: self.rect.collidepoint(pos)
    )
    def click(self):
        print(f"Botão {self.texto} pressionado!")

# Criação dos botões
botao_menu = Botao('menu_principal', "Novo Jogo", (100, 200))
botao_game_over = Botao('game_over', "Reiniciar", (100, 300))
```

### Comportamento em Diferentes Estados:
| Estado da Interface      | Botão do Menu | Botão do Game Over |
|--------------------------|---------------|--------------------|
| **Menu Principal Ativo** | ✅ Funciona    | 🚫 Não existe      |
| **Jogo Ativo**           | 🚫 Inativo    | 🚫 Inativo         |
| **Game Over Ativo**      | 🚫 Não existe | ✅ Funciona        |

### 4. Renderização de Telas
```python
@interface.frame
def renderizar_jogo(screen):
    # Lógica de desenho personalizada
    pygame.draw.circle(screen, (255, 0, 0), (400, 300), 30)
```

---

## Encerramento seguro

A instância de Game, por padrão, registra um evento de saída do jogo. 
O pygame será sempre fechado corretamente, mesmo que uma exceção ocorra.

### Controle Personalizado de Saída

Se quiser definir uma função para fechar o jogo, crie a instância de Game 
passando o parâmetro `quit = False`

```python
game = Game(quit=False)  # Desativa o tratamento padrão de saída

# Você pode registrar mais de um evento para a mesma função
@game.event(pygame.QUIT)
@game.event(pygame.KEYDOWN, key=pygame.K_q)
def saida_personalizada():
    print("Salvando estado do jogo...")
    quit_pygame()
```
**Note:** Somente uma função de saída do jogo pode ser registrada.

---

## Estrutura de Exemplo 📂

```
meu_jogo/
├── main.py
├── interfaces/
│   ├── __init__.py
│   ├── menu.py
│   ├── jogo.py
│   └── pausa.py
└── componentes/
    ├── jogador.py
    └── elementos_ui.py
```

---

## Contribuição 🤝

Contribuições são bem-vindas! Siga estes passos:
1. Faça um fork do repositório
2. Crie uma branch de funcionalidade (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request
