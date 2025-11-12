-- BSW-Arch AI Development Platform - Neovim Configuration
-- Integrates with OpenCode, OpenSpec, and Knowledge Graph
-- Spec-driven development with AI assistance

-- Leader key
vim.g.mapleader = " "
vim.g.maplocalleader = ","

-- Basic settings
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.expandtab = true
vim.opt.shiftwidth = 4
vim.opt.tabstop = 4
vim.opt.smartindent = true
vim.opt.wrap = false
vim.opt.swapfile = false
vim.opt.backup = false
vim.opt.undodir = os.getenv("HOME") .. "/.vim/undodir"
vim.opt.undofile = true
vim.opt.hlsearch = false
vim.opt.incsearch = true
vim.opt.termguicolors = true
vim.opt.scrolloff = 8
vim.opt.signcolumn = "yes"
vim.opt.updatetime = 50
vim.opt.colorcolumn = "100"

-- Plugin management with lazy.nvim
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- Plugins
require("lazy").setup({
  -- Telescope (fuzzy finder)
  {
    'nvim-telescope/telescope.nvim',
    dependencies = { 'nvim-lua/plenary.nvim' }
  },

  -- Treesitter (syntax highlighting)
  {
    'nvim-treesitter/nvim-treesitter',
    build = ':TSUpdate'
  },

  -- LSP
  {
    'neovim/nvim-lspconfig',
    dependencies = {
      'williamboman/mason.nvim',
      'williamboman/mason-lspconfig.nvim',
    }
  },

  -- Completion
  {
    'hrsh7th/nvim-cmp',
    dependencies = {
      'hrsh7th/cmp-nvim-lsp',
      'hrsh7th/cmp-buffer',
      'hrsh7th/cmp-path',
      'L3MON4D3/LuaSnip',
    }
  },

  -- Git integration
  'tpope/vim-fugitive',
  'lewis6991/gitsigns.nvim',

  -- File explorer
  'nvim-tree/nvim-tree.lua',
  'nvim-tree/nvim-web-devicons',

  -- Status line
  'nvim-lualine/lualine.nvim',

  -- Color scheme
  'folke/tokyonight.nvim',

  -- Comment
  'numToStr/Comment.nvim',

  -- Pairs
  'windwp/nvim-autopairs',
})

-- Color scheme
vim.cmd[[colorscheme tokyonight-night]]

-- LSP Configuration
require("mason").setup()
require("mason-lspconfig").setup({
  ensure_installed = { "pyright", "lua_ls", "bashls", "yamlls" }
})

local lspconfig = require('lspconfig')

-- Python LSP
lspconfig.pyright.setup{}

-- Lua LSP
lspconfig.lua_ls.setup{
  settings = {
    Lua = {
      diagnostics = {
        globals = {'vim'}
      }
    }
  }
}

-- YAML LSP
lspconfig.yamlls.setup{}

-- Completion setup
local cmp = require('cmp')
cmp.setup({
  snippet = {
    expand = function(args)
      require('luasnip').lsp_expand(args.body)
    end,
  },
  mapping = cmp.mapping.preset.insert({
    ['<C-b>'] = cmp.mapping.scroll_docs(-4),
    ['<C-f>'] = cmp.mapping.scroll_docs(4),
    ['<C-Space>'] = cmp.mapping.complete(),
    ['<C-e>'] = cmp.mapping.abort(),
    ['<CR>'] = cmp.mapping.confirm({ select = true }),
  }),
  sources = cmp.config.sources({
    { name = 'nvim_lsp' },
    { name = 'luasnip' },
    { name = 'buffer' },
    { name = 'path' },
  })
})

-- Treesitter
require('nvim-treesitter.configs').setup({
  ensure_installed = { "python", "lua", "bash", "yaml", "markdown" },
  highlight = { enable = true },
  indent = { enable = true },
})

-- Telescope
local telescope = require('telescope')
telescope.setup{}

