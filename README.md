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

### 1. Gerenciamento de Interfaces

#### Criando Interfaces
```python
from pygame_manager import Interface

interface_jogo = Interface(name='jogo')
menu_pausa = Interface(name='menu_pausa')

# Registra interface filha
interface_jogo.register_interface(menu_pausa)
```

#### Ativação de Interfaces
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

#### Exemplo Prático:
```python
interface_jogo.activate()       # Interface do jogo principal
menu_pausa.activate()           # Adiciona menu de pausa por cima
```
**Resultado**: Ambas as interfaces estarão ativas e processando eventos e draws.

---

### Como funciona **`switch_interface()`**  
- **Troca global de contexto**: Desativa **todas** as interfaces ativas e ativa apenas a especificada.  
- **Uso típico**: Transições entre telas principais (ex: menu → jogo, jogo → game over).  
- **Funcionamento interno**:
  1. Lança a exceção `SwitchInterface` com o nome da interface alvo.
  2. O bloco `try` em `run_event` captura a exceção.
  3. **Desativa todas as interfaces** (`it.deactivate()` no loop).
  4. **Ativa apenas a interface alvo** (se existir).

#### Exemplo Prático:
```python
switch_interface('menu_principal')  # Desativa todas interfaces e ativa o menu
```

---

### Diferença Chave ✨
| Característica          | `activate()`/`deactivate()` | `switch_interface()`          |
|-------------------------|-----------------------------|-------------------------------|
| **Escopo**              | Interface específica        | Todas as interfaces           |
| **Sobreposição**        | Permite                    | Desativa tudo antes de ativar |
| **Casos de Uso**        | Popups, submenus           | Troca de telas principais     |
| **Controle de Estado**  | Manual                     | Automático (global)           |

---

### Quando Usar Cada Um?
1. **`activate()`**:  
   - Adicionar elementos temporários (ex: diálogo de confirmação).  
   - Sistemas de pause/menus sobrepostos.  
   ```python
   # Exemplo: Pausar o jogo sem fechá-lo
   def toggle_pause():
       if menu_pausa.active:
           menu_pausa.deactivate()
       else:
           menu_pausa.activate()
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
```python
@interface.event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
def tratar_escape():
    alternar_pausa()
```

#### Componentes Baseados em Classes
```python
@interface.register_cls
class Jogador:
    def __init__(self):
        self.rect = pygame.Rect(100, 100, 50, 50)
    
    @interface.event(pygame.KEYDOWN, key=pygame.K_d)
    def mover_direita(self):
        self.rect.x += 10
```

Entendi perfeitamente! Vou reescrever essa seção com uma explicação precisa do funcionamento dos grupos:

---

## 3. Gerenciamento de Grupos 🎚️

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

## Uso Avançado 🧠

### Transição Entre Interfaces
```python
from pygame_manager import switch_interface

@interface.register_cls
class Botao:
    def __init__(self, interface_alvo):
        self.alvo = interface_alvo
    
    @interface.event(
        pygame.MOUSEBUTTONDOWN,
        button=pygame.BUTTON_LEFT,
        pos=lambda self, pos: self.rect.collidepoint(pos)
    )
    def navegar(self):
        switch_interface(self.alvo)
```

### Controle Personalizado de Saída
```python
game = Game(quit=False)  # Desativa o tratamento padrão de saída

# Você pode registrar mais de um evento para a mesma função
@game.event(pygame.QUIT)
@game.event(pygame.KEYDOWN, key=pygame.K_q)
def saida_personalizada():
    print("Salvando estado do jogo...")
    quit_pygame()
```

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
