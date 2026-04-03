from PIL import Image, ImageDraw, ImageFont
import os

# Criar diretório se não existir
os.makedirs('images', exist_ok=True)

def create_payment_icon(text, filename, color=(70, 130, 180)):
    # Criar imagem 64x64
    img = Image.new('RGB', (64, 64), color='white')
    draw = ImageDraw.Draw(img)

    # Desenhar um retângulo arredondado
    draw.rounded_rectangle([5, 5, 59, 59], fill=color, radius=10)

    # Tentar usar uma fonte, se não conseguir usar default
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Calcular posição do texto para centralizar
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (64 - text_width) // 2
    y = (64 - text_height) // 2

    # Desenhar texto em branco
    draw.text((x, y), text, fill='white', font=font)

    # Salvar imagem
    img.save(f'images/{filename}')
    print(f'Imagem {filename} criada com sucesso!')

# Criar ícones para cada método de pagamento
create_payment_icon('PIX', 'pix.png', (0, 150, 136))  # Verde
create_payment_icon('DEB', 'debito.png', (33, 150, 243))  # Azul
create_payment_icon('CRE', 'credito.png', (156, 39, 176))  # Roxo
create_payment_icon('$$$', 'dinheiro.png', (76, 175, 80))  # Verde escuro

print('Todas as imagens foram criadas!')