-- File explorer
require("nvim-tree").setup()

-- Status line
require('lualine').setup {
  options = {
    theme = 'tokyonight'
  }
}

-- Git signs
require('gitsigns').setup()

-- Comment
require('Comment').setup()

-- Autopairs
require('nvim-autopairs').setup{}

-- ============================================================================
-- BSW-Arch AI Development Platform Integration
-- ============================================================================

-- Environment variables
vim.env.NEO4J_URI = vim.env.NEO4J_URI or "bolt://localhost:7687"
vim.env.NEO4J_USER = vim.env.NEO4J_USER or "neo4j"
vim.env.NEO4J_PASSWORD = vim.env.NEO4J_PASSWORD or "bsw-arch-neo4j-2025"
vim.env.CHROMA_PATH = vim.env.CHROMA_PATH or "/opt/chroma-data"
vim.env.OPENSPEC_DIR = vim.env.OPENSPEC_DIR or "/opt/openspec"
vim.env.MCP_SERVER_PATH = vim.env.MCP_SERVER_PATH or "/opt/opencode/mcp-server/enhanced_mcp_server.py"

-- MCP Server integration
local mcp_server = {
  running = false,
  job_id = nil
}

function mcp_server.start()
  if mcp_server.running then
    print("MCP server already running")
    return
  end

  print("Starting MCP server...")
  mcp_server.job_id = vim.fn.jobstart({
    "python3",
    vim.env.MCP_SERVER_PATH
  }, {
    on_stdout = function(_, data)
      if data then
        print("MCP: " .. table.concat(data, "\n"))
      end
    end,
    on_stderr = function(_, data)
      if data then
        print("MCP Error: " .. table.concat(data, "\n"))
      end
    end,
    on_exit = function()
      mcp_server.running = false
      print("MCP server stopped")
    end
  })

  if mcp_server.job_id > 0 then
    mcp_server.running = true
    print("MCP server started (job " .. mcp_server.job_id .. ")")
  else
    print("Failed to start MCP server")
  end
end

function mcp_server.stop()
  if not mcp_server.running then
    print("MCP server not running")
    return
  end

  vim.fn.jobstop(mcp_server.job_id)
  mcp_server.running = false
  mcp_server.job_id = nil
  print("MCP server stopped")
end

-- Knowledge Graph query function
function query_knowledge_graph(query)
  local cmd = string.format(
    'python3 -c "' ..
    'import asyncio; ' ..
    'import json; ' ..
    'import sys; ' ..
    'sys.path.append(\\"/opt/opencode/mcp-server\\"); ' ..
    'from enhanced_mcp_server import EnhancedMCPServer; ' ..
    'async def q(): ' ..
    '    s = EnhancedMCPServer(); ' ..
    '    await s._initialize(); ' ..
    '    r = await s._query_spec_aware_graph(\\"%s\\"); ' ..
    '    print(json.dumps(r, indent=2)); ' ..
    '    await s.cleanup(); ' ..
    'asyncio.run(q())' ..
    '"',
    query:gsub('"', '\\"')
  )

  local result = vim.fn.system(cmd)
  return result
end

-- Spec validation function
function validate_spec(spec_id)
  local cmd = string.format(
    'python3 -c "' ..
    'import asyncio; ' ..
    'import json; ' ..
    'import sys; ' ..
    'sys.path.append(\\"/opt/opencode/mcp-server\\"); ' ..
    'from enhanced_mcp_server import EnhancedMCPServer; ' ..
    'async def v(): ' ..
    '    s = EnhancedMCPServer(); ' ..
    '    await s._initialize(); ' ..
    '    r = await s._validate_spec_implementation(\\"%s\\"); ' ..
    '    print(json.dumps(r, indent=2)); ' ..
    '    await s.cleanup(); ' ..
    'asyncio.run(v())' ..
    '"',
    spec_id
  )

  local result = vim.fn.system(cmd)
  return result
end

