# AI Agent Customization Guide for Biblioteca (Book Management System)

## Project Overview

**Sistema de Biblioteca** is a desktop point-of-sale application for bookstore management. It features:
- Book inventory management with pricing (purchase vs. retail)
- Customer and vendor relationship management
- Sales transaction processing with multiple payment methods (PIX, debit, credit, cash)
- Automatic stock deduction on sales
- Employee/seller tracking
- Windows installer deployment (Inno Setup)

**Tech Stack**: Python 3.x, Tkinter + ttkbootstrap (cosmo theme), SQLite3, PyInstaller

---

## Project Architecture

### Directory Structure

```
models/           # Business logic models (CRUD operations)
  ├── livro.py          # Book catalog management
  ├── cliente.py        # Customer management
  ├── fornecedor.py     # Supplier/vendor management
  ├── vendedor.py       # Employee/seller management
  └── venda.py          # Sales transaction logic

database.py       # SQLite persistence layer
main.py          # Tkinter GUI entry point
atualizar_banco.py # Database maintenance/reset utility
create_icons.py   # Icon generation for payment methods
build/           # PyInstaller build artifacts
images/          # Payment method icons (PIX, debit, credit, cash)
```

### Design Pattern: MVC-Inspired

- **Models** (`models/`): Business logic with CRUD operations
- **Database** (`database.py`): ORM-like persistence layer (raw SQLite3)
- **View** (`main.py`): Tkinter GUI with ttkbootstrap styling
- **Data Flow**: GUI → Models → Database → Models → GUI

---

## Code Conventions & Patterns

### Return Tuples (Standard Pattern)
All model methods return tuples for consistent error handling:
```python
(success_bool, message)                    # Query operations
(success_bool, resource_id, message)       # Create operations
```

### SQL Queries
- Use **parameterized statements** to prevent SQL injection: `?` placeholders
- All timestamps: `datetime.now().isoformat()`
- Foreign key constraints enforced between `vendas`, `itens_venda`, and `livros`

### Naming Conventions
- **Portuguese names** for UI elements, variables, and strings (e.g., `livro`, `venda`, `cliente`, `fornecedor`)
- Database tables also in Portuguese (e.g., `clientes`, `vendas`, `itens_venda`)
- Method names in English or Portuguese (mix is acceptable)

### Error Handling
All database operations wrapped in try/except:
```python
try:
    # database operation
except sqlite3.Error as e:
    return (False, f"Erro ao [action]: {str(e)}")
```

### Asset Paths (PyInstaller Compatibility)
Check for bundled execution:
```python
if getattr(sys, '_MEIPASS', None):
    # Running as frozen executable
    asset_path = os.path.join(sys._MEIPASS, 'images')
else:
    # Running as script
    asset_path = 'images'
```

---

## Database Schema Overview

### Core Tables
| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `clientes` | Customers | name, email, phone, address |
| `livros` | Book inventory | title, author, ISBN, qty, purchase_price, retail_price, supplier_id |
| `fornecedores` | Suppliers/vendors | name, CNPJ, email, phone, address |
| `vendedores` | Employees/sellers | name |
| `vendas` | Sales transactions | vendor_id, customer_id, status, total, payment_method, created_at |
| `itens_venda` | Sale line items | sale_id, book_id, qty, price |
| `inventario_historico` | Audit trail | (schema partially implemented) |

### Key Constraints
- Sales status flow: `'aberto'` (open) → completed states
- Inventory auto-decrements when items added to sales
- Foreign keys enforced between `vendas`, `itens_venda`, and `livros`

---

## UI/UX Patterns

### Styling
- **Framework**: Tkinter with ttkbootstrap (cosmo theme by default)
- **Button Styles**: Primary, secondary, success, info, warning, danger, light, dark
- **Icons**: 64x64 PNG images in `images/` folder for payment methods
- **Fallback**: Emoji characters if image assets missing

### Feature Implementation Guides
Detailed specifications for common UI improvements in feature README files:
- [README_ADICIONAR_LIVRO.md](README_ADICIONAR_LIVRO.md) - Book addition form redesign
- [README_FINALIZAR_VENDA.md](README_FINALIZAR_VENDA.md) - Payment screen improvements
- [README_BOTAO_VOLTAR_VENDAS.md](README_BOTAO_VOLTAR_VENDAS.md) - Back button in dialogs
- [README_INCLUIR_LIVRO_RAPIDO.md](README_INCLUIR_LIVRO_RAPIDO.md) - Quick book inclusion feature

---

## Deployment & Build

### Creating Standalone Executable
**Configuration**: [main.spec](main.spec) (PyInstaller spec file)
- Bundles `images/` folder into .exe
- Hides console window
- Detects bundled vs. script execution automatically

**Command**: `pyinstaller main.spec`

### Creating Windows Installer
**Configuration**: [Setup.iss](Setup.iss) (Inno Setup installer script)
- Generates `InstaladorLivraria.exe` installer
- Supports Portuguese and English
- Version: 1.5+

### Database Utilities
- **atualizar_banco.py**: Clears all sales/inventory data (⚠️ destructive). Requires "SIM" confirmation.
- **create_icons.py**: Regenerates payment method icons using PIL (PIX green, debit blue, credit purple, cash dark green)

---

## Development Workflow

### Adding a New Feature
1. **In Models**: Create/update CRUD methods in `models/`
2. **In Database**: Ensure schema supports new fields/relationships
3. **In GUI**: Add UI elements to `main.py` using ttkbootstrap patterns
4. **In Assets**: Add icons to `images/` if needed (64x64 PNG)
5. **Document**: Add feature spec as `README_FEATURE_NAME.md` if complex

### Modifying a Model
1. Update method in `models/{model}.py`
2. Test with tuple return pattern: `(bool, id/msg)`
3. Update database.py if schema changes needed
4. Test PyInstaller compatibility with `_MEIPASS` checks

### Debugging
- **GUI Issues**: Check `main.py` theme/style definitions and ttkbootstrap version
- **Database**: Verify foreign keys and parameterized queries in `database.py`
- **PyInstaller**: Ensure all imports are explicit (no dynamic `__import__`); test with `main.spec`
- **Installers**: Inno Setup logs in `.iss` file output directory

---

## Common Gotchas & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Icons missing in frozen exe | Asset path detection fails | Verify `_MEIPASS` check in main.py matches bundled structure |
| Database locked errors | Concurrent access during PyInstaller run | Exclude database files from build; recreate on first run |
| Portuguese characters broken | Encoding mismatch | Use `.isoformat()` for all timestamps; ensure UTF-8 encoding |
| Theme not applying | ttkbootstrap version mismatch | Check `main.py` for theme name (cosmo, flatly, etc.) |

---

## Useful Commands

```bash
# Run application
python main.py

# Create Windows executable
pyinstaller main.spec

# Regenerate payment icons
python create_icons.py

# Reset database (destructive)
python atualizar_banco.py

# Create Windows installer (requires Inno Setup installed)
iscc Setup.iss
```

---

## When to Ask for Clarification

- **Portuguese terminology**: Ask user for context if business domain terms are unclear
- **UI/UX decisions**: Confirm with user if changing existing UI patterns or theme
- **Database schema changes**: Verify backward compatibility and migration path
- **Deployment targets**: Confirm OS versions and installer requirements

