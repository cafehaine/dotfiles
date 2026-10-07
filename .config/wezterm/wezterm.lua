local wezterm = require 'wezterm'
local config = {}

function get_appearance()
  if wezterm.gui then
    return wezterm.gui.get_appearance()
  end
  return 'Light'
end

config.hide_tab_bar_if_only_one_tab = true
config.enable_scroll_bar = true

if get_appearance():find('Dark') then
  config.color_scheme = 'Catppuccin'
  config.window_frame = {
    -- Adwaita colors
    inactive_titlebar_bg = '#2c2c2c',
    active_titlebar_bg = '#303030',
    inactive_titlebar_fg = '#919191',
    active_titlebar_fg = '#f7f7f7',
    inactive_titlebar_border_bottom = '#1c1c1e',
    active_titlebar_border_bottom = '#323232',
    button_fg = '#f7f7f7',
    button_bg = '#444444',
    button_hover_fg = '#f7f7f7',
    button_hover_bg = '#4e4e4e',
  }
  config.colors = {
    -- Adwaita colors
    tab_bar = {
      background = '#2c2c2c',
      active_tab = {
        bg_color = '#414141',
        fg_color = '#f7f7f7',
      },
      inactive_tab = {
        bg_color = '#2c2c2c',
        fg_color = '#f7f7f7',
      },
      inactive_tab_hover = {
        bg_color = '#3a3a3a',
        fg_color = '#f7f7f7',
      },
      new_tab = {
        bg_color = '#2c2c2c',
        fg_color = '#f7f7f7',
      },
      new_tab_hover = {
        bg_color = '#3a3a3a',
        fg_color = '#f7f7f7',
      },
    },
  }
else
  config.color_scheme = 'Catppuccin Latte'
  config.window_frame = {
    -- Adwaita colors
    inactive_titlebar_bg = '#fafafa',
    active_titlebar_bg = '#ffffff',
    inactive_titlebar_fg = '#9b9b9b',
    active_titlebar_fg = '#3d3d3d',
    inactive_titlebar_border_bottom = '#dcdcdd',
    active_titlebar_border_bottom = '#e0e0e0',
    button_fg = '#3d3d3d',
    button_bg = '#ececec',
    button_hover_fg = '#3d3d3d',
    button_hover_bg = '#e2e2e2',
  }
  config.colors = {
    -- Adwaita colors
    tab_bar = {
      background = '#fafafa',
      active_tab = {
        bg_color = '#e7e7e7',
        fg_color = '#3d3d3d',
      },
      inactive_tab = {
        bg_color = '#fafafa',
        fg_color = '#3d3d3d',
      },
      inactive_tab_hover = {
        bg_color = '#ececec',
        fg_color = '#3d3d3d',
      },
      new_tab = {
        bg_color = '#fafafa',
        fg_color = '#3d3d3d',
      },
      new_tab_hover = {
        bg_color = '#ececec',
        fg_color = '#3d3d3d',
      },
    },
  }
end

config.integrated_title_button_style = "Gnome"
config.window_frame.font = wezterm.font "Ubuntu Sans"

config.font = wezterm.font('Fira Code')

return config