-- Impact analysis function
function analyze_impact()
  local file_path = vim.fn.expand('%:.')
  local cmd = string.format(
    'python3 -c "' ..
    'import asyncio; ' ..
    'import json; ' ..
    'import sys; ' ..
    'sys.path.append(\\"/opt/opencode/mcp-server\\"); ' ..
    'from enhanced_mcp_server import EnhancedMCPServer; ' ..
    'async def a(): ' ..
    '    s = EnhancedMCPServer(); ' ..
    '    await s._initialize(); ' ..
    '    r = await s._analyze_change_impact(\\"%s\\"); ' ..
    '    print(json.dumps(r, indent=2)); ' ..
    '    await s.cleanup(); ' ..
    'asyncio.run(a())' ..
    '"',
    file_path
  )

  local result = vim.fn.system(cmd)
  return result
end

-- ============================================================================
-- Custom Commands
-- ============================================================================

-- Start MCP server
vim.api.nvim_create_user_command('MCPStart', function()
  mcp_server.start()
end, {})

-- Stop MCP server
vim.api.nvim_create_user_command('MCPStop', function()
  mcp_server.stop()
end, {})

-- Query knowledge graph
vim.api.nvim_create_user_command('KGQuery', function(opts)
  local query = opts.args
  local result = query_knowledge_graph(query)

  -- Open result in split
  vim.cmd('vnew')
  vim.api.nvim_buf_set_lines(0, 0, -1, false, vim.split(result, '\n'))
  vim.bo.filetype = 'json'
  vim.bo.buftype = 'nofile'
end, { nargs = 1 })

-- Validate spec
vim.api.nvim_create_user_command('SpecValidate', function(opts)
  local spec_id = opts.args
  local result = validate_spec(spec_id)

  -- Open result in split
  vim.cmd('vnew')
  vim.api.nvim_buf_set_lines(0, 0, -1, false, vim.split(result, '\n'))
  vim.bo.filetype = 'json'
  vim.bo.buftype = 'nofile'
end, { nargs = 1 })

-- Analyze impact
vim.api.nvim_create_user_command('ImpactAnalysis', function()
  local result = analyze_impact()

  -- Open result in split
  vim.cmd('vnew')
  vim.api.nvim_buf_set_lines(0, 0, -1, false, vim.split(result, '\n'))
  vim.bo.filetype = 'json'
  vim.bo.buftype = 'nofile'
end, {})

-- Create new spec
vim.api.nvim_create_user_command('SpecNew', function(opts)
  local spec_name = opts.args
  vim.fn.system('spec new ' .. spec_name)
  vim.cmd('edit ' .. vim.env.OPENSPEC_DIR .. '/proposals/' .. spec_name .. '.yaml')
end, { nargs = 1 })

-- Apply spec
vim.api.nvim_create_user_command('SpecApply', function()
  local file = vim.fn.expand('%:p')
  vim.fn.system('spec apply ' .. file)
  print("Spec applied: " .. file)
end, {})

-- ============================================================================
-- Keybindings
-- ============================================================================

-- General
vim.keymap.set('n', '<leader>pv', vim.cmd.Ex, { desc = "File explorer" })
vim.keymap.set('n', '<leader>w', ':w<CR>', { desc = "Save file" })
vim.keymap.set('n', '<leader>q', ':q<CR>', { desc = "Quit" })

-- Telescope
vim.keymap.set('n', '<leader>ff', '<cmd>Telescope find_files<cr>', { desc = "Find files" })
vim.keymap.set('n', '<leader>fg', '<cmd>Telescope live_grep<cr>', { desc = "Live grep" })
vim.keymap.set('n', '<leader>fb', '<cmd>Telescope buffers<cr>', { desc = "Buffers" })
vim.keymap.set('n', '<leader>fh', '<cmd>Telescope help_tags<cr>', { desc = "Help tags" })

