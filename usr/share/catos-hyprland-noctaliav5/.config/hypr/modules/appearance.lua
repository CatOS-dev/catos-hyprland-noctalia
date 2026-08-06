hl.config({
    general = {
        gaps_in  = 5,
        gaps_out = 8,

        border_size = 1,

        resize_on_border = false,
        allow_tearing = false,
        layout = "scrolling",
    },

    decoration = {
        rounding       = 8,
        rounding_power = 2,

        active_opacity   = 1.0,
        inactive_opacity = 1.0,

        shadow = {
            enabled = true,
            range = 20,
            offset = {0, 2},
            render_power = 10,
            color = "rgba(00000020)"
        },

        blur = {
            enabled   = true,
            size      = 3,
            passes    = 2,
            vibrancy  = 0.1696,
            xray = false,
        },
    },

    animations = {
        enabled = true,
    },
})
