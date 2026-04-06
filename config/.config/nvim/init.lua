vim.g.mapleader = " "
vim.g.maplocalleader = " "

vim.opt.clipboard = "unnamedplus"
vim.opt.confirm = true
vim.opt.completeopt = { "menuone", "noselect" }
vim.opt.cursorline = true
vim.opt.hlsearch = true
vim.opt.inccommand = "split"
vim.opt.incsearch = true
vim.opt.ignorecase = true
vim.opt.mouse = "a"
vim.opt.number = true
vim.opt.relativenumber = false
vim.opt.scrolloff = 4
vim.opt.signcolumn = "yes"
vim.opt.sidescrolloff = 8
vim.opt.splitbelow = true
vim.opt.splitright = true
vim.opt.smartcase = true
vim.opt.termguicolors = true
vim.opt.timeoutlen = 400
vim.opt.undofile = true
vim.opt.updatetime = 250
vim.opt.wrap = false

if vim.fn.executable("rg") == 1 then
  vim.opt.grepformat = "%f:%l:%c:%m"
  vim.opt.grepprg = "rg --vimgrep --smart-case"
end

vim.keymap.set("n", "<leader>w", "<cmd>write<cr>", { silent = true })
vim.keymap.set("n", "<leader>q", "<cmd>quit<cr>", { silent = true })
vim.keymap.set("n", "<leader>h", "<cmd>nohlsearch<cr>", { silent = true })
vim.keymap.set("n", "<C-h>", "<C-w>h", { silent = true })
vim.keymap.set("n", "<C-j>", "<C-w>j", { silent = true })
vim.keymap.set("n", "<C-k>", "<C-w>k", { silent = true })
vim.keymap.set("n", "<C-l>", "<C-w>l", { silent = true })

vim.api.nvim_create_autocmd("TextYankPost", {
  callback = function()
    vim.highlight.on_yank({ timeout = 120 })
  end,
})

-- Restore the last cursor position when reopening a file.
vim.api.nvim_create_autocmd("BufReadPost", {
  callback = function(args)
    local mark = vim.api.nvim_buf_get_mark(args.buf, '"')
    local line_count = vim.api.nvim_buf_line_count(args.buf)
    if mark[1] > 0 and mark[1] <= line_count then
      pcall(vim.api.nvim_win_set_cursor, 0, mark)
    end
  end,
})

-- Make read-only viewer buffers quit like a pager.
vim.api.nvim_create_autocmd("BufEnter", {
  callback = function(args)
    if vim.bo[args.buf].modifiable then
      return
    end

    vim.keymap.set("n", "q", "<cmd>quit<cr>", { buffer = args.buf, silent = true })
  end,
})