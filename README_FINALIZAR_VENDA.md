# Sistema de Biblioteca - Tela de Finalizar Venda

## Melhorias Implementadas

### 1. Design Responsivo
- A tela agora usa layout fluido com canvas e scrollbar
- Ajusta-se automaticamente ao tamanho da janela
- Tamanho mínimo definido para garantir usabilidade
- Botão "Confirmar Pagamento" sempre visível

### 2. Imagens nos Métodos de Pagamento
- Cada método de pagamento agora tem uma imagem associada
- Imagens são carregadas automaticamente na inicialização
- Fallback para emojis se as imagens não forem encontradas

## Estrutura de Arquivos

```
biblioteca/
├── images/
│   ├── pix.png          # Ícone para PIX
│   ├── debito.png       # Ícone para Cartão de Débito
│   ├── credito.png      # Ícone para Cartão de Crédito
│   └── dinheiro.png     # Ícone para Dinheiro
├── create_icons.py      # Script para gerar ícones básicos
└── main.py             # Aplicação principal
```

## Personalização das Imagens

### Substituindo Imagens
1. Coloque suas imagens na pasta `images/`
2. Mantenha os nomes dos arquivos: `pix.png`, `debito.png`, `credito.png`, `dinheiro.png`
3. Use imagens PNG com fundo transparente para melhor aparência
4. Tamanho recomendado: 64x64 pixels (serão redimensionadas automaticamente)

### Criando Novas Imagens
Execute o script `create_icons.py` para gerar ícones básicos:
```bash
python create_icons.py
```

### Modificando Cores e Textos
Edite o script `create_icons.py` para personalizar:
- Cores dos ícones
- Textos exibidos
- Tamanhos das imagens

## Funcionalidades

- **Layout Responsivo**: A tela se adapta a diferentes tamanhos
- **Scroll Automático**: Barra de rolagem aparece quando necessário
- **Imagens Visuais**: Cada método de pagamento tem representação visual
- **Fallback Seguro**: Emojis são usados se imagens falharem ao carregar
- **Botão Sempre Visível**: O botão de confirmação nunca fica oculto

## Requisitos do Sistema

- Python 3.6+
- Tkinter (incluído no Python)
- Pillow (PIL) para manipulação de imagens
- tkcalendar para calendários

Instale as dependências:
```bash
pip install Pillow tkcalendar
```