-- LSP
vim.keymap.set('n', 'gd', vim.lsp.buf.definition, { desc = "Go to definition" })
vim.keymap.set('n', 'K', vim.lsp.buf.hover, { desc = "Hover documentation" })
vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, { desc = "Rename symbol" })
vim.keymap.set('n', '<leader>ca', vim.lsp.buf.code_action, { desc = "Code action" })
vim.keymap.set('n', 'gr', vim.lsp.buf.references, { desc = "References" })

-- Git
vim.keymap.set('n', '<leader>gs', vim.cmd.Git, { desc = "Git status" })
vim.keymap.set('n', '<leader>gc', ':Git commit<CR>', { desc = "Git commit" })
vim.keymap.set('n', '<leader>gp', ':Git push<CR>', { desc = "Git push" })

-- File tree
vim.keymap.set('n', '<leader>e', ':NvimTreeToggle<CR>', { desc = "Toggle file tree" })

-- ============================================================================
-- BSW-Arch Platform Keybindings
-- ============================================================================

-- MCP Server
vim.keymap.set('n', '<leader>ms', ':MCPStart<CR>', { desc = "Start MCP server" })
vim.keymap.set('n', '<leader>mq', ':MCPStop<CR>', { desc = "Stop MCP server" })

-- Knowledge Graph
vim.keymap.set('n', '<leader>kg', function()
  local query = vim.fn.input('Knowledge Graph Query: ')
  if query ~= '' then
    vim.cmd('KGQuery ' .. query)
  end
end, { desc = "Query knowledge graph" })

-- Spec Operations
vim.keymap.set('n', '<leader>sn', function()
  local name = vim.fn.input('Spec Name: ')
  if name ~= '' then
    vim.cmd('SpecNew ' .. name)
  end
end, { desc = "Create new spec" })

vim.keymap.set('n', '<leader>sa', ':SpecApply<CR>', { desc = "Apply current spec" })

vim.keymap.set('n', '<leader>sv', function()
  local spec_id = vim.fn.input('Spec ID: ')
  if spec_id ~= '' then
    vim.cmd('SpecValidate ' .. spec_id)
  end
end, { desc = "Validate spec" })

-- Impact Analysis
vim.keymap.set('n', '<leader>ia', ':ImpactAnalysis<CR>', { desc = "Analyze change impact" })

-- Quick spec templates
vim.keymap.set('n', '<leader>st', function()
  local lines = {
    "---",
    "version: 1.0.0",
    "spec:",
    "  id: SPEC-XXX-001",
    "  title: TODO",
    "  status: proposal",
    "  created: " .. os.date("%Y-%m-%dT%H:%M:%S"),
    "",
    "description: |",
    "  TODO: Describe the specification",
    "",
    "requirements:",
    "  - id: REQ-001",
    "    description: \"TODO\"",
    "    priority: high",
    "",
    "implementation:",
    "  file: \"TODO\"",
    "  function: \"TODO\"",
  }

  vim.cmd('vnew')
  vim.api.nvim_buf_set_lines(0, 0, -1, false, lines)
  vim.bo.filetype = 'yaml'
end, { desc = "Insert spec template" })

-- ============================================================================
-- Auto-commands
-- ============================================================================

-- Auto-start MCP server on startup (optional)
-- vim.api.nvim_create_autocmd("VimEnter", {
--   callback = function()
--     mcp_server.start()
--   end
-- })

-- Auto-stop MCP server on exit
vim.api.nvim_create_autocmd("VimLeavePre", {
  callback = function()
    if mcp_server.running then
      mcp_server.stop()
    end
  end
})

-- Format on save (Python)
vim.api.nvim_create_autocmd("BufWritePre", {
  pattern = "*.py",
  callback = function()
    vim.lsp.buf.format()
  end
})

print("BSW-Arch AI Development Platform - Neovim initialized!")
print("Leader key: <Space>")
print("Commands: :MCPStart, :MCPStop, :KGQuery, :SpecNew, :SpecValidate, :ImpactAnalysis")
