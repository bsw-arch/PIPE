# Neovim Configuration for BSW-Arch AI Development Platform

This Neovim configuration integrates with the BSW-Arch AI Development Platform, providing spec-driven development with AI assistance.

## Features

- ✅ LSP support (Python, Lua, Bash, YAML)
- ✅ Knowledge Graph integration
- ✅ MCP server integration
- ✅ Spec-aware commands
- ✅ Impact analysis
- ✅ Fuzzy finding (Telescope)
- ✅ Git integration
- ✅ Syntax highlighting (Treesitter)
- ✅ Auto-completion

## Installation

### 1. Prerequisites

```bash
# Install Neovim (>= 0.9.0)
# Ubuntu/Debian
sudo apt install neovim

# Fedora
sudo dnf install neovim

# macOS
brew install neovim
```

### 2. Install Configuration

```bash
# Backup existing config
mv ~/.config/nvim ~/.config/nvim.backup

# Create config directory
mkdir -p ~/.config/nvim

# Copy configuration
cp /home/user/bsw-arch/configs/neovim/init.lua ~/.config/nvim/

# Or symlink it
ln -s /home/user/bsw-arch/configs/neovim/init.lua ~/.config/nvim/init.lua
```

### 3. Install Plugins

Open Neovim and plugins will install automatically:

```bash
nvim
```

Wait for plugins to install, then restart Neovim.

### 4. Install Language Servers

Inside Neovim:

```vim
:MasonInstall pyright lua-language-server bash-language-server yaml-language-server
```

## Environment Variables

Ensure these are set (added by platform setup script):

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="bsw-arch-neo4j-2025"
export CHROMA_PATH="/opt/chroma-data"
export OPENSPEC_DIR="/opt/openspec"
export MCP_SERVER_PATH="/opt/opencode/mcp-server/enhanced_mcp_server.py"
```

## Keybindings

### Leader Key

- Leader: `<Space>`
- Local Leader: `,`

### General

| Key | Action |
|-----|--------|
| `<Space>pv` | File explorer |
| `<Space>w` | Save file |
| `<Space>q` | Quit |
| `<Space>e` | Toggle file tree |

### Telescope (Fuzzy Finder)

| Key | Action |
|-----|--------|
| `<Space>ff` | Find files |
| `<Space>fg` | Live grep (search in files) |
| `<Space>fb` | Buffers |
| `<Space>fh` | Help tags |

### LSP (Code Intelligence)

| Key | Action |
|-----|--------|
| `gd` | Go to definition |
| `K` | Hover documentation |
| `<Space>rn` | Rename symbol |
| `<Space>ca` | Code action |
| `gr` | Find references |

### Git

| Key | Action |
|-----|--------|
| `<Space>gs` | Git status |
| `<Space>gc` | Git commit |
| `<Space>gp` | Git push |

### BSW-Arch Platform Integration

#### MCP Server

| Key | Action |
|-----|--------|
| `<Space>ms` | Start MCP server |
| `<Space>mq` | Stop MCP server |

#### Knowledge Graph

| Key | Action |
|-----|--------|
| `<Space>kg` | Query knowledge graph |

Prompts for query, then opens results in split window.

#### Specification Operations

| Key | Action |
|-----|--------|
| `<Space>sn` | Create new spec |
| `<Space>sa` | Apply current spec |
| `<Space>sv` | Validate spec |
| `<Space>st` | Insert spec template |

#### Impact Analysis

| Key | Action |
|-----|--------|
| `<Space>ia` | Analyze change impact |

Shows which specs, tests, and code will be affected by current file changes.

## Custom Commands

### MCP Server

```vim
" Start MCP server
:MCPStart

" Stop MCP server
:MCPStop
```

### Knowledge Graph

```vim
" Query knowledge graph
:KGQuery show me IV bot architecture

" Results open in split window
```

### Specifications

```vim
" Create new spec
:SpecNew my-feature

" Validate spec implementation
:SpecValidate SPEC-MY-FEATURE-001

" Apply current spec
:SpecApply

" Analyze impact of changes
:ImpactAnalysis
```

## Workflows

### 1. Spec-First Development

```vim
" 1. Create specification
<Space>sn
" Enter: my-new-feature

" 2. Edit spec in YAML
" File opens automatically

" 3. Apply spec when ready
<Space>sa

" 4. Implement code
" ... write your code ...

" 5. Validate implementation
<Space>sv
" Enter spec ID
```

### 2. Knowledge Graph Exploration

```vim
" Query for IV bot info
<Space>kg
" Enter: IV bot architecture

" Results show:
" - Related code
" - Specifications
" - Relationships
```

### 3. Impact Analysis Workflow

```vim
" Open file to change
:e bot-utils/my_bot.py

" Check impact before changing
<Space>ia

" Review:
" - Affected specs
" - Affected tests
" - Called by functions
```

### 4. Code Navigation

```vim
" Find files by name
<Space>ff

" Search content across files
<Space>fg

" Go to definition
gd

" Find all references
gr
```

## Example Session

```vim
" Start Neovim
nvim

" Start MCP server
<Space>ms

" Create new spec
<Space>sn
" Enter: user-authentication

" Edit spec (opens in editor)
" ... define requirements ...

" Apply spec
<Space>sa

" Create implementation file
:e bot-utils/auth_bot.py

" Write code
" ... implement according to spec ...

" Check impact
<Space>ia

" Validate spec coverage
<Space>sv
" Enter: SPEC-USER-AUTHENTICATION-001

" Query knowledge graph for examples
<Space>kg
" Enter: authentication examples

" Commit changes
<Space>gs
" ... git workflow ...
```

## Plugin Information

### Installed Plugins

- **lazy.nvim**: Plugin manager
- **telescope.nvim**: Fuzzy finder
- **nvim-treesitter**: Syntax highlighting
- **nvim-lspconfig**: LSP client
- **mason.nvim**: LSP installer
- **nvim-cmp**: Auto-completion
- **vim-fugitive**: Git integration
- **gitsigns.nvim**: Git decorations
- **nvim-tree**: File explorer
- **lualine.nvim**: Status line
- **tokyonight.nvim**: Color scheme
- **Comment.nvim**: Easy commenting
- **nvim-autopairs**: Auto-close pairs

### Updating Plugins

```vim
" Update all plugins
:Lazy update

" Check plugin status
:Lazy
```

## Troubleshooting

### MCP Server Won't Start

Check that the path is correct:

```vim
:echo $MCP_SERVER_PATH
```

Should show: `/opt/opencode/mcp-server/enhanced_mcp_server.py`

Test manually:

```bash
python3 /opt/opencode/mcp-server/enhanced_mcp_server.py
```

### Knowledge Graph Queries Fail

Verify Neo4j connection:

```bash
# Check Neo4j is running
systemctl status neo4j

# Test connection
python3 -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'bsw-arch-neo4j-2025'))
driver.verify_connectivity()
print('OK')
"
```

### LSP Not Working

Install language servers:

```vim
:Mason
```

Then install required servers:
- Python: `pyright`
- Lua: `lua-language-server`
- YAML: `yaml-language-server`
- Bash: `bash-language-server`

### Spec Commands Not Found

Ensure helper scripts are installed:

```bash
which spec
which kg-query

# Should show /usr/local/bin/spec and /usr/local/bin/kg-query
```

If missing, run platform setup:

```bash
sudo /home/user/bsw-arch/bot-utils/complete-platform-setup.sh
```

## Advanced Configuration

### Custom Keybindings

Add to `~/.config/nvim/init.lua`:

```lua
-- Custom keybinding for your workflow
vim.keymap.set('n', '<leader>cb', function()
  -- Your custom function
  print("Custom binding executed")
end, { desc = "Custom binding" })
```

### Auto-start MCP Server

Uncomment in `init.lua`:

```lua
vim.api.nvim_create_autocmd("VimEnter", {
  callback = function()
    mcp_server.start()
  end
})
```

### Custom Spec Templates

Add template function:

```lua
vim.keymap.set('n', '<leader>siv', function()
  -- Insert IV bot spec template
  local lines = {
    "---",
    "version: 1.0.0",
    "spec:",
    "  id: SPEC-IV-BOT-001",
    "  title: IV Bot Implementation",
    "  domain: IV",
    -- ... more lines ...
  }
  vim.cmd('vnew')
  vim.api.nvim_buf_set_lines(0, 0, -1, false, lines)
  vim.bo.filetype = 'yaml'
end, { desc = "IV bot spec template" })
```

## Integration with Other Tools

### tmux Integration

```bash
# Start coding session with tmux
tmux new -s coding

# Window 1: Neovim
nvim

# Window 2: Services monitoring
tmux new-window
watch -n 1 'systemctl status neo4j chromadb ollama'

# Window 3: Logs
tmux new-window
tail -f /opt/neo4j/logs/neo4j.log
```

### Git Workflow

```vim
" Stage file
<Space>gs
" Press 's' on file to stage

" Commit
<Space>gc
" Write message, :wq to commit

" Push
<Space>gp
```

## Tips & Best Practices

1. **Use Telescope for Everything**
   - `<Space>ff` to find files by name
   - `<Space>fg` to search content

2. **Leverage LSP**
   - `gd` to explore code structure
   - `K` to read documentation
   - `<Space>ca` for quick fixes

3. **Spec-Driven Development**
   - Always create spec before coding
   - Use `<Space>ia` before major changes
   - Validate with `<Space>sv` regularly

4. **Knowledge Graph Queries**
   - Query for examples: `<Space>kg` → "authentication examples"
   - Find implementations: `<Space>kg` → "SPEC-XXX implementations"
   - Explore architecture: `<Space>kg` → "IV bot architecture"

5. **Efficient Navigation**
   - Use `gd` to jump to definitions
   - Use `Ctrl-o` to jump back
   - Use `<Space>fb` to switch buffers

## Support

For issues or questions:
- Platform docs: `/home/user/bsw-arch/docs/`
- Neovim help: `:help` in Neovim
- BSW-Arch repository: https://codeberg.org/bsw-arch

## License

Part of BSW-Arch AI Development Platform
